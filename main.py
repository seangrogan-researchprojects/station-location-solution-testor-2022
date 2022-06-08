import copy
import random
from collections import namedtuple

import pandas as pd
import scipy.spatial.distance
from matplotlib import pyplot as plt
from shapely.geometry import Polygon

import file_readers
from TornadoCaseGetter import TornadoCaseGetter, RouteClass
from pickles.pickle_io import pickle_input, pickle_dumper
from utilities import parfile_reader, euclidean, datetime_for_filename


def main(parfile_name, pickles=None, trials=100, result_folder="results"):
    pars = parfile_reader(parfile_name)
    if pickles:
        pickle_pars = parfile_reader(pickles)

    fire_stations = file_readers.read_fire_stations_file(pars['fire_stations'], pars['crs'])
    fire_stations_subset = {k: tuple(v) for k, v in
                            file_readers.read_json_generic(pars['fire_stations_subset']).items()}
    waypoints = file_readers.read_waypoint_file(pars['waypoints_file'])
    tornado_cases = None
    if pickles:
        tornado_cases = pickle_input(pickle_pars['300_meter_tornado_cases_pickle'])
    if tornado_cases is None or pickles is None:
        tornado_db = file_readers.read_tornadoes(pars['tornado_db'], pars['crs'], keep_unknown_ends=False)
        sbws = file_readers.read_sbw_file(pars['sbws'], pars['crs'])
        tornado_cases = TornadoCaseGetter(tornado_db, sbws, waypoints)
        if pickles:
            pickle_dumper(pickle_pars['300_meter_tornado_cases_pickle'],
                          tornado_cases,
                          "300_meter_tornado_cases_pickle", pickles)
    ResultInfo = namedtuple("ResultInfo", ["n_stations", "t_bar", "routes_data", "dists"])
    results = dict()
    result_counter = []
    for i in range(trials):
        print(f"\n\nTrial Number {i} of {trials}\nParfile {result_folder}\n{pars['result_file']}\n\n")
        best_solution, best_val, best_routes, best_dists, all_waypoints = \
            test_solution(fire_stations_subset, tornado_cases, waypoints, pars)
        results[i] = ResultInfo(best_solution, best_val, best_routes, best_dists)._asdict()
        results[i]['n_waypoints'] = len(all_waypoints)
        result_counter.append(bool(best_solution))

    result_file = f"./{result_folder}/{pars['result_file']}/{pars['result_file']}_{str(int(100 * sum(result_counter) / len(result_counter)))}_{datetime_for_filename()}.json"
    results['sucesses'] = sum(result_counter)
    results['trials'] = len(result_counter)
    results['pcts'] = sum(result_counter) / len(result_counter)
    file_readers.write_json_generic(result_file, results)
    print()
    print(f"{pars['fire_stations_subset']}")
    print(f"{sum(result_counter) / len(result_counter)}")
    return sum(result_counter), len(result_counter), sum(result_counter) / len(result_counter)


def get_random_position(waypoints, tornado_cases, min_factor=0.85):
    date = random.choice(tornado_cases.dates)
    _, event = tornado_cases.get_specific_event(date)
    old_wpts = event.waypoints
    n_old_wpts = len(old_wpts)
    new_waypoints_to_route = {}
    wpts_to_start = list(copy.deepcopy(waypoints))
    random.shuffle(wpts_to_start)
    while n_old_wpts * min_factor >= len(new_waypoints_to_route):
        if len(wpts_to_start) <= 0:
            date = random.choice(tornado_cases.dates)
            _, event = tornado_cases.get_specific_event(date)
            old_wpts = event.waypoints
            n_old_wpts = len(old_wpts)
            new_waypoints_to_route = {}
            wpts_to_start = list(copy.deepcopy(waypoints))
            random.shuffle(wpts_to_start)
        random_point = wpts_to_start.pop()
        sbws = event.sbw_geometries[:]
        sbws_pts = [itm for sbw in sbws for itm in list(zip(*sbw.boundary.xy))]
        x, y = zip(*sbws_pts)
        sbw_ref = sorted(sbws_pts, key=lambda tt: euclidean(tt, (min(x), min(y))))[0]

        del_x, del_y = random_point[0] - sbw_ref[0], random_point[1] - sbw_ref[1]

        adjusted_sbws = [
            Polygon([(coord[0] + del_x, coord[1] + del_y) for coord in list(zip(*sbw.boundary.xy))])
            for sbw in sbws
        ]

        new_waypoints_to_route = set()
        __temp_waypoints = pd.DataFrame(data=waypoints, index=waypoints, columns=['x', 'y'])
        for sbw in adjusted_sbws:
            new_waypoints_to_route.update(set(TornadoCaseGetter.filter_points(__temp_waypoints, sbw)))

        routes = RouteClass(new_waypoints_to_route)
    return new_waypoints_to_route, routes


