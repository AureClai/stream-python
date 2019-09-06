# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 10:09:02 2019

@author: aurelien.clairais

Script for analyzing the Simulation with XT diagramms on paths
"""

#...
# import dependancies
import numpy as np
import os
import sys

#...
# Functions
#...
def getWhoHasSub(Simulation):
    hasSubLinks = []
    for link in list(Simulation["Links"]):
        if Simulation["Links"][link]["AssociatedLink"]!=None:
            hasSubLinks.append(link)
    return hasSubLinks

def getWhoIsSub(Simulation):
    isSubLinks = []
    for link in list(Simulation["Links"]):
        if Simulation["Links"][link]["AssociatedLink"]!=None:
            isSubLinks.append(Simulation["Links"][link]["AssociatedLink"])
    return isSubLinks

def calcCVCInter(CVCin, CVCout, x, L, u, w, kx):
    """
    Function to calculate the internal CVC on a link at position x
    """
    #...
    if abs(x) < 1e-6:
        return CVCin
    if abs(x - L) < 1e-6:
        return CVCout[1:-1]
    #...
    # demand
    CVCd = CVCin + x / u
    #...
    # supply
    # list of index
    idsCVCout = np.arange(len(CVCout))
    idsCVCouto = np.maximum(np.arange(len(CVCout)) - kx * (L - x),np.zeros(len(CVCout)))
    CVCo = np.interp(idsCVCouto, idsCVCout, CVCout) + (L-x)/w
    CVCo[np.isnan(CVCo)] = -np.inf

    return np.maximum(CVCd, CVCo[1:-1])
#...
def calcXTOnLink(Simulation, link, dt, dx):
    """
    Function to calculate the aggregated variables on a specified link
    """
    print(link)
    L = Simulation["Links"][link]["Length"]
    u = Simulation["Links"][link]["FD"]["u"]
    w = Simulation["Links"][link]["FD"]["w"]
    kx = Simulation["Links"][link]["FD"]["kx"] * Simulation["Links"][link]["NumLanes"]
    FD = {'u' : u , 'C' : kx * u * w / (u+w), 'kx' : kx}
    #...
    # get the incoming and outgoing nodes
    nodeInID = Simulation["Links"][link]["NodeUpID"]
    nodeOutID = Simulation["Links"][link]["NodeDownID"]
    #...
    CVCin = np.array([])
    CVCout = np.array([])
    #...
    # in
    linkIndex = np.where(Simulation["Nodes"][nodeInID]["OutgoingLinksID"] == link)[0][0]
    CVCin = Simulation["Events"][nodeInID]["Exits"][linkIndex]["Time"]
    CVCin.sort()

    #...
    # out
    linkIndex = np.where(Simulation["Nodes"][nodeOutID]["IncomingLinksID"] == link)[0][0]
    for _out in list(Simulation["Events"][nodeOutID]["Exits"]):
        goodindixes = np.where( Simulation["Events"][nodeOutID]["Exits"][_out]["PreviousLinkID"] == linkIndex)[0]
        CVCout = np.concatenate((CVCout, Simulation["Events"][nodeOutID]["Exits"][_out]["Time"][goodindixes]))
    CVCout.sort()


    #...
    # cut the vehicles that have not exited the link
    CVCin = CVCin[0:len(CVCout)]
    CVCout = np.concatenate((np.array([-np.inf]), CVCout, np.array([np.inf])))
    #...
    #Get all the CVCs
    CVCs = CVCin
    x_vect = np.concatenate((np.arange(start = 0, step = dx, stop = L), np.array([L])))
    for x in x_vect[1:]:
        # get the CVC corresponding to x
        CVCs = np.vstack((CVCs, calcCVCInter(CVCin,CVCout, x, L, u, w, kx)))

    #...
    # calculate the cells
    t_start = Simulation["General"]["SimulationDuration"][0]
    t_end = Simulation["General"]["SimulationDuration"][1]
    t_vect = np.concatenate((np.arange(start = t_start, step = dt, stop = t_end), np.array([t_end])))
    dx_vect = x_vect[1:] - x_vect[0:-1]
    dx_vect = dx_vect.reshape((len(dx_vect), 1))
    dt_vect = t_vect[1:] - t_vect[0:-1]
    dt_vect = dt_vect.reshape((1, len(dt_vect)))
    # init the cells
    cellsArea = np.dot(dx_vect, dt_vect) # area
    cellsPT = np.zeros(cellsArea.shape) # passed time
    cellsDT = np.zeros(cellsArea.shape) # distance traveled

    #...
    # looping all over the cells
    for i in range(cellsArea.shape[0]):
        for j in range(cellsArea.shape[1]):

            #...
            # init the total passed time and distance travelled in cell
            PT = 0
            DT = 0
            #...
            # detect vehicles in cell
            vehsInFromIn = np.where(np.logical_and(CVCs[i,:] >= t_vect[j], CVCs[i,:] <= t_vect[j+1]))[0]
            vehsInFromOut = np.where(np.logical_and(CVCs[i+1,:] >= t_vect[j], CVCs[i+1,:] <= t_vect[j+1]))[0]
            vehsIn = np.union1d(vehsInFromIn, vehsInFromOut)
            #...
            # Looping all over the vehicles in cell
            CVCin = CVCs[i, vehsIn]
            CVCout = CVCs[i+1, vehsIn]
            for veh in  range(len(vehsIn)):
                #...
                # if the vehicle pass the entire cell during the period
                if CVCin[veh] >= t_vect[j] and CVCout[veh] <= t_vect[j+1]:
                    DT += dx_vect[i]
                    PT += CVCout[veh] - CVCin[veh]
                #...
                # if the trajectory of the vehicle is not contained in the cell
                else:
                    speed = dx_vect[i]/(CVCout[veh] - CVCin[veh])
                    #...
                    # vehicles not present at the vegining of the period
                    if CVCin[veh] >= t_vect[j]:
                        pt = t_vect[j+1] - CVCin[veh]
                    #...
                    # vehicles already present at the beginig of the period
                    else:
                        pt = CVCout[veh] - t_vect[j]
                    PT += pt
                    DT += speed * pt
            # update the cells values
            cellsPT[i,j] = PT
            cellsDT[i,j] = DT

    # Eddie's formulas
    cellsQ = cellsDT/cellsArea
    cellsK = cellsPT/cellsArea
    cellsV = cellsQ/cellsK
    cellsV[np.isnan(cellsV)] = u

    cellsX = np.transpose(np.tile(x_vect[0:-1], [dt_vect.shape[1], 1]))
    cellsT = np.tile(t_vect[0:-1], [dx_vect.shape[0], 1])

    return (cellsT, cellsX, cellsQ, cellsK, cellsV, FD)

#...
def calcXTOnAllLinks(Simulation, dx, dt):
    """
    Function to calculate the aggregated variables on all links in Simulation
    """
    #...
    # init
    diagsXT = {}
    hasSubLinks = getWhoHasSub(Simulation)
    isSubLinks = getWhoIsSub(Simulation)
    for link in Simulation["Links"]:
        print(link)
        #...
        hasSub = False
        isMain = True
        if link in hasSubLinks:
            hasSub = True
        if link in isSubLinks:
            isMain = False
        #...
        cellsT, cellsX, cellsQ, cellsK, cellsV, FD = calcXTOnLink(Simulation, link, dt, dx)
        diagsXT.update({link : {"X" : cellsX,
                               "T" : cellsT,
                               "Q" : cellsQ,
                               "K" : cellsK,
                               "V" : cellsV,
                               "FD" : FD,
                               "Length" : Simulation["Links"][link]["Length"],
                               "hasSub" : hasSub,
                               "isMain" : isMain}})
    return diagsXT

#...
def calcXTOnPath(Simulation, path, dx, dt):
    """
    Function to calculate the aggregated variables on all links in specified
    path
    """
    #...
    # init
    diagsXT = {}
    for link in path:
        print(link)
        cellsT, cellsX, cellsQ, cellsK, cellsV, FD = calcXTOnLink(Simulation, link, dt, dx)
        diagsXT.update({link : {"X" : cellsX,
                               "T" : cellsT,
                               "Q" : cellsQ,
                               "K" : cellsK,
                               "V" : cellsV,
                               "FD": FD}})
    return diagsXT

if __name__ == '__main__':
    #...
    #loading simulation
    try:
        config = sys.argv[1:]
        file = config[0]
        name = config[1]
        dx = int(config[2])
        dt = int(config[3])
        Simulation = np.load(file).item(0)
        diagsXT =  calcXTOnAllLinks(Simulation, dx,dt)
        dirPath = os.path.dirname(file)
        namepath = os.path.join(dirPath, name)
    except Exception as e:
        print(e)
        input('ERROR')
    np.save(namepath, diagsXT)
    print("Saved in :")
    print(namepath)
    input('Hit <Return> to continue')
