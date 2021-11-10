"""
Functions to import scenario from sources

list :
    - import_scenario_from_npy(filename):
        Inputs :
            filename (string) : the file of the source
        Outputs : 
            Inputs (dict) : the inputs read from source and to be processedby the model

"""

from numpy import load

"""Import the data file in numpy format
"""
def import_scenario_from_npy(filename):
    print("Original importation from " + filename + "...")
    Inputs = load(filename, allow_pickle=True).item(0)
    return Inputs