def find_starting_cluster_count(waypoints, target, n_stations, est_wpts_p_cluster=450):
    dist_matrix = scipy.spatial.distance.squareform(scipy.spatial.distance.pdist(list(waypoints)))
    max_val = dist_matrix.max()
    start = max(int(max_val / target), int(len(waypoints) / est_wpts_p_cluster))
    start = min(start, n_stations)
    start = max(1, start)
    return start


def test_solution(fire_stations_subset, tornado_cases, waypoints, pars,
                  fail_stations=False,
                  use_random_position=True):
    if fail_stations:
        fire_stations_subset = {k: v for k, v in fire_stations_subset.items()
                                if random.random() >= pars["depot_failure_rate"]}
    if use_random_position:
        new_waypoints_to_route, routes_class = get_random_position(waypoints, tornado_cases)
        while len(new_waypoints_to_route) < 350:  # or len(new_waypoints_to_route) > 4000:
            new_waypoints_to_route, routes_class = get_random_position(waypoints, tornado_cases)
        print(f"n_waypoints_{len(new_waypoints_to_route)}")
        n_stations_to_check = list(range(1, min(len(fire_stations_subset) + 1, len(waypoints) - 1)))
        best_solution, best_val, best_routes, best_dists = None, float('inf'), None, None
        k = 0
        start = find_starting_cluster_count(waypoints=new_waypoints_to_route,
                                            target=pars["maximum_service_time_hours"] * pars[
                                                "drone_speed_mps"] * 60 * 60,
                                            n_stations=len(fire_stations_subset))
        assert start >= 1
        assert start <= len(n_stations_to_check)
        if start != 1:
            while True:
                print(f"Starting at {start} stations")
                routes, dists, t_bars = routes_class.get_route(start)
                new_routes, new_dists = get_closest_stations(fire_stations_subset, routes, dists)
                if max(new_dists.values()) < pars["maximum_service_time_hours"] * pars["drone_speed_mps"] * 60 * 60:
                    start -= 1
                if max(new_dists.values()) >= pars["maximum_service_time_hours"] * pars["drone_speed_mps"] * 60 * 60:
                    break
        start -= 1
        start = max(start, 1)
        for n_station in n_stations_to_check[start - 1:]:
            routes, dists, t_bars = routes_class.get_route(n_station)
            new_routes, new_dists = get_closest_stations(fire_stations_subset, routes, dists)
            if max(new_dists.values()) > pars["maximum_service_time_hours"] * pars["drone_speed_mps"] * 60 * 60:
                continue
            if max(new_dists.values()) <= pars["maximum_service_time_hours"] * pars["drone_speed_mps"] * 60 * 60:
                best_solution, best_val, best_routes, best_dists = \
                    n_station, max(new_dists.values()), copy.deepcopy(new_routes), copy.deepcopy(new_dists)
                break
            if max(new_dists.values()) <= best_val:
                best_solution, best_val, best_routes, best_dists = \
                    n_station, max(new_dists.values()), copy.deepcopy(new_routes), copy.deepcopy(new_dists)
            elif max(new_dists.values()) >= best_val:
                k += 1
                if k > 3:
                    break
        return best_solution, best_val, best_routes, best_dists, new_waypoints_to_route
    else:
        date = random.choice(tornado_cases.dates)
        _, event = tornado_cases.get_specific_event(date)
        solved = False
        n_stations_to_check = list(range(1, len(fire_stations_subset) + 1))
        start = min(1 + int(len(event.waypoints) * pars['scanning_r'] * 2 / \
                            (pars["endurance"] * pars["drone_speed_mps"] * 60 * 60)), len(n_stations_to_check) - 1)
        left, right = n_stations_to_check[:start - 1], n_stations_to_check[start - 1:]
        best_solution = None
        while not solved:
            n_station = left[-1]
            routes, dists, t_bars = event.route_data.get_route(n_station)
            get_closest_stations(fire_stations_subset, routes, dists)
            if t_bars > pars["endurance"]:
                _i = int(len(right) / 2)
                left, right = right[:_i], n_stations_to_check[_i:]
                continue
        return True


def get_closest_stations(stations, routes, dists):
    data = []
    for st_id, st_point in stations.items():
        for rt_id, wpts in routes.items():
            data.append((euclidean(st_point, wpts[0]), st_id, rt_id, 'fwd'))
            data.append((euclidean(st_point, wpts[-1]), st_id, rt_id, 'rev'))
    data.sort(key=lambda x: x[0])
    _routes = copy.deepcopy(routes)
    new_routes, new_dists = dict(), dict()

    while len(new_routes) < len(routes):
        d, st_id, rt_id, direction = data.pop(0)
        if st_id in new_routes.keys():
            continue
        if rt_id not in _routes.keys():
            continue
        if direction == 'rev':
            new_routes[st_id] = [stations[st_id]] + list(reversed(routes[rt_id]))
        else:
            new_routes[st_id] = [stations[st_id]] + list(routes[rt_id])
        new_dists[st_id] = dists[rt_id] + d
    return new_routes, new_dists


if __name__ == '__main__':
    main(
        parfile_name="./par_files/par1.json",
        pickles="./pickles/pickles.json"
    )
