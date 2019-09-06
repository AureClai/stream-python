# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 10:41:28 2019

@author: aurelien.clairais


# =============================================================================
# Code structure
# =============================================================================


# Loading packages
# Export in .csv format
    # export_flow_speed_on_links( Simulation, ilink )
    
"""

# =============================================================================
# Loading packages
# =============================================================================


import numpy as np
import matplotlib.pyplot as plt

from .analysis import compute_travel_times_on_links, compute_stats_on_links

import csv
import os
# import pdb; pdb.set_trace() # debug mode : CC+CV in the script


# =============================================================================
# Computational functions
# =============================================================================


def export_flow_speed_on_links( Simulation, filePath ):
    #...
    TravelTimes = compute_travel_times_on_links( Simulation )
    Statistics = compute_stats_on_links( Simulation, TravelTimes )
    #...
    column_names = ['link_id', 'time', 'flow', 'speed']
    res = np.array(column_names).reshape((1,4))
    # loop on all links
    for ilink in list(Simulation["Links"]):
        nLines = Statistics[ilink]["Times"].shape[0]
        times = Statistics[ilink]["Times"].reshape((nLines, 1))
        flows = Statistics[ilink]["Flows"].reshape((nLines, 1))
        speeds = Statistics[ilink]["Speeds"].reshape((nLines, 1))
        ids = np.ones(times.shape) * ilink
        link_infos = np.hstack((ids, times, flows, speeds))
        res = np.vstack((res, link_infos))
        
    #export csv
    np.savetxt(os.path.join(filePath,"speed_flow.csv"), res, fmt='%s',  delimiter = ";")
    return

def export_travel_times_on_links(Simulation, filePath):
    #...
    TravelTimes = compute_travel_times_on_links( Simulation )
    column_names = ['link_id', 'entry', 'exit', 'travel']
    res = np.array(column_names).reshape((1,4))
    #...
    # loop on all links
    for ilink in list(Simulation["Links"]):
        nLines = TravelTimes[ilink]["ArrivalTimes"].shape[0]
        atimes = TravelTimes[ilink]["ArrivalTimes"].reshape((nLines, 1))
        dtimes = TravelTimes[ilink]["DepartureTimes"].reshape((nLines, 1))
        ttimes = TravelTimes[ilink]["TravelTimes"].reshape((nLines, 1))
        ids = np.ones(atimes.shape) * ilink
        link_infos = np.hstack((ids, dtimes, atimes, ttimes))
        res = np.vstack((res, link_infos))
        
    #export csv
    np.savetxt(os.path.join(filePath,"travel_times.csv"), res, fmt='%s',  delimiter = ";")
    return