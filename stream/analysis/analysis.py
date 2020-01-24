# -*- coding: utf-8 -*-


# =============================================================================
# Code structure
# =============================================================================


# Loading packages
# Computational functions
    # TravelTimes = compute_travel_times_on_links( Simulation )
    # Statistics = compute_stats_on_links( Simulation, TravelTimes )
    # NodeEvent = node_info( Simulation, nodeid )
    # PathTravelTimes = compute_travel_times_on_path( Simulation, Path )
    # coord = node_coord( Simulation, nodeid )
# Plot functions on network
    # plot_network( Simulation )
    # plot_trafficolor_on_network( Simulation, Statistics )
# Plot functions on graphics
    # plot_flow_speed_on_link( Statistics, ilink )
    # plot_cvc_on_link( Statistics, ilink )
    # plot_mean_trajectories_on_link( Statistics, ilink )
    # plot_travel_times_on_path( Simulation, PathTravelTimes, Path )
    # plot_node_analysis( NodeEvent, remove_shadow=1 )
# Applying functions


# =============================================================================
# Loading packages
# =============================================================================


import numpy as np
import matplotlib.pyplot as plt
# import pdb; pdb.set_trace() # debug mode : CC+CV in the script


# =============================================================================
# Computational functions
# =============================================================================


def compute_travel_times_on_links( Simulation ):
    '''Function to compute travel times on all the links of the network'''
    # ...
    # initialisation of dict
    TravelTimes = {}
    for ilink in list( Simulation["Links"] ):
        TravelTimes[ilink] = {}
        TravelTimes[ilink]["DepartureTimes"] = []
        TravelTimes[ilink]["ArrivalTimes"] = []
        TravelTimes[ilink]["TravelTimes"] = []
    # ...
    # complete dict with meso results
    for iveh in list(Simulation["Vehicles"]):
        for link in range(len(Simulation["Vehicles"][iveh]["RealPath"])):
            ilink = Simulation["Vehicles"][iveh]["RealPath"][link]
            DT = Simulation["Vehicles"][iveh]["NodeTimes"][link]
            AT = Simulation["Vehicles"][iveh]["NodeTimes"][link+1]
            TT = AT - DT
            if TT > 0: # sinon, trajet pas fini (voir même pas commencé)
                TravelTimes[ilink]["DepartureTimes"].append(DT)
                TravelTimes[ilink]["ArrivalTimes"].append(AT)
                TravelTimes[ilink]["TravelTimes"].append(TT)
    # ...
    # finalisation of dict : conversion to numpy arrays
    for ilink in list( Simulation["Links"] ):
        my_array = np.vstack((TravelTimes[ilink]["DepartureTimes"],TravelTimes[ilink]["ArrivalTimes"],TravelTimes[ilink]["TravelTimes"])).T
        my_array = my_array[my_array[:,0].argsort()].T
        TravelTimes[ilink]["DepartureTimes"] = my_array[0,:]
        TravelTimes[ilink]["ArrivalTimes"] = my_array[1,:]
        TravelTimes[ilink]["TravelTimes"] = my_array[2,:]
    # ...
    return TravelTimes


