# IMPORTS
import copy
import numpy as np

from .validate_and_complete_scenario import update_link_DF


def initialize_simulation(Simulation):  # , User):
    print("Original initialization...")
    '''Main function'''
    # ...
    #Links, Nodes, VehicleClass, General, Entries, Exits, Routes, Periods = inputs_to_variables(Inputs)
    # ...
    # ---- (1) Initialisation of the dynamic variables of nodes and links
    Simulation["Events"] = initial_Events(
        Simulation["Nodes"], Simulation["Links"])
    # ...
    # ---- (2) Initialisation of the arrivals at entries
    Simulation["Events"] = initial_arrivals(
        Simulation["Entries"], Simulation["Events"], Simulation["tmp"]["vehArray"])
    # ...
    # --- (3) Initialization of the actualization times in the simulation
    Simulation["General"] = complete_general(Simulation["General"])
    # ...
    # ---- (4) Initialization of regulations
    Simulation = initialize_regulations(Simulation)
    # ...
    # ---- (5) Add action
    Simulation = initialize_actions(Simulation)
    # ...
    del Simulation["tmp"]
    return (Simulation)


def initial_Events(Nodes, Links):
    '''initialise the structure for Events'''
    Events = {}
    # ...
    for node in list(Nodes.keys()):
        # init the Arrivals
        Arrivals = {}
        for j in range(Nodes[node]["NumIncomingLinks"] + 1):
            # Arrivals on the nodes
            Arrival = {}
            Arrival.update({"Time": np.zeros(0)})
            Arrival.update({"VehID": np.zeros(0)})
            Arrival.update({"IsExit": np.zeros(0)})
            Arrival.update({"NextLinkID": np.zeros(0)})
            Arrival.update({"Num": 0})
            Arrivals.update({j: Arrival})
        Events.update({node: {"Arrivals": Arrivals}})
        # ...
        # Initialization of Exits
        Exits = {}
        for j in range(Nodes[node]["NumOutgoingLinks"] + 1):
            # Sorties du noeud
            Exit = {}
            Exit.update({"Time": np.zeros(0)})
            Exit.update({"Regime": np.zeros(0)})
            Exit.update({"VehID": np.zeros(0)})
            Exit.update({"PreviousLinkID": np.zeros(0)})
            Exit.update({"Num": 0})
            Exits.update({j: Exit})
        Events[node].update({"Exits": Exits})
        # ...
        # ---- Initial initial_node_supply_time ---
        if len(Nodes[node]["OutgoingLinksID"]) == 0:
            VehiclesNum = 0
        else:
            VehiclesNum = 1 + np.floor(np.max(np.array([Links[link]["Length"] for link in Nodes[node]["OutgoingLinksID"]]) * np.array(
                [Links[link]["NumLanes"] for link in Nodes[node]["OutgoingLinksID"]]) * [Links[link]["FD"]["kx"] for link in Nodes[node]["OutgoingLinksID"]]))
        VehiclesNum = max([VehiclesNum, 1])
        OutgoingLinksNum = 1 + Nodes[node]["NumOutgoingLinks"]
        IncomingLinksNum = 1 + Nodes[node]["NumIncomingLinks"]
        SupplyTimes = {}
        SupplyTimes["Downstream"] = -np.inf * \
            np.ones([int(VehiclesNum), int(OutgoingLinksNum)])
        SupplyTimes["DownCapacity"] = -np.inf * np.ones(int(OutgoingLinksNum))
        SupplyTimes["UpCapacity"] = -np.inf * np.ones(int(IncomingLinksNum))
        Events[node].update({"SupplyTimes": SupplyTimes})
    # ...
    return Events


def initial_arrivals(Entries, Events, vehArray):
    '''initialise arrivals at entries in the Events structure'''
    if len(vehArray) != 0:
        # ...
        for entry in list(Entries):
            subArray = vehArray[np.where(vehArray[:, 1] == entry)[0], :]
            # sorting
            subArray = subArray[subArray[:, 2].argsort()]
            # ...
            Events[entry]["Arrivals"][0]["Time"] = subArray[:, 2]
            Events[entry]["Arrivals"][0]["VehID"] = subArray[:, 0]
            Events[entry]["Arrivals"][0]["IsExit"] = np.zeros(
                subArray.shape[0])
            # np.zeros(subArray.shape[0])
            Events[entry]["Arrivals"][0]["NextLinkID"] = subArray[:, 3]
        # ...
    return Events


def complete_general(General):
    '''complete General dictionary to integrate the save of computational times'''
    # ...
    Computation = {}
    Computation.update({"NumEvent": 0,
                        "NodeEvent": np.array([]),
                        "CurrentSimulationTime": np.array([]),
                        "Time": np.array([]),
                        })
    General.update({"Computation": Computation})
    # ...
    return General


