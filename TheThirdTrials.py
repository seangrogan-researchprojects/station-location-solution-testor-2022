import copy
import os
from collections import defaultdict

from main import main
from utilities import parfile_reader, parfile_writer, json_writer


def the_third_trials(
        default_parfile,
        par_data_to_update,
        n_iter,
        n_trials,
        base_output_folder,
):
    base_parfile = parfile_reader(default_parfile)
    results = defaultdict(dict)
    alternate = par_data_to_update
    new_parfile = copy.deepcopy(base_parfile)
    new_parfile.update(alternate)
    new_parfile_name = f'./{base_output_folder}/PARS_{base_output_folder}/' \
                       f'PAR_FAIL_{int(new_parfile["depot_failure_rate"] * 100)}' \
                       f'_FEAS_{int(new_parfile["target_feasibility_pct"] * 100)}.json'
    parfile_writer(new_parfile_name, new_parfile)
    success, trials, pct = main(new_parfile_name, trials=n_trials,
                                result_folder=base_output_folder,
                                pickles="./pickles/pickles.json")
    key = f"{n_iter:0>4}_{base_output_folder}"
    results[key]['sucesses'] = success
    results[key]['trials'] = trials
    results[key]['pcts'] = pct
    json_writer(results, f"./{base_output_folder}/results_{n_iter:0>2}_{base_output_folder}.json")
    return 0


def get_solution_filename(base_path, feas, fail):
    list_of_output_folders = os.listdir(base_path)
    dater = dict()
    for folder in list_of_output_folders:
        folder_data = folder.split("_")
        feas_data, fail_data = int(folder_data[5][:3]), int(folder_data[3][:3])
        dater[(feas_data, fail_data)] = folder
    solution_folder = dater[(feas, fail)]
    list_of_solution_folders = os.listdir(f"{base_path}/{solution_folder}/solutions")
    list_of_solution_folders.sort()
    file = f"{base_path}/{solution_folder}/solutions/{list_of_solution_folders[0]}"
    return file


if __name__ == "__main__":
    bath_solution_folder_path = "G:/DisasterLocationTool/outputs"
    case_type = "UNMATCHED"
    n_iter=5
    n_trials=10
    for n in range(n_iter):
        for feas in [100, 99, 98]:
            for fail in [0, 5, 10]:
                if case_type in {"UNMATCHED"}:
                    solution_filename = get_solution_filename(bath_solution_folder_path, feas=feas, fail=0)
                else:
                    solution_filename = get_solution_filename(bath_solution_folder_path, feas=feas, fail=fail)
                updated_par_data = {
                    "target_feasibility_pct": (feas / 100),
                    "depot_failure_rate": (fail / 100),
                    "fire_stations_subset": solution_filename,
                    "result_file": f""
                }
                the_third_trials(
                    default_parfile="./par_files/par1.json",
                    par_data_to_update=updated_par_data,
                    n_iter=n,
                    n_trials=n_trials,
                    base_output_folder=f"{case_type}/{case_type}_TgtFEAS_{feas:0>3}_FAIL_{fail:0>3}_nTrials_{n_trials:0>3}_{n:0>2}of{n_iter:0>2}"
                )
