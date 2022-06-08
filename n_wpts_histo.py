import file_readers
from TornadoCaseGetter import TornadoCaseGetter
from pickles.pickle_io import pickle_input, pickle_dumper
from utilities import parfile_reader


def n_wpt_histo(parfile_name, pickles=None):
    pars = parfile_reader(parfile_name)
    waypoints = file_readers.read_waypoint_file(pars['waypoints_file'])
    if pickles:
        pickle_pars = parfile_reader(pickles)
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
    data = []
    data.append(["date", "n_wpts"])
    for date in tornado_cases.dates:
        d, event = tornado_cases.get_specific_event(date)
        # case = tornado_cases.get_specific_case(date)
        n_wpt = len(event.waypoints)
        print(f"{date}\t{n_wpt}")
        data.append([date, n_wpt])

    import csv
    with open("data_waypoints.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)

if __name__ == '__main__':
    n_wpt_histo(parfile_name="./par_files/par1.json",
        pickles="./pickles/pickles.json")