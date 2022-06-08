import copy
from collections import namedtuple
import concurrent.futures
import numpy as np
import scipy.spatial.distance
from tqdm import tqdm

from utilities import euclidean


def route_clusters_serially(clusters):
    cluster_tours, dists = dict(), dict()
    for cluster_number, waypoints in clusters.items():
        waypoints = sorted(sorted(list(waypoints), key=lambda x: x[0]), key=lambda x: x[1])
        distance_matrix = scipy.spatial.distance.squareform(scipy.spatial.distance.pdist(waypoints))
        tour, c_num = construct_path_nearest_insertion_heuristic(distance_matrix, start_min_arc=True,
                                                                 c_num=cluster_number)
        cluster_tours[cluster_number] = [waypoints[idx] for idx in tour]
        dists[cluster_number] = sum(euclidean(p1, p2)
                                    for p1, p2 in
                                    zip(cluster_tours[cluster_number], cluster_tours[cluster_number][1:]))
    return cluster_tours, dists


def route_clusters_with_multiprocessing(clusters):
    cluster_tours, dists = dict(), dict()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results, wpt_clusters = list(), dict()
        for cluster, waypoints in tqdm(clusters.items(), desc='Submitting'):
            waypoints = sorted(sorted(list(waypoints), key=lambda x: x[0]), key=lambda x: x[1])
            wpt_clusters[cluster] = waypoints
            distance_matrix = scipy.spatial.distance.squareform(scipy.spatial.distance.pdist(waypoints))
            results.append(
                executor.submit(construct_path_nearest_insertion_heuristic_mp_wrapper,
                                [distance_matrix, True, cluster]))
        for result in tqdm(concurrent.futures.as_completed(results), desc='Getting Results'):
            tour, c_num = result.result()
            cluster_tours[c_num] = [wpt_clusters[c_num][idx] for idx in tour]
            dists[c_num] = sum(euclidean(p1, p2)
                               for p1, p2 in
                               zip(cluster_tours[c_num], cluster_tours[c_num][1:]))
    return cluster_tours, dists


def construct_path_nearest_insertion_heuristic_mp_wrapper(args):
    return construct_path_nearest_insertion_heuristic(*args)


def nearest_insertion_attempt_two(clusters, mp=True):
    if len(clusters) <= 1:
        mp = False
    if mp:
        cluster_tours, dists = route_clusters_with_multiprocessing(clusters)
    else:
        cluster_tours, dists = route_clusters_serially(clusters)
    return cluster_tours, dists, max(dists.values())


def construct_path_nearest_insertion_heuristic(dist_matrix, start_min_arc=True, c_num=None):
    p_bar = tqdm(total=len(dist_matrix), position=0, leave=False, desc=f"Routing Cluster {c_num}")
    default_dist_matrix = copy.deepcopy(dist_matrix)
    D_ijk = namedtuple("D_ijk", ["i", "j", "k", "val"])
    n_cities = len(default_dist_matrix)
    for i in range(len(dist_matrix)):
        dist_matrix = _set_dist_mat_to(i, i, dist_matrix, val=float('inf'))
    if start_min_arc:
        desired_val = dist_matrix.min()
    else:
        desired_val = dist_matrix.max()
    __is, __js = np.where(desired_val == dist_matrix)
    __i, __j = int(__is[0]), int(__js[0])
    tour = [-999] + [__i, __j] + [-888]
    dist_matrix = _set_dist_mat_to(__i, __j, dist_matrix, val=float('inf'))
    while len(tour) < n_cities + 2:
        waypoint, dist_matrix, _other = _find_next_waypoint_to_insert(dist_matrix, tour)
        change_arc_list = [
            D_ijk(i, j, waypoint, _d_ijk(i, j, waypoint, default_dist_matrix))
            for i, j in zip(tour, tour[1:])
        ]
        change_arc_list.sort(key=lambda __x: __x.val)
        if change_arc_list:
            near_insert = change_arc_list.pop(0)
            while near_insert.k in tour:
                near_insert = change_arc_list.pop(0)
            idx_i = tour.index(near_insert.i)
            tour = tour[:idx_i + 1] + [near_insert.k] + tour[idx_i + 1:]
            for element in tour[1:-1]:
                dist_matrix = _set_dist_mat_to(near_insert.k, element, dist_matrix, val=float('inf'))
        else:
            assert False, "Something Has Gone Wrong Here!"
        p_bar.set_postfix_str(f"{len(tour) - 2}")
        p_bar.update()
    return tour[1:-1], c_num


def _set_dist_mat_to(i, j, dm, val=float('inf')):
    dm[i, j] = val
    dm[j, i] = val
    return dm


def _get_val_from_dist_matrix(_i, _j, _dist_matrix):
    if _i in {-888, -999} or _j in {-888, -999}:
        return 0
    if _i == _j:
        return 0
    return _dist_matrix[_i, _j]


def _d_ijk(_i, _j, _k, _dist_matrix):
    return _get_val_from_dist_matrix(_i, _k, _dist_matrix) + \
           _get_val_from_dist_matrix(_k, _j, _dist_matrix) - \
           _get_val_from_dist_matrix(_i, _j, _dist_matrix)


def _find_next_waypoint_to_insert(_dist_matrix, tour):
    while True:
        min_val = _dist_matrix[tour[1:-1], :].min()
        _is, _js = np.where(min_val == _dist_matrix)
        _i, _j = int(_is[0]), int(_js[0])
        _dist_matrix = _set_dist_mat_to(_i, _j, _dist_matrix, val=float('inf'))
        if _i in tour and not (_j in tour):
            return _j, _dist_matrix, _i
        elif _j in tour and not (_i in tour):
            return _i, _dist_matrix, _j
        elif min_val >= float('inf'):
            assert False
