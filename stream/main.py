import os
import datetime
import numpy as np

#
from initialization.validate_and_complete_scenario import validate_and_complete_scenario
from initialization.assignment import assignment
from initialization.initialize_simulation import initialize_simulation
from simulation.main_simulation_meso import main_simulation_meso

def runSimulation(filename, saveS = True):
    print("Running simulation for " + filename)
    Inputs = np.load(filename).item(0)
    #
    S = validate_and_complete_scenario(Inputs)
    S = assignment(S)
    S = initialize_simulation(S)

    S = main_simulation_meso(S, S["General"]["SimulationDuration"][1])
    # Saving
    if saveS:
        __saveAsNpy(filename, S)
    return S

def __saveAsNpy(filename, S):
    filename = ".".join(filename.split('.')[0:-1])
    filename = filename + datetime.datetime.now().strftime("_%Y%m%d_%H%M%S") + ".npy"
    np.save(filename, S)
    print("Simulation saved in :")
    print(filename)
    input('Hit <Return> to continue')

# If stream is called from command line
def main(args):
    if len(args)==0:
        sys.exit("You must specify scenario files in NPY format...")
        input()
    else:
        for arg in args:
            if arg.split('.')[-1]=='npy':
                exists = os.path.isfile(arg)
                if exists:
                    try:
                        runSimulation(arg)
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