def compute_stats_on_links( Simulation, TravelTimes = None, StepTime=60 ):
    '''Function to compute main statistics of flows on links of the network'''
    # ...
    if TravelTimes == None:
        TravelTimes = compute_travel_times_on_links( Simulation )
    # ...
    # initialisation of dict
    Statistics = {}
    SD = Simulation["General"]["SimulationDuration"]
    Bins = np.arange(SD[0],SD[1]+StepTime,StepTime) # toutes les 6 minutes sur 24 h
    for ilink in list( Simulation["Links"] ):
        Statistics[ilink] = {}
        # ...
        # free travel time
        Statistics[ilink]["FreeTravelTime"] = Simulation["Links"][ilink]["Length"] / Simulation["Links"][ilink]["Speed"]
        # ...
        # Times
        Statistics[ilink]["Times"] = Bins[0:-1]
        # ...
        # Flow
        AT = TravelTimes[ilink]["ArrivalTimes"]
        Statistics[ilink]["Flows"] = (3600/StepTime) * np.histogram( AT, bins=Bins )[0] # veh/h
        DT = TravelTimes[ilink]["DepartureTimes"]
        Statistics[ilink]["InFlows"] = (3600/StepTime) * np.histogram( DT, bins=Bins )[0] # veh/h
        # ...
        # Demand if relevant
        nodeup = Simulation['Links'][ilink]['NodeUpID']
        if nodeup in list(Simulation['Entries']): # this link is an entry link
            DemT = Simulation['Events'][nodeup]['Arrivals'][0]['Time']
            Statistics[ilink]["Demand"] = (3600/StepTime) * np.histogram( DemT, bins=Bins )[0] # veh/h
        else:
            Statistics[ilink]["Demand"] = np.zeros(len(Statistics[ilink]["Flows"]))
        # ...
        # Speed
        if len(TravelTimes[ilink]["ArrivalTimes"])>0:
            TT = np.interp( Bins[0:-1], TravelTimes[ilink]["ArrivalTimes"], TravelTimes[ilink]["TravelTimes"] )
        else:
            TT = -1 * np.ones(len(Statistics[ilink]["Flows"]))
        Statistics[ilink]["Speeds"] = 3.6 * Simulation["Links"][ilink]["Length"] / TT # km/h
        # ...
        # vehicles travel times
        Statistics[ilink]["DepartureTimes"] = TravelTimes[ilink]["DepartureTimes"]
        Statistics[ilink]["ArrivalTimes"] = TravelTimes[ilink]["ArrivalTimes"]
        Statistics[ilink]["TravelTimes"] = TravelTimes[ilink]["TravelTimes"]
        # ...
        # Link caracteristics
        Statistics[ilink]["Capacity"] = 3600 * Simulation['Links'][ilink]["Capacity"]
        Statistics[ilink]["Length"] = Simulation['Links'][ilink]["Length"]
    # ...
    return Statistics


def node_info( Simulation, nodeid ):
    '''Function to gather all information about passage times of vehicles at a node'''
    # ...
    NumIns = len(Simulation['Events'][nodeid]['Arrivals'])
    NumOuts = len(Simulation['Events'][nodeid]['Exits']) # interesting fields : 'Time', 'PreviousLinkID'
    # ...
    NodeEvent = {}
    NodeEvent['Info'] = {}
    NodeEvent['Info']['ID'] = nodeid
    NodeEvent['Info']['NumIns'] = NumIns
    NodeEvent['Info']['NumOuts'] = NumOuts
    # ...
    NodeEvent['Out'] = {}
    linksout = Simulation['Nodes'][nodeid]['OutgoingLinksID']
    for out in range(NumOuts):
        NodeEvent['Out'][out] = {}
        Times = Simulation['Events'][nodeid]['Exits'][out]['Time']
        if len(Times)>0:
            NodeEvent['Out'][out]['Times'] = Times
            NodeEvent['Out'][out]['Headways'] = np.concatenate( ([np.inf], Times[1:] - Times[0:-1]) )
            NodeEvent['Out'][out]['Flow'] = 3600/NodeEvent['Out'][out]['Headways']
            NodeEvent['Out'][out]['PreviousLink'] = Simulation['Events'][nodeid]['Exits'][out]['PreviousLinkID']
        else:
            NodeEvent['Out'][out]['Times'] = np.array([])
            NodeEvent['Out'][out]['Headways'] = np.array([])
            NodeEvent['Out'][out]['Flow'] = np.array([])
            NodeEvent['Out'][out]['PreviousLink'] = np.array([])
        # ...
        if out < len(linksout):
            linkid = linksout[out]
            NodeEvent['Out'][out]['LinkID'] = linkid
            NodeEvent['Out'][out]['Capacity'] = 3600 * Simulation['Links'][linkid]['Capacity']
        else:
            NodeEvent['Out'][out]['LinkID'] = -1
            NodeEvent['Out'][out]['Capacity'] = 0
    # ...
    Times = np.zeros(0)
    PreviousLink = np.zeros(0)
    NextLink = np.zeros(0)
    for out in range(NumOuts):
        Times = np.concatenate( (Times, Simulation['Events'][nodeid]['Exits'][out]['Time']) )
        PreviousLink = np.concatenate( (PreviousLink, Simulation['Events'][nodeid]['Exits'][out]['PreviousLinkID']) )
        NextLink = np.concatenate( (NextLink, out*np.ones(len(Simulation['Events'][nodeid]['Exits'][out]['Time'])) ))
    # ...
    linksin = Simulation['Nodes'][nodeid]['IncomingLinksID']
    NodeEvent['In'] = {}
    for iin in range(NumIns):
        NodeEvent['In'][iin] = {}
        liste = np.where(PreviousLink==iin)[0]
        if len(liste)>0:
            order = np.argsort(Times[liste])
            NodeEvent['In'][iin]['Times'] = Times[liste[order]]
            NodeEvent['In'][iin]['Headways'] = np.concatenate( ([np.inf], Times[liste[order]][1:] - Times[liste[order]][0:-1]) )
            NodeEvent['In'][iin]['Flow'] = 3600/NodeEvent['In'][iin]['Headways']
            NodeEvent['In'][iin]['NextLink'] = NextLink[liste[order]]
        else:
            NodeEvent['In'][iin]['Times'] = np.array([])
            NodeEvent['In'][iin]['Headways'] = np.array([])
            NodeEvent['In'][iin]['Flow'] = np.array([])
            NodeEvent['In'][iin]['NextLink'] = np.array([])
        # ...
        if iin < len(linksin):
            linkid = linksin[iin]
            NodeEvent['In'][iin]['LinkID'] = linkid
            NodeEvent['In'][iin]['Capacity'] = 3600 * Simulation['Links'][linkid]['Capacity']
        else:
            NodeEvent['In'][iin]['LinkID'] = -1
            NodeEvent['In'][iin]['Capacity'] = 0
    # ...
    return NodeEvent


