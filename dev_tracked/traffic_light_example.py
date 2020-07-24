# -*- coding: utf-8 -*-
"""
author: Aurélien Clairais

This script aims to add a traffic light on an arbitrary node from the example provided file.

The node with the traffic light is the Node 10.
The signal definition must follow the pattern :

Simulation["Signals"] = {key : value}
and associated with the nodes
Simulation["Nodes"][nodeID]["SignalsID"] = [the_ids] 
CAUTION : THE ID HAS TO BE SET ACCORDING WITH THE ORDER OF THE INCOMING BRANCHES
"""

import numpy as np
import os
import matplotlib.pyplot as plt

from stream.main import run_simulation_from_inputs
from stream.analysis.analysis import node_info

# We load the inputs from the example file
Simulation = np.load(os.path.join(
    '..', 'example', 'inputs.npy'), allow_pickle=True).item()

"""
Displaying the node number 10 with :
print(Simulation["Nodes"][10])

Yields: 
{   
    'name': None,
    'Type': 0,
    'OutgoingLinksID': array([10], dtype=int32),
    'IncomingLinksID': array([5, 9], dtype=int32),
    'NumOutgoingLinks': 1,
    'NumIncomingLinks': 2
}
So, the incoming links of the node number 10 are the links 5 and 9.
"""

# We define the green times for the branch from 5 and the branch from 9
green_5 = 30
green_9 = 20

# We define a function to calculate the green starts and red starts on the whole simulation
# For the moment, the user has to define every green and red starts manually
# TODO:  Insert the green and red starts to initialization and provides the user a way to overwrite the default behaviour


def makeSignalTimes(green_time, red_time, duration, startGreen=True):
    step = green_time+red_time
    if startGreen:
        green_starts = np.arange(
            start=duration[0], stop=duration[1] + step, step=green_time+red_time)
        red_starts = np.arange(
            start=duration[0]+green_time, stop=duration[1] + step, step=green_time+red_time)
    else:
        red_starts = np.arange(
            start=duration[0], stop=duration[1] + step, step=green_time+red_time)
        green_starts = np.arange(
            start=duration[0]+red_time, stop=duration[1] + step, step=green_time+red_time)

    red_starts = np.append(red_starts, np.inf)
    green_starts = np.append(green_starts, np.inf)
    return {'green_starts': green_starts, 'red_starts': red_starts}


# We create the dictionnary of Traffic lights
# Here the two signals are synchronized so the green time from 5 is equal the red from 9
# For more complex behavior, the user has to set manually the green and red times
# TODO: provide a tool to help the user to design the signals in simulation
Signals = {
    1: makeSignalTimes(green_5, green_9, Simulation['General']['SimulationDuration']),
    2: makeSignalTimes(green_9, green_5, Simulation['General']['SimulationDuration'], False)
}

# According to the pattern in intro, the Signals variable take the dict
Simulation['Signals'] = Signals
# We say to the nodes that they are associated with Signals
Simulation['Nodes'][10]['SignalsID'] = [1, 2]

# We run the simulation
Simulation = run_simulation_from_inputs(Simulation)

# We get the output from the node 10
NodeEvent = node_info(Simulation, 10)

# Here we plot the two CVC from 5 and 9 to validate the traffic light behaviour
plt.figure()
plt.plot(NodeEvent['In'][0]['Times'], np.arange(
    1, len(NodeEvent['In'][0]['Times'])+1))
plt.plot(NodeEvent['In'][1]['Times'], np.arange(
    1, len(NodeEvent['In'][1]['Times'])+1))
plt.show()
