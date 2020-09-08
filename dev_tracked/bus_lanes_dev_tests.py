# -*- coding: utf-8 -*-

import numpy as np
import os
import matplotlib.pyplot as plt

"""
In this example, busses go from the southern entry to the eastern exit only
"""

# We load the inputs from the example file
Simulation = np.load(os.path.join(
    '..', 'example', 'bus_dev.npy'), allow_pickle=True).item()

# Load an old version Stream input file
# in which no "IsReservedTo" key is present in Links
from stream.initialization.validate_and_complete_scenario import validate_and_complete_scenario

"""
HERE IS THE ASSIGNMENT !
"""
# Assign link 15 to BUS (type 1) and link 14 to all other
Simulation["Links"][14]["IsReservedTo"] = list(filter(lambda x: x!= 1, list(Simulation["VehicleClass"].keys())))
Simulation["Links"][15]["IsReservedTo"] = [1]

# Test if "IsReservedTo" are set to []
validate_and_complete_scenario(Simulation)

"""
Part of the "assignment.py" file
"""
# --------- Creation of input dict for route calculation
inputDict = {}
for key in ["Links", "Nodes", "Entries", "Exits", "VehicleClass"]:
    inputDict.update({key: Simulation[key]})

# --------- Routes calculation
from stream.initialization.routes import getRoutes
Routes = getRoutes(inputDict)

"""
Entries : 1 8 11
Exits : 2 7 12
"""

# Assigning
from stream.initialization.assignment import assignment
Simulation = assignment(Simulation)

# This calculate the unique paths taken by the busses
uniquePaths = []
for veh in Simulation["Vehicles"].keys():
    if Simulation["Vehicles"][veh]["VehicleClass"]==1:
        if not(Simulation["Vehicles"][veh]["Path"] in uniquePaths):
            uniquePaths.append(Simulation["Vehicles"][veh]["Path"])
            
# plot them
from stream.analysis.analysis import plot_network
for Path in uniquePaths:
    plt.figure()
    plot_network( Simulation, color = (0.5, 0.5, 0.5), linewidth = 1, bool_linkid = True, bool_nodeid = False, new = False )
    for linkid in Path:
        plt.plot( Simulation["Links"][linkid]["Points"][0], Simulation["Links"][linkid]["Points"][1],\
        color = (.82, .37, .37), linewidth = 3 )
    plt.plot( Simulation["Links"][Path[0]]["Points"][0,0], Simulation["Links"][Path[0]]["Points"][1,0] ,'.', color='lime')
    plt.plot( Simulation["Links"][Path[-1]]["Points"][0,-1], Simulation["Links"][Path[-1]]["Points"][1,-1],'r.')
    plt.title("One path for buses")
    
    plt.show()


# This calculate the unique paths taken by the cars
uniquePaths = []
for veh in Simulation["Vehicles"].keys():
    if Simulation["Vehicles"][veh]["VehicleClass"]==0:
        if not(Simulation["Vehicles"][veh]["Path"] in uniquePaths):
            uniquePaths.append(Simulation["Vehicles"][veh]["Path"])
            
# plot them
from stream.analysis.analysis import plot_network
for Path in uniquePaths:
    plt.figure()
    plot_network( Simulation, color = (0.5, 0.5, 0.5), linewidth = 1, bool_linkid = True, bool_nodeid = False, new = False )
    for linkid in Path:
        plt.plot( Simulation["Links"][linkid]["Points"][0], Simulation["Links"][linkid]["Points"][1],\
        color = (.82, .37, .37), linewidth = 3 )
    plt.plot( Simulation["Links"][Path[0]]["Points"][0,0], Simulation["Links"][Path[0]]["Points"][1,0] ,'.', color='lime')
    plt.plot( Simulation["Links"][Path[-1]]["Points"][0,-1], Simulation["Links"][Path[-1]]["Points"][1,-1],'r.')
    plt.title("One path for cars")
    
    plt.show()            
    