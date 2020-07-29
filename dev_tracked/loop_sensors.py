# -*- coding: utf-8 -*-

#imports
import numpy as np
from stream.analysis.analysis import plot_network
from stream.analysis.analysis import plot_cvc_on_link
from stream.main import run_simulation_from_inputs

from stream.analysis.diagXT import calcCVCInter

import matplotlib.pyplot as plt


# Ouverture d'un fichier de simulation
Simulation = np.load("../example/outputs.npy",allow_pickle=True).item()

"""
We set a simple loop sensor in the link number 5 at 100m after the start with
a 6 minutes time step and starting at the begining of the simulation
"""
Simulation["Sensors"] = {
    1 : {
        "Type" : "simple_loop",
        "Args" : {
            "Link" : 5,
            "Offset": 100,
            "Start": Simulation["General"]["SimulationDuration"][0],
            "Step" : 60 # = 6 minutes
            },
        "Name" : "link5_100m"
        },
    2 : {
        "Type" : "double_loop",
        "Args" : {
            "Link" : 5,
            "Offset": 100,
            "Start": Simulation["General"]["SimulationDuration"][0],
            "Step" : 60, # = 6 minutes,
            "Size": 1
            },
        "Name" : "link5_100m_double"
        }
    }

def get_sensors_outputs(Simulation):
    outputs = {}
    for sensorID in Simulation["Sensors"]:
        sensor = Simulation["Sensors"][sensorID]
        if sensor["Type"] == "simple_loop":
            outputs[sensorID] = get_simple_loop_outputs(Simulation, sensor)
        elif sensor["Type"] == "double_loop":
            outputs[sensorID] = get_double_loop_outputs(Simulation, sensor)
    return outputs

def get_simple_loop_outputs(Simulation, sensor):
    # Unpack the sensor
    linkID = sensor["Args"]["Link"]
    offset = sensor["Args"]["Offset"]
    start = sensor["Args"]["Start"]
    step = sensor["Args"]["Step"]
    
    #Unpack the link info
    # Get the FD
    FD = Simulation["Links"][linkID]["FD"]
    #Get the length
    length = Simulation["Links"][linkID]["Length"]
    
    # Get the CVC a the incoming node
    nodeUpID = Simulation["Links"][linkID]["NodeUpID"]
    indexOfCurrentLinkWithinNodeUp = list(Simulation["Nodes"][nodeUpID]["OutgoingLinksID"]).index(linkID)
    CVCin = Simulation["Events"][nodeUpID]["Exits"][indexOfCurrentLinkWithinNodeUp]["Time"]
    
    # Get the CVC a the outgoing node
    nodeDownID = Simulation["Links"][linkID]["NodeDownID"]
    indexOfCurrentLinkWithinNodeDown = list(Simulation["Nodes"][nodeDownID]["IncomingLinksID"]).index(linkID)
    CVCout = []
    for outgoingLinkIndex in Simulation["Events"][nodeDownID]["Exits"]:
        allInfo =  Simulation["Events"][nodeDownID]["Exits"][outgoingLinkIndex]
        for i in range(allInfo["Time"].shape[0]):
            if allInfo["PreviousLinkID"][i] == indexOfCurrentLinkWithinNodeDown:
                CVCout.append(allInfo["Time"][i])
    CVCout.sort()
    CVCout = np.array(CVCout)
    
    # cut the vehicles that have not exited the link
    CVCin = CVCin[0:len(CVCout)]
    CVCout = np.concatenate((np.array([-np.inf]), CVCout, np.array([np.inf])))
    CVC = calcCVCInter(CVCin, CVCout, offset, length, FD["u"], FD["w"], FD["kx"])
    
    # Create time steps vect
    time_vect = np.arange(start = start, step = step, stop = Simulation["General"]["SimulationDuration"][1])
    q_vect = np.zeros(time_vect.shape)
    
    for j in range(time_vect.shape[0] - 1):
        # detect vehicles in time steps
        vehsInFromIn = np.where(np.logical_and(CVC >= time_vect[j], CVC <= time_vect[j+1]))[0]
        q_vect[j] = vehsInFromIn.shape[0]/step
        
    outputs = {
        "Times" : time_vect[0:-1],
        "Flows" : q_vect[0:-1]*3600.0
        }
    
    return outputs

