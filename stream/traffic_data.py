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


import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
# ...
import analysis as san


# =============================================================================
# Function
# =============================================================================


def initialise_loop(data, loopid, days, times, init='zero' ):
    '''initialize a loop dictionary in the data dictionary'''
    # ...
    # initialisation
    if not 'Loops' in data: data['Loops'] = {}
    data['Loops'][loopid] = {}
    # ...
    data['Loops'][loopid]['LinkID'] = -1 # id of link on the Stream network
    data['Loops'][loopid]['StepTime'] = times[1] - times[0] # time step of loops, in sec
    data['Loops'][loopid]['Times'] = times
    data['Loops'][loopid]['NumTimes'] = len(times)
    data['Loops'][loopid]['Days'] = days # days where measures are provided
    data['Loops'][loopid]['Weekdays'] = get_weekdays(days) # sunday, monday
    data['Loops'][loopid]['NumDays'] = len(days)
    # ...
    if init == 'zero':
        data['Loops'][loopid]['Flows'] = np.zeros((data['Loops'][loopid]['NumTimes'],data['Loops'][loopid]['NumDays']))
        data['Loops'][loopid]['Speeds'] = np.zeros((data['Loops'][loopid]['NumTimes'],data['Loops'][loopid]['NumDays']))
    elif init == 'rand':
        data['Loops'][loopid]['Flows'] = 4000 * np.random.rand(data['Loops'][loopid]['NumTimes'],data['Loops'][loopid]['NumDays'])
        data['Loops'][loopid]['Speeds'] = 130 * np.random.rand(data['Loops'][loopid]['NumTimes'],data['Loops'][loopid]['NumDays'])
    # ...
    return data


def initialise_tt_data(data, odttid, days, times, init='zero' ):
    '''initialize a travel time data dictionary in the data dictionary'''
    # ...
    # initialisation
    if not 'TravelTimes' in data: data['TravelTimes'] = {}
    data['TravelTimes'][odttid] = {}
    # ...
    data['TravelTimes'][odttid]['NodeUpID'] = -1 # id of upstream link on the Stream network
    data['TravelTimes'][odttid]['NodeDownID'] = -1 # id of upstream link on the Stream network
    data['TravelTimes'][odttid]['StepTime'] = times[1] - times[0] # time step of loops, in sec
    data['TravelTimes'][odttid]['Times'] = times
    data['TravelTimes'][odttid]['NumTimes'] = len(times)
    data['TravelTimes'][odttid]['Days'] = days # days where measures are provided
    data['TravelTimes'][odttid]['Weekdays'] = get_weekdays(days) # sunday, monday
    data['TravelTimes'][odttid]['NumDays'] = len(days)
    # ...
    if init == 'zero':
        data['TravelTimes'][odttid]['TravelTimes'] = np.zeros((data['TravelTimes'][odttid]['NumTimes'],data['TravelTimes'][odttid]['NumDays']))
    elif init == 'rand':
        data['TravelTimes'][odttid]['TravelTimes'] = np.random.rand(data['TravelTimes'][odttid]['NumTimes'],data['TravelTimes'][odttid]['NumDays'])
    # ...
    return data


def get_weekdays(list_days):
    '''give weekdays from a list of days in the format "DD/MM/YYYY" '''
    # ...
    list_weekdays = []
    for date in list_days:
        day = int(date[0:2])
        month = int(date[3:5])
        year = int(date[6:10])
        dt = datetime.datetime(year,month,day)
        weekday = dt.weekday() + 1
        list_weekdays.append(weekday)
    # ...
    return list_weekdays


def get_stats_about_data(data, sensor_type, sensor_id, measure_type, selected_days=[]):
    '''compute statistics on data of a given type on selected days'''
    # ...
    if len(selected_days) == 0:
        selected_days = np.arange(data[sensor_type][sensor_id][measure_type].shape[1])
    # ...
    var = {}
    var['times'] = (1/3600)*data[sensor_type][sensor_id]['Times']
    var['med'] = np.median( data[sensor_type][sensor_id][measure_type][:,selected_days], axis=1 )
    var['min'] = np.min( data[sensor_type][sensor_id][measure_type][:,selected_days], axis=1 )
    var['max'] = np.max( data[sensor_type][sensor_id][measure_type][:,selected_days], axis=1 )
    # ...
    return var


def plot_stats_about_data(data, sensor_type, sensor_id, measure_type, selected_days, new=True):
    '''plot the computed statistics'''
    # ...
    var = get_stats_about_data(data, sensor_type, sensor_id, measure_type, selected_days)
    # ...
    if new:
        plt.figure()
    # ...
    plt.title( measure_type[0:-1] + " on " + sensor_type[0:-1] + " " + str(sensor_id))
    plt.xlabel('Time')
    plt.ylabel(measure_type)
    # ...
    ax = plt.axes() # axes courant
    x = np.concatenate((var['times'],var['times'][-1::-1]))
    y = np.concatenate((var['min'],var['max'][-1::-1]))
    coord = np.vstack((x,y)).T
    poly = ptc.Polygon( coord, linewidth=1, edgecolor='none', facecolor=(1, .8, .8)) # création du patch d'un polygone
    ax.add_patch(poly) # ajout du patch à l'axe
    # ...
    ax.plot( var['times'], var['med'], color='r' )
    # ...
    return var


# =============================================================================
# Execution of functions
# =============================================================================

if __name__=='__main__':
    # ...
    data = {}
    
    # adding a random loop dataset
    loopid = 'MG47.J4'
    times = np.arange(0,86400,360)
    days = ['01/09/2019','02/09/2019']
    data = initialise_loop(data, loopid, days, times, 'rand' )
    
    # adding a random travel time dataset
    odttid = 'B1 - B2'
    days = ['03/09/2019','04/09/2019']
    data = initialise_tt_data(data, odttid, days, times, 'rand' )
    
    # computation and plot
    plt.close("all")
    selected_days = np.arange(data['Loops'][loopid]['NumDays'])
    flow = plot_stats_about_data(data, 'Loops', loopid, 'Flows', selected_days)
    speed = plot_stats_about_data(data, 'Loops', loopid, 'Speeds', selected_days)
    speed = plot_stats_about_data(data, 'TravelTimes', odttid, 'TravelTimes', selected_days)
    
    
    # =============================================================================
    # reinitialisation of figures
    plt.close("all")

    # loading a Simulation.npy
    Simulation = np.load('../simulation.npy').item(0)
    Statistics = san.compute_stats_on_links( Simulation, StepTime=60 )
    


