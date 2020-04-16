import os
import datetime
import numpy as np

#
from .initialization.validate_and_complete_scenario import validate_and_complete_scenario
from .initialization.assignment import assignment
from .initialization.initialize_simulation import initialize_simulation
from .initialization.importation import import_scenario_from_npy
from .simulation.main_simulation_meso import main_simulation_meso


def get_stream_base_process():
    Process = {
        'import': import_scenario_from_npy,
        'validate_and_complete': validate_and_complete_scenario,
        'assignment': assignment,
        'initialize': initialize_simulation,
        'run': main_simulation_meso
    }
    return Process


def run_simulation(filename, custom_process=None, saveS=True):
    # if a custom process has been set, use it
    if not custom_process:
        Process = get_stream_base_process()
    else:
        Process = custom_process

    S = Process['import'](filename)
    S = Process['validate_and_complete'](S)
    S = Process['assignment'](S)
    S = Process['initialize'](S)
    S = Process['run'](S, S["General"]["SimulationDuration"][1])
    # Saving
    if saveS:
        __saveAsNpy(filename, S)
    return S


def run_simulation_from_inputs(Inputs, custom_process=None):
    # if a custom process has been set, use it
    if not custom_process:
        Process = get_stream_base_process()
    else:
        Process = custom_process

    S = Process['validate_and_complete'](Inputs)
    S = Process['assignment'](S)
    S = Process['initialize'](S)
    S = Process['run'](S, S["General"]["SimulationDuration"][1])
    return S


def __saveAsNpy(filename, S):
    directory = os.path.join(os.path.dirname(
        os.path.abspath(filename)), "results")
    newName = "results" + datetime.datetime.now().strftime("_%Y%m%d_%H%M%S") + ".npy"
    path = os.path.join(directory, newName)
    try:
        os.makedirs(directory)
    except OSError as e:
        print("info : Results folder already exists")
    np.save(path, S)
    print("Simulation saved in :")
    print(path)
    input('Hit <Return> to continue')

# If stream is called from command line


def main(args):
    if len(args) == 0:
        sys.exit("You must specify scenario files in NPY format...")
        input()
    else:
        for arg in args:
            if arg.split('.')[-1] == 'npy':
                exists = os.path.isfile(arg)
                if exists:
                    try:
                        run_simulation(arg)
                    except Exception as e:
                        print(e)
                        input('ERROR')
                else:
                    print(arg + " does not exists.")
                    input()
                    continue
            else:
                print(arg + "do not have the correct extension.")
                input()
                continue


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