def node_coord( Simulation, nodeid ):
    '''Function to compute the coordinates of a node'''
    if nodeid not in list(Simulation['Nodes']):
        coord = np.array( [np.nan, np.nan] )
    else:
        numpoints = 0
        coords = np.array([0,0])
        for linkid in Simulation['Nodes'][nodeid]['IncomingLinksID']:
            coords = coords + Simulation['Links'][linkid]['Points'][:,-1]
            numpoints += 1
        for linkid in Simulation['Nodes'][nodeid]['OutgoingLinksID']:
            coords = coords + Simulation['Links'][linkid]['Points'][:,0]
            numpoints += 1
        # ...
        coord = coords / numpoints
    # ...
    return coord


def compute_travel_times_on_path( Simulation, Path ):
    '''Function to compute travel times of all the vehicle classes on a given path'''
    # ...
    # initialisation
    PathTravelTimes = {}
    for iclass in list(Simulation['VehicleClass']):
        PathTravelTimes[iclass] = {}
        PathTravelTimes[iclass]['VehicleClass'] = Simulation['VehicleClass'][iclass]['Name']
        PathTravelTimes[iclass]['DepartureTime'] = []
        PathTravelTimes[iclass]['TravelTime'] = []
    # ...
    # completion
    for veh in list(Simulation['Vehicles']):
        VehiclePath = Simulation['Vehicles'][veh]['Path']
        (boolean_path_included, ind_beg, ind_end) = is_a_path_included_in_the_vehicle_path( VehiclePath, Path )
        if boolean_path_included:
            NodeTimes = Simulation['Vehicles'][veh]['NodeTimes']
            DT = NodeTimes[ind_beg]
            AT = NodeTimes[ind_end]
            TT = AT - DT
            if TT > 0:
                iclass = Simulation['Vehicles'][veh]['VehicleClass']
                PathTravelTimes[iclass]['DepartureTime'].append(DT)
                PathTravelTimes[iclass]['TravelTime'].append(TT)
    # ...
    # ordering
    for iclass in list(Simulation['VehicleClass']):
        order = np.argsort( PathTravelTimes[iclass]['DepartureTime'] )
        PathTravelTimes[iclass]['DepartureTime'] = np.array(PathTravelTimes[iclass]['DepartureTime'])[order]
        PathTravelTimes[iclass]['TravelTime'] = np.array(PathTravelTimes[iclass]['TravelTime'])[order]
    # ...
    return PathTravelTimes


def is_a_path_included_in_the_vehicle_path( VehiclePath, Path ):
    '''test if a given path is included in the real path a vehicle'''
    # ...
    boolean = True
    ind_beg = -1
    ind_end = -1
    # ...
    if Path[0] in VehiclePath:
        ind_beg = VehiclePath.index(Path[0])
        ind_end = ind_beg + len(Path) #VehiclePath.index(Path[-1])
        boolean = Path == VehiclePath[ind_beg:ind_end]
    else:
        boolean = False
    # ...
    return (boolean, ind_beg, ind_end)


