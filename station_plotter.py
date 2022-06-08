import csv
from collections import defaultdict
from multiprocessing import Process

import geopandas as gpd
from matplotlib import pyplot as plt

import file_readers
from TheThirdTrials import get_solution_filename
from utilities import automkdir


def station_plotter():
    bath_solution_folder_path = "G:/DisasterLocationTool/outputs"
    states = "D:/gis_database/usa/states/states.shp"
    states = gpd.read_file(states)
    states = states.to_crs("EPSG:26914")
    x, y = states[states.STATE == 'OK'].geometry.iloc[0].exterior.xy
    x, y = list(x), list(y)
    oklahoma = list(zip(x, y))
    roads = "D:/gis_database/usa/oklahoma/roads/highways/ODOT_Highways.shp"
    roads = gpd.read_file(roads)
    roads = roads.to_crs("EPSG:26914")
    roads = roads.geometry.to_list()
    data = defaultdict(dict)
    for feas in range(90, 101):
        data_to_csv = []
        data_to_csv.append(['name', 'easting', 'northing', 'feas', 'fail'])
        for fail in range(0, 11):
            solution_filename = get_solution_filename(bath_solution_folder_path, feas=feas, fail=fail)
            solution = file_readers.read_json_generic(solution_filename)
            data[feas][fail] = solution
            for station_key, station_value in solution.items():
                x, y = station_value
                data_to_csv.append([
                    station_key, x, y, feas, fail
                ])
            p = Process(target=plot_stations, args=(
                f"./plots300/feas_{feas:0>3}_fail_{fail:0>3}.png",
                f"Solution NStation={len(solution)}: FeasTgt={feas}%, DeptFail={fail}%",
                solution,
                oklahoma,
                roads
            )
                        )
            p.start()
            # plot_stations(
            #     filename=f"./plots/feas_{feas:0>3}/feas_{feas:0>3}_fail_{fail:0>3}.png",
            #     title=f"Solution NStation={len(solution)}: FeasTgt={feas}%, DeptFail={fail}%",
            #     stations=solution,
            #     state_bounds=oklahoma,
            #     major_roads=roads
            # )
        with open(f"./solution_data/solution_data_{feas}.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data_to_csv)


def plot_stations(filename, title, stations, state_bounds, major_roads):
    print(title)
    automkdir(filename)
    keys, values = zip(*stations.items())
    values = list(values)
    x, y = zip(*values)
    fig, ax = plt.subplots()
    ax.scatter(x, y, zorder=999, color='red')
    x, y = zip(*state_bounds)
    ax.plot(x, y, zorder=100, color='black')
    for road in major_roads:
        x, y = road.xy
        x, y = list(x), list(y)
        ax.plot(x, y, zorder=500, color='blue', linewidth=0.5)
    ax.set_title(title)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    station_plotter()
