import copy
from collections import defaultdict
from multiprocessing import Process

from file_readers import read_json_generic
from main import main
from utilities import parfile_reader, parfile_writer, json_writer


def trials1(trials=100):
    pars_to_update = [
        {
            # 0, 100
            "target_feasibility_pct": 1.00,
            "depot_failure_rate": 0.00,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_000pct_tgtFeas_100pct_20220313_100034\solutions"
                                    f"\solution_00101_000000040150_000000000030.json",
            "result_file": "UPDATE_output_Oklahoma_deptFail_000pct_tgtFeas_100pct",
        },
        {
            # 5, 100
            "target_feasibility_pct": 1.00,
            "depot_failure_rate": 0.05,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_005pct_tgtFeas_100pct_20220318_213534"
                                    f"\solutions"
                                    f"\solution_00173_000000007300_000000000007.json",
            "result_file": "UPDATE_output_Oklahoma_deptFail_005pct_tgtFeas_100pct",
        },
        {
            # 10, 100
            "target_feasibility_pct": 1.00,
            "depot_failure_rate": 0.10,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_010pct_tgtFeas_100pct_20220317_091233\solutions"
                                    f"\solution_00194_000000076650_000000000075.json",
            "result_file": "UPDATE_output_Oklahoma_deptFail_010pct_tgtFeas_100pct",
        },
        {
            # 0, 99
            "target_feasibility_pct": 0.99,
            "depot_failure_rate": 0.00,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_000pct_tgtFeas_099pct_20220313_100034\solutions"
                                    f"\solution_00077_000000018250_000000000013.json",
            "result_file": "UPDATE_output_Oklahoma_deptFail_000pct_tgtFeas_099pct",
        },
        {
            # 5, 99
            "target_feasibility_pct": 0.99,
            "depot_failure_rate": 0.05,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_005pct_tgtFeas_099pct_20220317_160224\solutions"
                                    f"\solution_00088_000000003650_000000000002.json",
            "result_file": "UPDATE_output_Oklahoma_deptFail_005pct_tgtFeas_099pct_20220317_160224",
        },
        {
            # 10, 99
            "target_feasibility_pct": 0.99,
            "depot_failure_rate": 0.10,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_010pct_tgtFeas_099pct_20220403_100250\solutions"
                                    f"\solution_00101_000000062050_000000000049.json",
            "result_file": "UPDATE_output_Oklahoma_deptFail_010pct_tgtFeas_099pct",
        },
        {
            # 0, 98
            "target_feasibility_pct": 0.98,
            "depot_failure_rate": 0.00,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_000pct_tgtFeas_098pct_20220313_100034\solutions"
                                    f"\solution_00067_000000010950_000000000006.json",
            "result_file": "UPDATE_output_Oklahoma_deptFail_000pct_tgtFeas_098pct",
        },
        {
            # 5, 98
            "target_feasibility_pct": 0.98,
            "depot_failure_rate": 0.05,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_005pct_tgtFeas_098pct_20220324_100814\solutions"
                                    f"\solution_00070_000000003650_000000000002.json",
            "result_file": "UPDATE_output_Oklahoma_deptFail_005pct_tgtFeas_098pct",
        },
        {
            # 10, 98
            "target_feasibility_pct": 0.98,
            "depot_failure_rate": 0.10,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_010pct_tgtFeas_098pct_20220403_110112\solutions"
                                    f"\solution_00080_000000010950_000000000009.json",
            "result_file": "UPDATE_output_Oklahoma_deptFail_010pct_tgtFeas_098pct",
        }
    ]
    pars_to_update.reverse()
    base_parfile = "./par_files/par1.json"
    base_parfile = parfile_reader(base_parfile)
    results = defaultdict(dict)
    for alternate in pars_to_update:
        print()
        print("======================================================================================================")
        print(f"File\t{alternate['result_file']}")
        print("======================================================================================================")
        new_parfile = copy.deepcopy(base_parfile)
        new_parfile.update(alternate)
        new_parfile_name = f'./UPDATE_pars_like_for_like/par_fail_{int(new_parfile["depot_failure_rate"] * 100)}' \
                           f'_feas_{int(new_parfile["target_feasibility_pct"] * 100)}.json'
        parfile_writer(new_parfile_name, new_parfile)
        success, trials, pct = main(new_parfile_name, trials=trials, result_folder="UPDATE_results_like_for_like",
                                    pickles="./pickles/pickles.json")
        old_results = read_json_generic("./UPDATE_results_like_for_like/results_unlike_fails.json")
        if old_results is not None:
            results.update(old_results)
        key = f"fail_{int(new_parfile['depot_failure_rate'] * 100)}_feas_{int(new_parfile['target_feasibility_pct'] * 100)}"
        results[key]['sucesses'] = success
        results[key]['trials'] = trials
        results[key]['pcts'] = pct
        json_writer(results, "./UPDATE_results_like_for_like/results_like_fails.json")