# =============================================================================
# Plot functions on network
# =============================================================================


def plot_network( Simulation, color = (0, 0.2, 0.8), linewidth = 2, bool_linkid = True, bool_nodeid = True, new = True ):
    '''Function to plot the nework'''
    # ...
    if new:
        plt.rc('font', family='Cambria', size = 10, style = 'normal', weight = 'light')
        plt.figure() #plt.figure( figsize=(8,6), facecolor='w' )
    # ...
    plt.title("Network")
    plt.xlabel("")
    plt.ylabel("")
    plt.gca().get_xaxis().set_visible(False)
    plt.gca().get_yaxis().set_visible(False)
    #plt.axis('equal')
    plt.gca().set_aspect('equal', adjustable='box')
    # ...
    for linkid in list( Simulation["Links"] ):
        plt.plot( Simulation["Links"][linkid]["Points"][0], Simulation["Links"][linkid]["Points"][1],\
                 color = color, linewidth = linewidth )
    # ...
    if bool_linkid:
        LinkStyle = dict(boxstyle="square", ec=color, fc=(1, 1, 1) )
        for linkid in list( Simulation["Links"] ):
            coord = np.median(Simulation["Links"][linkid]["Points"],axis=1)
            plt.text(coord[0],coord[1],str(linkid),ha="center", va="center", bbox=LinkStyle )
    # ...
    if bool_nodeid:
        NodeStyle = dict(boxstyle="square", ec=color, fc=color )
        for nodeid in list( Simulation["Nodes"] ):
            coord = node_coord( Simulation, nodeid )
            plt.text(coord[0],coord[1],str(nodeid),ha="center", va="center", bbox=NodeStyle, color=(1, 1, 1) )
    # ...
    # axis equal
    plt.show()
    return True


def plot_trafficolor_on_network( Simulation, Statistics, width = 'constant' ):
    # ...
    '''Function to plot a classical trafficolor on the network, with flow = width, speed = color'''
    plt.rc('font', family='Cambria', size = 10, style = 'normal', weight = 'light')
    plt.figure( figsize=(8,6), facecolor='w' )
    plt.title("Trafficolor on the network")
    plt.xlabel("")
    plt.ylabel("")
    # ...
    for ilink in list( Simulation["Links"] ):
        if width == 'constant':
            LineWidth = 3
        else:
            LineWidth = 1 + np.floor((1/500)*np.max(Statistics[ilink]["Flows"]))
        # ...
        IndicColor = np.min(Statistics[ilink]["Speeds"]) / (3.6*Simulation["Links"][ilink]["Speed"])
        if IndicColor>0.95:
            Color = (0, 0.8, 0)
        elif IndicColor>0.8:
            Color = (0.2, 1, 0.2)
        elif IndicColor>0.5:
            Color = (0.8, 0.6, 0)
        elif IndicColor>0.25:
            Color = (0.8, 0.6, 0)
        else:
            Color = (0.5, 0, 0)
        plt.plot( Simulation["Links"][ilink]["Points"][0], Simulation["Links"][ilink]["Points"][1],\
                 color = Color, linewidth = LineWidth )
        plt.gca().set_aspect('equal')
    # ...
    return True


# =============================================================================
# Plot functions on graphics
# =============================================================================


def subplot_number(n):
    '''define good number of lines and columns for a subplot of n plots'''
    # ...
    if n in [0,1] :   lig = 1; col = 1
    elif n == 2 :     lig = 1; col = 2
    elif n == 3 :     lig = 1; col = 3
    elif n == 4 :     lig = 2; col = 2
    elif n in [5,6] : lig = 2; col = 3
    elif n in [7,8] : lig = 2; col = 4
    elif n == 9 :     lig = 3; col = 3
    else: #lig = int(np.sqrt(n)); col = int(n / lig) + 1
        col = int(np.sqrt(n))
        if col * col < n: col += 1
        lig = int(n/col)
        if col * lig < n: lig += 1
    # ...
    return (lig,col)