def initialize_regulations(Simulation):
    '''account for regulations and modify Simulation dictioaries'''
    # ...
    for reg in list(Simulation["Regulations"]):
        Regulation = Simulation["Regulations"][reg]
        # ...
        # Adapt the simulation with a managed Lane
        if Regulation['Type'] == 'managed_lane':
            for managedLaneLink in Regulation['Args']['Links']:
                # Creation of a new link
                newLinkID = max(list(Simulation["Links"]))+1
                newLink = copy.deepcopy(Simulation["Links"][managedLaneLink])
                newLink["NumLanes"] = 1
                Simulation["Links"].update({newLinkID: newLink})
                if "Capacity" in list(Regulation['Args'].keys()):
                    newLink["Capacity"] = Regulation['Args']['Capacity']
                    update_link_DF(Simulation["Links"], newLinkID)
                else:
                    Simulation["Links"][newLinkID]["Capacity"] = Simulation["Links"][managedLaneLink]["FD"]["C"]

                # ...
                # Modify the existing link
                NumLanes = Simulation["Links"][managedLaneLink]['NumLanes']
                ratio1 = (NumLanes-1)/NumLanes
                LaneProbability = [ratio1, 1-ratio1]
                LaneProbabilities = [LaneProbability for vehclass in list(
                    Simulation['VehicleClass'])]

                # Capacity
                if "Capacity" in list(Regulation['Args'].keys()):
                    cap = NumLanes * \
                        Simulation["Links"][managedLaneLink]["FD"]["C"] - \
                        Regulation['Args']['Capacity']
                else:
                    cap = (NumLanes-1) * \
                        Simulation["Links"][managedLaneLink]["FD"]["C"]

                Simulation["Links"][managedLaneLink].update({
                    'AssociatedLink': newLinkID,
                    'LaneProbabilities': LaneProbabilities,
                    'NumLanes': (NumLanes-1),
                    'Capacity': cap
                })
                update_link_DF(Simulation["Links"], managedLaneLink)

                # ...
                # Modify the nodes
                nodeup = Simulation["Links"][managedLaneLink]["NodeUpID"]
                Simulation["Nodes"][nodeup]["OutgoingLinksID"] = np.concatenate((
                    Simulation["Nodes"][nodeup]["OutgoingLinksID"], np.array([newLinkID])))
                Simulation["Nodes"][nodeup]["NumOutgoingLinks"] += 1
                # ...
                nodedown = Simulation["Links"][managedLaneLink]["NodeDownID"]
                Simulation["Nodes"][nodedown]["IncomingLinksID"] = np.concatenate((
                    Simulation["Nodes"][nodedown]["IncomingLinksID"], np.array([newLinkID])))
                Simulation["Nodes"][nodedown]["NumIncomingLinks"] += 1
                Simulation["Nodes"][nodedown]["CapacityDrop"] = np.array([0.] *
                                                                         (Simulation["Nodes"][nodedown]["NumIncomingLinks"] + 1))
                Simulation["Nodes"][nodedown].update(recalculateAlphaOD(
                    Simulation["Nodes"][nodedown], Simulation["Links"]))
    # ...
    return Simulation


def initialize_actions(Simulation):
    '''initialize Action dictionary in Simulation'''
    # ...
    # initialize if necessary
    if not "Actions" in list(Simulation):
        Simulation["Actions"] = []
    # ...
    # Display times
    step_time = Simulation["General"]["TimesStepByDefault"]  # sec
    display_times = np.arange(Simulation["General"]["SimulationDuration"][0],
                              Simulation["General"]["SimulationDuration"][1] + 2 * step_time, step_time)
    display_times = display_times - \
        (Simulation["General"]["SimulationDuration"][0] % step_time)
    for disp_time in display_times:
        # ...
        Action = {}
        Action['Time'] = disp_time
        Action['Type'] = 'display_time_simulation'
        Action['Args'] = {}
        Simulation['Actions'].append(Action)
    # ...
    # Managed lanes
    for reg in list(Simulation["Regulations"]):
        Regulation = Simulation["Regulations"][reg]
        if Regulation['Type'] == 'managed_lane':
            for managedLaneLink in Regulation['Args']['Links']:
                activated = False
                for time in Regulation['Args']['Times']:
                    # ....
                    Action = {}
                    Action['Time'] = time
                    if activated:
                        Action['Type'] = 'managed_lane_deactivation'
                        activated = False
                    else:
                        Action['Type'] = 'managed_lane_activation'
                        activated = True
                    Action['Args'] = {
                        'LinkID': managedLaneLink, 'Class': Regulation['Args']['Class'], 'Display': True}
                    Simulation['Actions'].append(Action)
    # ...
    # Sort actions
    Simulation['Actions'] = sortActionsByTime(Simulation["Actions"])
    # ...
    return Simulation


# =============================================================================
# Sub-functions
# =============================================================================


def recalculateAlphaOD(node, Links):
    node.update({"AlphaOD": np.array([])})
    if node["NumIncomingLinks"] >= 1:  # this is a merge
        NumIncomingLanes = [Links[link]["NumLanes"]
                            for link in node["IncomingLinksID"]]
        classic = 1/sum(NumIncomingLanes) * np.array(NumIncomingLanes)
        node.update({"AlphaOD": np.hstack((classic, np.array([0])))})
    if node["NumIncomingLinks"] == 0:
        node["AlphaOD"] = np.array([1.])
    return node


def sortActionsByTime(Actions):
    actionsArray = np.zeros(len(Actions))
    for i, action in enumerate(Actions):
        actionsArray[i] = action["Time"]
        sortedIndexes = np.argsort(actionsArray)
    # ...
    # sorting
    newActions = []
    for i in range(len(sortedIndexes)):
        newActions.append(Actions[sortedIndexes[i]])
    Actions = newActions
    return Actions