def trials2(trials=100):
    pars_to_update = [
        {
            # 0, 100
            "target_feasibility_pct": 1.00,
            "depot_failure_rate": 0.00,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_000pct_tgtFeas_100pct_20220313_100034\solutions"
                                    f"\solution_00101_000000040150_000000000030.json",
            "result_file": "UPDATE_UNLIKE_output_Oklahoma_deptFail_000pct_00pct_tgtFeas_100pct",
        },
        {
            # 5, 100
            "target_feasibility_pct": 1.00,
            "depot_failure_rate": 0.05,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_000pct_tgtFeas_100pct_20220313_100034\solutions"
                                    f"\solution_00101_000000040150_000000000030.json",
            "result_file": "UPDATE_UNLIKE_output_Oklahoma_deptFail_000pct_05pct_tgtFeas_100pct",
        },
        {
            # 10, 100
            "target_feasibility_pct": 1.00,
            "depot_failure_rate": 0.10,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_000pct_tgtFeas_100pct_20220313_100034\solutions"
                                    f"\solution_00101_000000040150_000000000030.json",
            "result_file": "UPDATE_UNLIKE_output_Oklahoma_deptFail_000pct_10pct_tgtFeas_100pct",
        },
        {
            # 0, 99
            "target_feasibility_pct": 0.99,
            "depot_failure_rate": 0.00,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_000pct_tgtFeas_099pct_20220313_100034\solutions"
                                    f"\solution_00077_000000018250_000000000013.json",
            "result_file": "UPDATE_UNLIKE_output_Oklahoma_deptFail_000pct_00pct_tgtFeas_099pct",
        },
        {
            # 5, 99
            "target_feasibility_pct": 0.99,
            "depot_failure_rate": 0.05,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_000pct_tgtFeas_099pct_20220313_100034\solutions"
                                    f"\solution_00077_000000018250_000000000013.json",
            "result_file": "UPDATE_UNLIKE_output_Oklahoma_deptFail_000pct_05pct_tgtFeas_099pct",
        },
        {
            # 10, 99
            "target_feasibility_pct": 0.99,
            "depot_failure_rate": 0.10,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_000pct_tgtFeas_099pct_20220313_100034\solutions"
                                    f"\solution_00077_000000018250_000000000013.json",
            "result_file": "UPDATE_UNLIKE_output_Oklahoma_deptFail_000pct_10pct_tgtFeas_099pct",
        },
        {
            # 0, 98
            "target_feasibility_pct": 0.98,
            "depot_failure_rate": 0.00,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_000pct_tgtFeas_098pct_20220313_100034\solutions"
                                    f"\solution_00067_000000010950_000000000006.json",
            "result_file": "UPDATE_UNLIKE_output_Oklahoma_deptFail_000pct_00pct_tgtFeas_098pct",
        },
        {
            # 5, 98
            "target_feasibility_pct": 0.98,
            "depot_failure_rate": 0.05,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_000pct_tgtFeas_098pct_20220313_100034\solutions"
                                    f"\solution_00067_000000010950_000000000006.json",
            "result_file": "UPDATE_UNLIKE_output_Oklahoma_deptFail_000pct_05pct_tgtFeas_098pct",
        },
        {
            # 10, 98
            "target_feasibility_pct": 0.98,
            "depot_failure_rate": 0.10,
            "fire_stations_subset": f"G:\DisasterLocationTool\outputs"
                                    f"\output_Oklahoma_deptFail_000pct_tgtFeas_098pct_20220313_100034\solutions"
                                    f"\solution_00067_000000010950_000000000006.json",
            "result_file": "UPDATE_UNLIKE_output_Oklahoma_deptFail_000pct_10pct_tgtFeas_098pct",
        }
    ]
    pars_to_update.reverse()
    base_parfile = "./par_files/par1.json"
    base_parfile = parfile_reader(base_parfile)
    results = defaultdict(dict)
    for alternate in pars_to_update:
        print()
        print("======================================================================================================")
        print(f"File\t{alternate['result_file']}")
        print("======================================================================================================")
        new_parfile = copy.deepcopy(base_parfile)
        new_parfile.update(alternate)
        new_parfile_name = f'./UPDATE_pars_unlike_fails/par_fail_{int(new_parfile["depot_failure_rate"] * 100)}' \
                           f'_feas_{int(new_parfile["target_feasibility_pct"] * 100)}.json'
        parfile_writer(new_parfile_name, new_parfile)
        success, trials, pct = main(new_parfile_name, trials=trials, result_folder="UPDATE_results_unlike_fails",
                                    pickles="./pickles/pickles.json")
        old_results = read_json_generic("./UPDATE_results_unlike_fails/results_unlike_fails.json")
        if old_results is not None:
            results.update(old_results)
        key = f"fail_{int(new_parfile['depot_failure_rate'] * 100)}_feas_{int(new_parfile['target_feasibility_pct'] * 100)}"
        results[key]['sucesses'] = success
        results[key]['trials'] = trials
        results[key]['pcts'] = pct
        json_writer(results, "./UPDATE_results_unlike_fails/results_unlike_fails.json")


if __name__ == '__main__':
    print(f"BEGINNING THE TRIALS")
    p = Process(target=trials2, args=(250,))
    p.start()
    p2 = Process(target=trials1, args=(250,))
    p2.start()
    # trials2(100)
    # trials1(100)
    print("STARTED!!")
    p.join()
    p2.join()
    print(f"FINISHED THE TRIALS")