def plot_flow_speed_on_link( Statistics, ilink ):
    '''Function to plot flow-speed diagram on a link'''
    # ...
    # Generate both y-axis
    fig, ax1 = plt.subplots()
    ax1.set_title("Flow-speed on link " + str(ilink))
    ax2 = ax1.twinx()
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Flow [veh/h]') #, color='b')
    ax2.set_ylabel('Speed [km/h]') #, color='r')
    # ...
    # Plot curves
    x = Statistics[ilink]["Times"]
    y1 = Statistics[ilink]["Flows"]
    y1 = Statistics[ilink]["Flows"]
    y1bis = Statistics[ilink]["InFlows"]
    y1ter = Statistics[ilink]["Demand"]
    y2 = Statistics[ilink]["Speeds"]

    # ...
    ax2.plot(x, y2, 'r--')
    ax2.set_ylim([0, 1.4 * 3.6 * Statistics[ilink]["Length"] / Statistics[ilink]["FreeTravelTime"]])
    # ...
    ax1.plot(x[[0,-1]], Statistics[ilink]["Capacity"] * np.ones(2), 'k-')
    ax1.plot(x, y1, 'b-')
    ax1.plot(x, y1bis, 'c-')
    ax1.plot(x, y1ter, 'g:')
    ax1.plot(np.nan,np.nan,'r--')
    # ...
    # legend
    ax1.legend(['capacity','outflow','inflow','demand','speed'])
    # ...
    plt.show()
    return True


def plot_cvc_on_link( Statistics, ilink ):
    '''Function to plot entry and exit cumulative count curves on a link'''
    # ...
    # Generate both y-axis
    plt.figure()
    plt.title("Cumulative count curves on link " + str(ilink))
    plt.xlabel('Time [s]')
    plt.ylabel('N curves [veh]')
    # ...
    plt.plot(Statistics[ilink]["DepartureTimes"], range(len(Statistics[ilink]["DepartureTimes"])))
    plt.plot(Statistics[ilink]["ArrivalTimes"], range(len(Statistics[ilink]["ArrivalTimes"])))
    # ...
    plt.legend(['departures from link begining','arrivals to link end'])
    # ...
    return True


def plot_mean_trajectories_on_link( Statistics, ilink ):
    '''Function to plot the mean vehicule trajectories on a link'''
    # ...
    # Generate both y-axis
    plt.figure()
    plt.title("Vehicle trajectories on link " + str(ilink))
    plt.xlabel('Time [s]')
    plt.ylabel('Position [m]')
    # ...
    x = np.array([])
    t = np.array([])
    for iveh in range(len(Statistics[ilink]["DepartureTimes"])):
        x_tmp = np.array([0,Statistics[ilink]["Length"],np.nan])
        t_tmp = np.array([Statistics[ilink]["DepartureTimes"][iveh], Statistics[ilink]["ArrivalTimes"][iveh],np.nan])
        x = np.concatenate((x,x_tmp))
        t = np.concatenate((t,t_tmp))
    plt.plot(t,x,'k-')
    # ...
    return True


def plot_travel_times_on_path( Simulation, Path, PathTravelTimes = None, bool_network = False ):
    '''Function to plot the travel times of all the vehicle classes on a given path'''
    if PathTravelTimes == None:
        PathTravelTimes = compute_travel_times_on_path( Simulation, Path )
    # ...
    plt.figure()
    # ...
    if bool_network:
        plt.subplot(1,2,1)
        plot_network( Simulation, color = (0.5, 0.5, 0.5), linewidth = 1, bool_linkid = False, bool_nodeid = False, new = False )
        for linkid in Path:
            plt.plot( Simulation["Links"][linkid]["Points"][0], Simulation["Links"][linkid]["Points"][1],\
            color = (.82, .37, .37), linewidth = 3 )
        plt.plot( Simulation["Links"][Path[0]]["Points"][0,0], Simulation["Links"][Path[0]]["Points"][1,0] ,'.', color='lime')
        plt.plot( Simulation["Links"][Path[-1]]["Points"][0,-1], Simulation["Links"][Path[-1]]["Points"][1,-1],'r.')
        # ...
        plt.subplots_adjust(wspace = 0.5)
        plt.subplot(1,2,2)
    # ...
    plt.title("Vehicle class comparison on path " + ', '.join(str(ilink) for ilink in Path))
    plt.xlabel('Departure time [s]')
    plt.ylabel('Travel Time [s]')
    # ...

    for iclass in list(Simulation['VehicleClass']):
        plt.plot( PathTravelTimes[iclass]['DepartureTime'], PathTravelTimes[iclass]['TravelTime'], '.' )
    # ...
    VehicleClass = [Simulation['VehicleClass'][iclass]['Name'] for iclass in list(Simulation['VehicleClass'])]
    plt.legend(VehicleClass)
    # ...
    iclass = list(Simulation['VehicleClass'])[0]
    plt.plot(np.min(np.min(PathTravelTimes[iclass]['DepartureTime'])),0,'w.')
    plt.plot(np.min(np.min(PathTravelTimes[iclass]['DepartureTime'])),2*np.min(PathTravelTimes[iclass]['TravelTime']),'w.')
    # ...
    plt.show()
    return True


