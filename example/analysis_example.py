"""
Example Analysis
The analysis features will be changed in next versions...
"""

# imports
import numpy as np
import matplotlib.pyplot as plt
from stream.analysis.export import export_travel_times_on_links, export_flow_speed_on_links
from stream.analysis.analysis import *

import sys

# Get the filename from command line arguments
for arg in sys.argv:
    if len(sys.argv) == 1:
        print("No result file provided")
    else:
        filename = sys.argv[1]

# load the results
Simulation = np.load(filename, allow_pickle=True).item(0)

"""
CSV exports
"""

# Export Travel Times on links in csv format
export_travel_times_on_links(Simulation, '')

# Export Flow and Speed on links
export_flow_speed_on_links(Simulation, '')


"""
Graphs
"""
# reinitialisation of figures
plt.close("all")

# computation of all the travel times on links of network
TravelTimes = compute_travel_times_on_links(Simulation)

# Function to compute main statistics of flows on links of the network
Statistics = compute_stats_on_links(Simulation, TravelTimes)

# Plotting network
plot_network(Simulation)

# choice of a specific link or node for analyses
linkid = list(Simulation['Links'])[0]
NumIns = [Simulation['Nodes'][nodeid]['NumIncomingLinks']
          for nodeid in list(Simulation['Nodes'])]
NumOuts = [Simulation['Nodes'][nodeid]['NumOutgoingLinks']
           for nodeid in list(Simulation['Nodes'])]
nodeid = np.intersect1d(np.where(np.array(NumIns) > 0)[
                        0],  np.where(np.array(NumOuts) > 0)[0])
if len(nodeid) == 0:
    nodeid = -1
else:
    nodeid = nodeid[-1]
    nodeid = list(Simulation['Nodes'])[nodeid]
nodeid = 1

# Plotting trafficolor on the network
plot_trafficolor_on_network(Simulation, Statistics)

# Plotting flow-speed diagram on a link
plot_flow_speed_on_link(Statistics, linkid)

# Plotting cumulative count curves on a link
plot_cvc_on_link(Statistics, linkid)

# trajectories on a link
# plot_mean_trajectories_on_link( Statistics, linkid )

# plotting informations on a node
NodeEvent = node_info(Simulation, nodeid)
# plot_node_analysis( NodeEvent )

# ♥ traveil times on a path
Path = Simulation['Routes'][4]['Path']
plot_travel_times_on_path(Simulation, Path, bool_network=True)
