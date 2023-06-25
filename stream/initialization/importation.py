from numpy import load

def import_scenario_from_npy(filename):
    """
    This function imports a scenario from a .npy file.

    Parameters:
    filename (str): The name of the .npy file.

    Returns:
    dict: A dictionary containing the inputs read from the source file.
    """
    print("Original importation from " + filename + "...")
    Inputs = load(filename, allow_pickle=True).item(0)
    return Inputs