def plot_node_analysis( NodeEvent, remove_shadow=1 ):
    '''Function to graphically plot passage times of vehicles at a node'''
    # ...
    NumIns = NodeEvent['Info']['NumIns']
    NumOuts = NodeEvent['Info']['NumOuts']
    nodeid = NodeEvent['Info']['ID']
    plt.figure()
    # ...
    for iin in range(NumIns-remove_shadow):
        plt.subplot(2,NumIns-remove_shadow,iin+1)
        plt.title('incoming '+str(iin)+' of node '+str(nodeid)+' : link '+str(NodeEvent['In'][iin]['LinkID']))
        plt.plot( NodeEvent['In'][iin]['Times'], NodeEvent['In'][iin]['Flow'], 'b.-')
        plt.plot( NodeEvent['In'][iin]['Times'][[0,-1]], NodeEvent['In'][iin]['Capacity']*np.ones(2), 'k:')
    # ...
    for out in range(NumOuts-remove_shadow):
        plt.subplot(2,NumOuts-remove_shadow,NumOuts-remove_shadow+out+1)
        plt.title('outgoing '+str(out)+' of node '+str(nodeid)+' : link '+str(NodeEvent['Out'][out]['LinkID']))
        plt.plot( NodeEvent['Out'][out]['Times'], NodeEvent['Out'][out]['Flow'], 'r.-')
        plt.plot( NodeEvent['Out'][out]['Times'][[0,-1]], NodeEvent['Out'][out]['Capacity']*np.ones(2), 'k:')
    # ...
    plt.show()
    return True


# =============================================================================
# Applying functions
# =============================================================================


if __name__=='__main__':
    # reinitialisation of figures
    plt.close("all")

    # loading a Simulation.npy
    Simulation = np.load('Donnees/simulation.npy', allow_pickle=True).item(0)

    # computation of all the travel times on links of network
    TravelTimes = compute_travel_times_on_links( Simulation )

    # Function to compute main statistics of flows on links of the network
    Statistics = compute_stats_on_links( Simulation, TravelTimes )

    # Plotting network
    plot_network( Simulation )

    # choice of a specific link or node for analyses
    linkid = list(Simulation['Links'])[0]
    NumIns = [Simulation['Nodes'][nodeid]['NumIncomingLinks'] for nodeid in list(Simulation['Nodes'])]
    NumOuts = [Simulation['Nodes'][nodeid]['NumOutgoingLinks'] for nodeid in list(Simulation['Nodes'])]
    nodeid = np.intersect1d( np.where(np.array(NumIns)>0)[0],  np.where(np.array(NumOuts)>0)[0] )
    if len(nodeid)==0: nodeid = -1
    else: nodeid = nodeid[-1]; nodeid = list(Simulation['Nodes'])[nodeid]
    nodeid = 1

    if  True:
        # Plotting trafficolor on the network
        plot_trafficolor_on_network( Simulation, Statistics )

    # Plotting flow-speed diagram on a link
    plot_flow_speed_on_link( Statistics, linkid )

    # Plotting cumulative count curves on a link
    plot_cvc_on_link( Statistics, linkid )

    # trajectories on a link
    #plot_mean_trajectories_on_link( Statistics, linkid )

    # plotting informations on a node
    NodeEvent = node_info( Simulation, nodeid )
    #plot_node_analysis( NodeEvent )

    #♥ traveil times on a path
    Path = Simulation['Routes'][4]['Path']
    plot_travel_times_on_path( Simulation, Path, bool_network=True )