def get_double_loop_outputs(Simulation, sensor):
    # Unpack the sensor
    linkID = sensor["Args"]["Link"]
    offset = sensor["Args"]["Offset"]
    start = sensor["Args"]["Start"]
    step = sensor["Args"]["Step"]
    size = sensor["Args"]["Size"]
    
    #Unpack the link info
    # Get the FD
    FD = Simulation["Links"][linkID]["FD"]
    #Get the length
    length = Simulation["Links"][linkID]["Length"]
    
    # Get the CVC a the incoming node
    nodeUpID = Simulation["Links"][linkID]["NodeUpID"]
    indexOfCurrentLinkWithinNodeUp = list(Simulation["Nodes"][nodeUpID]["OutgoingLinksID"]).index(linkID)
    CVCin = Simulation["Events"][nodeUpID]["Exits"][indexOfCurrentLinkWithinNodeUp]["Time"]
    
    # Get the CVC a the outgoing node
    nodeDownID = Simulation["Links"][linkID]["NodeDownID"]
    indexOfCurrentLinkWithinNodeDown = list(Simulation["Nodes"][nodeDownID]["IncomingLinksID"]).index(linkID)
    CVCout = []
    for outgoingLinkIndex in Simulation["Events"][nodeDownID]["Exits"]:
        allInfo =  Simulation["Events"][nodeDownID]["Exits"][outgoingLinkIndex]
        for i in range(allInfo["Time"].shape[0]):
            if allInfo["PreviousLinkID"][i] == indexOfCurrentLinkWithinNodeDown:
                CVCout.append(allInfo["Time"][i])
    CVCout.sort()
    CVCout = np.array(CVCout)
    
    # cut the vehicles that have not exited the link
    CVCin = CVCin[0:len(CVCout)]
    CVCout = np.concatenate((np.array([-np.inf]), CVCout, np.array([np.inf])))
    CVC1 = calcCVCInter(CVCin, CVCout, offset - size/2, length, FD["u"], FD["w"], FD["kx"])
    CVC2 = calcCVCInter(CVCin, CVCout, offset + size/2, length, FD["u"], FD["w"], FD["kx"])
    
     # Create time steps vect
    time_vect = np.arange(start = start, step = step, stop = Simulation["General"]["SimulationDuration"][1])
    q_vect = np.zeros(time_vect.shape)
    k_vect = np.zeros(time_vect.shape)
    v_vect = np.zeros(time_vect.shape)
    
    for j in range(time_vect.shape[0] - 1):
        # init the total passed time and distance travelled in cell
        PT = 0
        DT = 0
        #...
        # detect vehicles in cell
        vehsInFromIn = np.where(np.logical_and(CVC1 >= time_vect[j], CVC1 <= time_vect[j+1]))[0]
        vehsInFromOut = np.where(np.logical_and(CVC2 >= time_vect[j], CVC2 <= time_vect[j+1]))[0]
        vehsIn = np.union1d(vehsInFromIn, vehsInFromOut)
         # Looping all over the vehicles in cell
        timesAtPos1 = CVC1[vehsIn]
        timesAtPos2 = CVC2[vehsIn]
        for veh in  range(len(vehsIn)):
            #...
            # if the vehicle pass the entire cell during the period
            if timesAtPos1[veh] >= time_vect[j] and timesAtPos2[veh] <= time_vect[j+1]:
                # Distance travelled
                DT += size
                # Passed time
                PT += timesAtPos2[veh] - timesAtPos1[veh]
            #...
            # if the trajectory of the vehicle is not contained in the cell
            else:
                speed = size/(timesAtPos2[veh] - timesAtPos1[veh])
                #...
                # vehicles not present at the begining of the period
                if timesAtPos1[veh] >= time_vect[j]:
                    pt = time_vect[j+1] - timesAtPos1[veh]
                #...
                # vehicles already present at the beginig of the period
                else:
                    pt = timesAtPos2[veh] - time_vect[j]
                PT += pt
                DT += speed * pt
        # Eddie's formulas
        q_vect[j] = DT/(size*step)
        k_vect[j] = PT/(size*step)
        v_vect[j] = DT/PT
    
    outputs = {
        "Times" : time_vect[0:-1],
        "Flows" : q_vect[0:-1]*3600.0,
        "Densities": k_vect[0:-1]*1000.,
        "Speeds": v_vect[0:-1]*3.6
        }
    
    return outputs

outputs = get_sensors_outputs(Simulation)







