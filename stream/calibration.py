# -*- coding: utf-8 -*-


# =============================================================================
# Code structure
# =============================================================================


# data = initialise_loop(data, loopid, days, times, init)
# data = initialise_tt_data(data, odttid, days, times, init)
# list_weekdays = get_weekdays(list_days)
# var = get_stats_about_data(data, sensor_type, sensor_id, measure_type, selected_days)
# var = plot_stats_about_data(data, sensor_type, sensor_id, measure_type, selected_days, new)


# =============================================================================
# Loading packages
# =============================================================================


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
# ...
import traffic_data as dat
import analysis as san


# =============================================================================
# Function
# =============================================================================


def get_list_of_loops_on_links(Simulation, Data):
    '''give the list of loops associated with a link id on the simulation network'''
    # ...
    list_of_loops = []
    for loopid in list(Data['Loops']):
        linkid = Data['Loops'][loopid]['LinkID']
        if linkid in list(Simulation['Links']):
            list_of_loops.append(loopid)
    # ...
    return list_of_loops


def get_proper_dimensions_for_subplot(n):
    '''define good number of lines and columns for a subplot of n plots'''
    # ...
    if n in [0,1] :   lig = 1; col = 1
    elif n == 2 :     lig = 1; col = 2
    elif n == 3 :     lig = 1; col = 3
    elif n == 4 :     lig = 2; col = 2
    elif n in [5,6] : lig = 2; col = 3
    elif n in [7,8] : lig = 2; col = 4
    elif n == 9 :     lig = 3; col = 3
    else:             lig = int(np.sqrt(n)); col = int(n / lig) + 1
    # ...
    return (lig,col)


def plot_calibration_results(Statistics, Data, measure_type):
    '''plot the figure that show the calibration results on a variable'''
    # ...
    list_of_loops = get_list_of_loops_on_links(Simulation, Data)
    # ...
    lig, col = get_proper_dimensions_for_subplot(len(list_of_loops))
    # ...
    if measure_type == 'Flows' : sensor_type = 'Loops'
    elif measure_type == 'Speeds' : sensor_type = 'Loops'
    # ...
    if len(list_of_loops)>0: plt.figure()
    for iloop,loopid in enumerate(list_of_loops):
        linkid = Data['Loops'][loopid]['LinkID']
        var_data = dat.get_stats_about_data(Data, sensor_type, loopid, measure_type)
        var_simu = {'times' : (1/3600)*Statistics[linkid]['Times'],
                     'values': Statistics[linkid][measure_type]}
        # ...
        plt.subplot(lig,col,iloop+1)
        plt.title('Loop ' + str(loopid) + ' on link ' + str(linkid))
        plt.xlabel('Time [h]')
        if measure_type == 'Flows' : plt.ylabel('Flow [veh/h]')
        elif measure_type == 'Speeds' : plt.ylabel('Speed [km/h]')
        plt.plot(var_data['times'],var_data['med'])
        plt.plot(var_simu['times'],var_simu['values'])
        plt.xlim( var_simu['times'][0], var_simu['times'][-1] + var_simu['times'][1] - var_simu['times'][0])
        # ...
        if iloop==0:
            plt.legend(['data','simulation'])
    # ...
    return True
    


# =============================================================================
# Execution of functions
# =============================================================================

if __name__=='__main__':
    
    # ...
    # generation of synthetic data
    Data = {}
    steptime = 360
    times = np.arange(0,86400,steptime)
    days = ['01/09/2019','02/09/2019']
    
    # adding a random loop dataset
    loopid = 'MG47.J4'
    Data = dat.initialise_loop(Data, loopid, days, times, 'rand' )
    Data['Loops'][loopid]['LinkID'] = 27
    # ...
    loopid = 'MJ84.K2'
    Data = dat.initialise_loop(Data, loopid, days, times, 'rand' )
    Data['Loops'][loopid]['LinkID'] = 29
    
    # adding a random travel time dataset
    odttid = 'B1 - B2'
    Data = dat.initialise_tt_data(Data, odttid, days, times, 'rand' )
    
    
    # =============================================================================
    # reinitialisation of figures
    plt.close("all")

    # loading a Simulation.npy
    Simulation = np.load('../simulation.npy').item(0)
    Statistics = san.compute_stats_on_links( Simulation, StepTime=60 )
    
    plot_calibration_results(Statistics, Data, 'Flows')
    plot_calibration_results(Statistics, Data, 'Speeds')
    
    
# ...


