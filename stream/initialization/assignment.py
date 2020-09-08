from .routes import getRoutes
import random
import numpy as np


def assignment(Simulation, When='initialization'):

    print("Original assignment = shortest path...")

    # NOTE : Demand [period, type, origin, destination, number of vehicles]
    #                    0      1    2           3               4

    # --------- Creation of input dict for route calculation
    inputDict = {}
    for key in ["Links", "Nodes", "Entries", "Exits", "VehicleClass"]:
        inputDict.update({key: Simulation[key]})

    # --------- Routes calculation
    Simulation["Routes"] = getRoutes(inputDict)

    # --------- demand Validation
    Simulation["Demand"] = validation_of_demand(Simulation["Demand"],
                                                Simulation["Routes"])

    # ---- Vehicle Assignment
    Simulation["Vehicles"], Simulation["tmp"]["vehArray"] = first_vehicle_assignment(Simulation["Routes"],
                                                                                     Simulation["Demand"],
                                                                                     Simulation["Periods"],
                                                                                     Simulation["Nodes"])
    return (Simulation)


def first_vehicle_assignment(Routes, Demand, Periods, Nodes):
    # init of array of route id - entryid - exitid
    routeArrays = {vehClass: np.array([[routeID, Routes[vehClass][routeID]["EntryID"],
                                        Routes[vehClass][routeID]["ExitID"]] for routeID in list(Routes[vehClass].keys())]) for vehClass in Routes.keys()}

    # Change demand to not include zero flows
    Demand = Demand[np.where(Demand[:, 4] != 0)[0], :]

    # Initialisation of the vehicles dict
    Vehicles = {}
    vehArray = []
    # For each entry
    for entry in np.unique(Demand[:, 2]):
        duration = Periods[2]['start'] - Periods[1]['start']
        d_O = Demand[np.where(Demand[:, 2] == entry)[0], :]
        for per in np.unique(Demand[:, 0]):
            start = Periods[per]['start']
            # Get current id
            currID = len(Vehicles) + 1
            d_OP = d_O[np.where(d_O[:, 0] == per)[0], :]
            # Here the demand is for ONE origin and for ONE Period
            # Total number of vehicles
            nTotal = sum(d_OP[:, 4])/3600 * duration
            if nTotal == 0:
                continue
            # Mean headway
            hMean = duration / nTotal
            currTime = start + hMean
            while currTime <= start + duration:
                # Vehicle initialization
                vehicle = {}
                # information of vehicle
                line = d_OP[findLineByCumProb(d_OP[:, 4]), [1, 3]]
                # Which vehicle class ?
                currVehClass = int(line[0])
                # determination of the RouteID
                routeLine = findLineCorrespondingToInOut(
                    routeArrays[currVehClass][:, [1, 2]], entry, line[1])
                # Security condition
                if len(routeLine) != 0:
                    routeID = routeArrays[currVehClass][routeLine, 0][0]
                    nextLinkID = np.where(
                        Nodes[entry]["OutgoingLinksID"] == Routes[currVehClass][routeID]["Path"][0])[0][0]
                    vehicle.update({
                        "EntryID": int(entry),
                        "ExitID": int(line[1]),
                        "VehicleClass": currVehClass,
                        "NetworkArrivalTime": currTime,
                        "IDRoute": routeID,
                        "Path": Routes[currVehClass][routeID]["Path"],
                        "NodeList": Routes[currVehClass][routeID]["NodeList"],
                        "NodeTimes": np.zeros(len(Routes[currVehClass][routeID]["NodeList"])),
                        "CurrentNode": -1,
                        "RealPath": []
                    })
                    vehArray.append(
                        [int(currID), int(entry), currTime, nextLinkID])
                    Vehicles.update({currID: vehicle})
                    currID += 1
                else:
                    print("WARNING : no path between entry " +
                          str(entry) + " and exit " + str(line[1]) + " for vehicles of type " + str(currVehClass))
                currTime = currTime + hMean
    print(str(len(Vehicles)) + " vehicles created...")
    # np.save('vehArray',np.array(vehArray))
    return (Vehicles, np.array(vehArray))


def validation_of_demand(demandArray, Routes):

    # init of array of route id - entryid - exitid
    routeArrays = {vehClass: np.array([[routeID, Routes[vehClass][routeID]["EntryID"], Routes[vehClass][routeID]["ExitID"]]
                                       for routeID in list(Routes[vehClass].keys())]) for vehClass in Routes.keys()}

    for vehClass in Routes.keys():
        routeArray = routeArrays[vehClass]
        for entryID in np.unique(demandArray[:, 2]):
            for exitID in np.unique(demandArray[:, 3]):
                if len(findLineCorrespondingToInOut(routeArray[:, [1, 2]], entryID, exitID)) == 0:
                    demandLines = findLineCorrespondingToInOutAndVehicleClass(
                        demandArray[:, [1, 2, 3]], entryID, exitID, vehClass)
                    if np.sum(demandArray[demandLines, 4]) != 0:
                        # The route does not exist and there is a non null demand
                        print("Warning : no path between entry " +
                              str(entryID) + " and exit " + str(exitID) + "for vehicle of class " + str(vehClass))
                        print(
                            "Every flow between these two extrems are set to zero...")
                        # set the demand Lines to 0
                        if len(demandLines) != 0:
                            demandArray[demandLines, 4] = 0
    return demandArray

##############################################################################
# small functions


def findLineByCumProb(arr):
    # Make cum sum
    arr2 = np.cumsum(arr)
    # RNG
    rng = np.floor(random.random()*arr2[-1])
    # Looping over the lines
    for i in range(arr.shape[0]):
        if rng <= arr2[i]:
            break
    return i


def findLineCorrespondingToInOut(InOutArray, entry, exit):
    return np.where(np.logical_and(InOutArray[:, 0] == entry, InOutArray[:, 1] == exit))[0]


def findLineCorrespondingToInOutAndVehicleClass(InOutClassArray, entry, exit, vehClass):
    return np.where(np.logical_and.reduce((InOutClassArray[:, 1] == entry, InOutClassArray[:, 2] == exit, InOutClassArray[:, 0] == vehClass)))[0]
