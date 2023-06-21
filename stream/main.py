import os
import datetime
import numpy as np
import argparse

import sys

#
from .initialization.validate_and_complete_scenario import validate_and_complete_scenario
from .initialization.assignment import assignment
from .initialization.initialize_simulation import initialize_simulation
from .initialization.importation import import_scenario_from_npy
from .simulation.main_simulation_meso import main_simulation_meso

class AutoFlushStream:
    def __init__(self, stream):
        self.stream = stream

    def write(self, text):
        self.stream.write(text)
        self.stream.flush()

    def flush(self):
        self.stream.flush()

# Create an instance of AutoFlushStream for sys.stdout
sys.stdout = AutoFlushStream(sys.stdout)

def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("-i", "--input", required=True, help="Input file for the simulation")
    parser.add_argument("-o", "--output", help="Output directory for the simulation")
    parser.add_argument("--display_advance", action="store_true", help="Display the advance of the simulation")
    parsed_args = parser.parse_args(args)

    input_file = parsed_args.input
    output_dir = parsed_args.output
    display_advance = parsed_args.display_advance

    if not os.path.isfile(input_file):
        sys.exit(f"{input_file} does not exist.")

    try:
        run_simulation(input_file, output_dir = output_dir)
    except Exception as e:
        print(e)
        input("ERROR")

def get_stream_base_process():
    Process = {
        'import': import_scenario_from_npy,
        'validate_and_complete': validate_and_complete_scenario,
        'assignment': assignment,
        'initialize': initialize_simulation,
        'run': main_simulation_meso
    }
    return Process


def run_simulation(filename, custom_process=None, saveS=True, output_dir=None):
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
        if output_dir:
            __saveAsNpy(output_dir, S)
        else:
            directory = os.path.join(os.path.dirname(os.path.abspath(filename)), "results")
            try:
                os.makedirs(directory)
            except OSError as e:
                print("info : Results folder already exists")
            __saveAsNpy(directory, S)
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


def __saveAsNpy(directory, S):
    newName = "results" + datetime.datetime.now().strftime("_%Y%m%d_%H%M%S") + ".npy"
    path = os.path.join(directory, newName)
    np.save(path, S)
    print("Simulation saved in :")
    print(path)


