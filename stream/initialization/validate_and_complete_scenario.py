import sys
import numpy as np

# Main function


def validate_and_complete_scenario(Inputs, User=[]):

    print("Original validation of the scenario...")

    Inputs = change_parameters_by_user(Inputs, User)
    Inputs = add_missing_variables(Inputs)

    Inputs["tmp"] = {}

    Inputs["General"] = complete_general(Inputs["General"])
    Inputs["Traffic"], Inputs["VehicleClass"] = complete_by_default_traffic(
        Inputs["Traffic"], Inputs["VehicleClass"])

    Inputs["Links"] = complete_links(
        Inputs["Links"], Inputs["Nodes"], Inputs["Traffic"])
    Inputs["Nodes"] = complete_nodes(
        Inputs["Links"], Inputs["Nodes"], Inputs["Traffic"])
    # Inputs["Signals"] = complete_nodes(Inputs["Signals"], Inputs["General"])
    Inputs["Exits"] = complete_exits(
        Inputs["Nodes"], Inputs["Exits"], Inputs["General"])
    #Inputs["Entries"] = complete_entries(Inputs["Nodes"], Inputs["Links"], Inputs["Entries"], Inputs["Exits"], Inputs["VehicleClass"])
    #Inputs["Routes"] = complete_routes(Inputs["Routes"])
    if 'Signals' in Inputs.keys():
        Inputs['Signals'][0] = {}
    else:
        Inputs['Signals'] = {0: {}}

        # Assignment
        # Regulations
    validation(Inputs["Links"], Inputs["Nodes"],
               Inputs["Entries"], Inputs["Exits"])

    # signal & assignement
    return Inputs

##############################################################################
# Functions

# Function template to enable users to change parameters
# NOT IN USE


def change_parameters_by_user(Inputs, User=[]):

    if len(User) != 0 and ("ChangeParameters" in User["Simulation"].keys()):
        NumberModifications = len(User["Simulation"]["ChangeParameters"])
        for modif in range(NumberModifications):
            STRING = User["Simulation"]["ChangeParameters"][modif]
            if STRING:
                eval(STRING)
                print("Modifying : " + STRING)
    return Inputs

# Add the missing variables to standardize the inputs of the simulation


def add_missing_variables(Inputs):

    if not("Links" in Inputs.keys()):
        Inputs.update({"Links": {}})

    if not("Nodes" in Inputs.keys()):
        Inputs.update({"Nodes": {}})

    if not("Signals" in Inputs.keys()):
        Inputs.update({"Signals": {}})

    if not("Sensors" in Inputs.keys()):
        Inputs.update({"Sensors": {}})

    if not("General" in Inputs.keys()):
        Inputs.update({"General": {}})

    if not("Traffic" in Inputs.keys()):
        Inputs.update({"Traffic": {}})

    if not("VehicleClass" in Inputs.keys()):
        Inputs.update({"VehicleClass": {}})

    if not("Entries" in Inputs.keys()):
        Inputs.update({"Entries": {}})

    if not("Exits" in Inputs.keys()):
        Inputs.update({"Exits": {}})

    if not("Assignment" in Inputs.keys()):
        Inputs.update({"Assignment": {}})

    if not("Routes" in Inputs.keys()):
        Inputs.update({"Routes": {}})

    if not("Regulations" in Inputs.keys()):
        Inputs.update({"Regulations": {}})

    if not("Assimilation" in Inputs.keys()):
        Inputs.update({"Assimilation": {}})

    return Inputs

# Complete the "General" key content to match with the standards


def complete_general(General={}):
    if not(General):
        General["SimulationDuration"] = [0, 60]
        General["SimulationModel"] = 'MesoLWR'
        General["Peloton"] = 1
        General["TimesStepByDefault"] = 360
        # Type of each model component (deterministic vs Stochasticity
        Stochasticity = {}
        Stochasticity["Demand"] = False
        Stochasticity["Vehicle"] = False
        Stochasticity["Assignment"] = False
        Stochasticity["Merge"] = True
        General["Stochasticity"] = Stochasticity
        General["ActiveUpstreamCapacity"] = True
        print("Warning : Simulation duration must be specified")
    else:
        if not("SimulationDuration" in General.keys()):
            General["SimulationDuration"] = [0, 60]
        elif len(General["SimulationDuration"]) == 1:
            General["SimulationDuration"] = [
                0, General["SimulationDuration"][0]]
        if not("SimulationModel" in General.keys()):
            General["SimulationModel"] = "MesoLWR"
        if not("Peloton" in General.keys()):
            General["Peloton"] = 1
        if not("TimesStepByDefault" in General.keys()):
            General["TimesStepByDefault"] = 360
        if not("Stochasticity" in General.keys()):
            Stochasticity = {}
            Stochasticity["Demand"] = False
            Stochasticity["Vehicle"] = False
            Stochasticity["Assignment"] = False
            Stochasticity["Merge"] = True
            General["Stochasticity"] = Stochasticity
        else:
            if not("Demand" in General["Stochasticity"].keys()):
                General["Stochasticity"]["Demand"] = False
            if not("Vehicle" in General["Stochasticity"].keys()):
                General["Stochasticity"]["Vehicle"] = False
            if not("Assignment" in General["Stochasticity"].keys()):
                General["Stochasticity"]["Assignment"] = False
            if not("Merge" in General["Stochasticity"].keys()):
                General["Stochasticity"]["Merge"] = False
        if not("ActiveUpStreamCapacity" in General.keys()):
            General["ActiveUpStreamCapacity"] = False

    return General


# Complete by default traffic if none is provided in the input dict
def complete_by_default_traffic(Traffic={}, VehicleClass={}):
    if not(Traffic):
        # Fundamental diagram by lane
        FD = {}
        FD["u"] = 30
        FD["w"] = 5
        FD["kx"] = 0.2
        FD["C"] = 0.8571428571428571
        Traffic["FD"] = FD

        # Lane-Flow distribution
        LFD_2_lanes = {}
        LFD_2_lanes["values"] = [0.5, 0.5]
        LFD_2_lanes["speed_homogen"] = 10
        LFD_2_lanes["crossing_flow"] = 0.5 * 2 * Traffic["FD"]["C"]
        Traffic["LFD_2_lanes"] = LFD_2_lanes
        # 3 lanes
        LFD_3_lanes = {}
        LFD_3_lanes["values"] = [0.34, 0.33, 0.33]
        LFD_3_lanes["speed_homogen"] = 10
        LFD_3_lanes["crossing_flow"] = 0.5 * 3 * Traffic["FD"]["C"]
        Traffic["LFD_3_lanes"] = LFD_3_lanes

        # Behavior at nodes
        Traffic["FIFO"] = 1
    else:
        if not("FD" in Traffic.keys()):
            FD = {}
            FD["u"] = 30
            FD["w"] = 5
            FD["kx"] = 0.2
            FD["C"] = 0.8571428571428571
            Traffic["FD"] = FD
        if not("LFD_2_lanes" in Traffic.keys()):
            LFD_2_lanes = {}
            LFD_2_lanes["values"] = [0.5, 0.5]
            LFD_2_lanes["speed_homogen"] = 10
            LFD_2_lanes["crossing_flow"] = 0.5 * 2 * Traffic["FD"]["C"]
            Traffic["LFD_2_lanes"] = LFD_2_lanes
        if not("LFD_3_lanes" in Traffic.keys()):
            LFD_3_lanes = {}
            LFD_3_lanes["values"] = [0.34, 0.33, 0.33]
            LFD_3_lanes["speed_homogen"] = 10
            LFD_3_lanes["crossing_flow"] = 0.5 * 3 * Traffic["FD"]["C"]
            Traffic["LFD_3_lanes"] = LFD_3_lanes
        if not("FIFO" in Traffic.keys()):
            Traffic["FIFO"] = 1

    if not(VehicleClass):
        # Class 1 by default
        i = 1
        vclass = {}
        vclass["Name"] = "VL"
        #vclass["Speed"] = 36
        #vclass["Length"] = 5
        #vclass["Color"] = [0,0,0.8]
        VehicleClass[i] = vclass
#    else:
#        for iveh in list(VehicleClass.keys()):
# if not("Name" in VehicleClass[iveh].keys()) or not(VehicleClass[iveh]["Name"]):
##                VehicleClass[iveh]["Name"] = "VL"
# if not("Speed" in VehicleClass[iveh].keys()) or not(VehicleClass[iveh]["Speed"]):
##                VehicleClass[iveh]["Speed"] = 36
# if not("Length" in VehicleClass[iveh].keys()) or not(VehicleClass[iveh]["Length"]):
##                VehicleClass[iveh]["Length"] = 5
#            if not("Color" in VehicleClass[iveh].keys()) or not(VehicleClass[iveh]["Color"]):
#                VehicleClass[iveh]["Color"] = [0,0,0.8]

    return (Traffic, VehicleClass)

# Complete the "Links" key contents


def complete_links(Links, Nodes, Traffic):

    for link in list(Links.keys()):
        # Complete the missing "keys" of number of lanes and traffic
        # display warning messages if none have been provided
        if not("NumLanes" in Links[link].keys()):
            Links[link]["NumLanes"] = 1
            print("WARNING: No number of lanes has been set for link:" + str(link))
        if not("FD" in Links[link].keys()):
            Links[link]["FD"] = Traffic["FD"]
            print('WARNOING: No Fundamental Diagram has been set for link: ' + str(link))
        # ...
        # Calibration section
        # Change values from link type to user-provided values
        if Links[link]["Speed"] == None:
            Links[link]["Speed"] = Links[link]["FD"]["u"]

        if Links[link]["Capacity"] == None:
            Links[link]["Capacity"] = Links[link]["FD"]["C"] * \
                Links[link]["NumLanes"]

        if Links[link]["Priority"] == None:
            Links[link]["Priority"] = Links[link]["NumLanes"]
        # Modifie le FD en fonction du calage
        Links = update_link_DF(Links, link)
        # ...
        # Lane Fundamental Diagram Section to different lane behavior : NOT IN USE
#        if not("LFD" in Links[link].keys()) or not("values" in Links[link]["LFD"].keys()):
#            LFD = {}
#            if Links[link]["NumLanes"] == 1:
#                LFD["values"] = [1]
#            elif Links[link]["NumLanes"] == 2:
#                LFD["values"] = Traffic["LFD_2_lanes"]["values"]
#            elif Links[link]["NumLanes"] == 3:
#                LFD["values"] = Traffic["LFD_3_lanes"]["values"]
#            else:
#                LFD["values"] = [1/Links[link]["NumLanes"]] * Links[link]["NumLanes"]
#            Links[link]["LFD"] = LFD
#        elif type(Links[link]["LFD"]["values"])==int:
#            Links[link]["LFD"]["values"] = [Links[link]["LFD"]["values"]]
# elif len(Links[link]["LFD"]["values"]) != Links[link]["NumLanes"]:
##            Message = "Warning! The number of lanes for link " + str(link) + " is different from the number of specified LFDs on this link."
##            raise BaseException(Message)

    # If the length has not been set up, calculate it with the points
        if not("Length" in Links[link].keys()):
            Temp_List_X = np.array(Links[link]["Points"][0, :])
            Temp_List_Y = np.array(Links[link]["Points"][1, :])
            Temp_L = 0
            for j in range(len(Temp_List_X)-1):
                Temp_L = Temp_L + \
                    np.sqrt((Temp_List_X[j+1] - Temp_List_X[j]) **
                            2 + (Temp_List_Y[j+1] - Temp_List_Y[j])**2)
            Links[link]["Length"] = Temp_L
        # Mean travel time
        if not("MeanTravelTime" in Links[link].keys()):
            Links[link]["MeanTravelTime"] = Links[link]["Length"] / \
                Links[link]["Speed"]
        # Node Up Id
        if not("NodeUpID" in Links[link].keys()):
            Links[link]["NodeUpID"] = []
        # Node down ID
        if not("NodeDownID" in Links[link].keys()):
            Links[link]["NodeDownID"] = []
        # ...
        # Partie régulation
        if not("AssociatedLink" in Links[link].keys()):
            Links[link]["AssociatedLink"] = None
        
        # ...
        # Reserved links for certain category of vehicles
        # Has to be an array
        if not("IsReservedTo" in Links[link].keys()):
            Links[link]["IsReservedTo"] = []

    for node in list(Nodes.keys()):
        # ----
        for j in Nodes[node]["IncomingLinksID"]:
            Links[j]["NodeDownID"] = node
        for j in Nodes[node]["OutgoingLinksID"]:
            Links[j]["NodeUpID"] = node

    return Links

# def update_link_capacite(Links, i):
#    NumLanes = Links[i]["NumLanes"]
#    try:
#        Tmp_Link_LFD = Links[i]["LFD"]["values"]
#    except:
#        import pdb
#        pdb.set_trace()
#
#    C_DF = Links[i]["FD"]["kx"] * Links[i]["FD"]["w"] * Links[i]["FD"]["u"] / (Links[i]["FD"]["w"] + Links[i]["FD"]["u"])
#    if NumLanes == 1:
#        Capa_LFD = np.inf
#    if NumLanes == 2:
#        P_gd = abs(Tmp_Link_LFD[1] - Tmp_Link_LFD[0])
#        Capa_LFD = C_DF*2/(1+P_gd)
#    if NumLanes == 3:
#        P_cd = Tmp_Link_LFD[1] - Tmp_Link_LFD[0]
#        P_gd = Tmp_Link_LFD[2] - Tmp_Link_LFD[0]
#        Capa_LFD = C_DF*3/(1 + P_cd + P_gd)
#    if NumLanes>3:
#        Capa_LFD = np.inf
#
#    Capacity = min(C_DF*NumLanes, Capa_LFD)
#
#    if "CapacityLimit" in Links.keys():
#        Capacity = min(Capacity, Links[i]["CapacityLimit"])
#
#    return Capacity


def update_link_DF(Links, i):
    FD = Links[i]["FD"]
    u = Links[i]['Speed']
    kx = FD['kx']
    C = Links[i]['Capacity']/Links[i]["NumLanes"]

    FD.update({'u': u, 'C': C, 'w': C / (kx - C/u)})
    Links[i]["FD"].update({"FD": FD})
    return Links


def complete_nodes(Links, Nodes, Traffic):

    for node in Nodes.keys():
        if not("Type" in Nodes[node].keys()):
            Nodes[node]["Type"] = []
        if not("IncomingLinksID" in Nodes[node].keys()):
            Message = "Defining IncomingLinksID for Nodes is necessary !"
            raise BaseException(Message)
        if not("OutgoingLinksID" in Nodes[node].keys()):
            Message = "Defining OutgoingLinksID for Nodes is necessary !"
            raise BaseException(Message)
        if not("SignalsID" in Nodes[node].keys()):
            Nodes[node]["SignalsID"] = []
#        if not("BoundaryID" in Nodes[node].keys()):
#            Message = "Boundary nodes must be associated to Entry and Exits ids."
#            raise BaseException("Message")
        if not("NumIncomingLinks" in Nodes[node].keys()):
            Nodes[node]["NumIncomingLinks"] = []
        if not("NumOutgoingLinks" in Nodes[node].keys()):
            Nodes[node]["NumOutgoingLinks"] = []
        if not("AlphaOD" in Nodes[node].keys()):
            Nodes[node]["AlphaOD"] = []
        if not("FIFO" in Nodes[node].keys()):
            Nodes[node]["FIFO"] = Traffic["FIFO"]
        if not("LaneAllocation" in Nodes[node].keys()):
            Nodes[node]["LaneAllocation"] = []
        if not("CapacityDrop" in Nodes[node].keys()):
            Nodes[node]["CapacityDrop"] = np.zeros(
                Nodes[node]["NumIncomingLinks"]+1)
        if not("TransitTime" in Nodes[node].keys()):
            Nodes[node]["TransitTime"] = 0
        if not("CapacityForced" in Nodes[node].keys()):
            Nodes[node]["CapacityForced"] = np.inf

    for node in Nodes.keys():
        # (a) Type
        if not("Type" in Nodes[node].keys()):
            if len(Nodes[node]["IncomingLinksID"]) == 0:
                Nodes[node]["Type"] = 1  # Entry
            elif len(Nodes[node]["OutgoingLinksID"]) == 0:
                Nodes[node]["Type"] = 2
            else:
                Nodes[node]["Type"] = 0

        # (b) NumIncomingLinks
        if not("NumIncomingLinks" in Nodes[node].keys()):
            Nodes[node]["NumIncomingLinks"] = len(
                Nodes[node]["IncomingLinksID"])

        # (c) NumOutgoingLinks
        if not("NumOutgoingLinks" in Nodes[node].keys()):
            Nodes[node]["NumOutgoingLinks"] = len(
                Nodes[node]["OutgoingLinksID"])

        # (d) AlphaOD
        Nodes[node].update({"AlphaOD": np.array([])})
        if Nodes[node]["NumIncomingLinks"] >= 1:  # this is a merge
            NumIncomingLanes = [Links[link]["Priority"]
                                for link in Nodes[node]["IncomingLinksID"]]
            if sum(NumIncomingLanes) == 0:
                NumIncomingLanes = [Links[link]["NumLanes"]
                                    for link in Nodes[node]["IncomingLinksID"]]
            moyenne = 1/sum(NumIncomingLanes) * np.array(NumIncomingLanes)
            Nodes[node].update(
                {"AlphaOD": np.hstack((moyenne, np.array([0])))})
            # if Nodes[node]["AlphaOD"].shape[0] > 1:
            #     Nodes[node]["AlphaOD"] = Nodes[node]["AlphaOD"][0,:]

        if Nodes[node]["NumIncomingLinks"] == 0:
            Nodes[node]["AlphaOD"] = np.array([1.])
        # elif not(Nodes[node]["AlphaOD"].shape[1]==len(Nodes[node]["IncomingLinksID"])+1):
        #     Nodes[node]["AlphaOD"] = np.vstack([Nodes[node]["AlphaOD"], np.zeros([1,Nodes[node]["AlphaOD"].shape[1]])])

        # (e) SignalID ---
        if not('SignalsID' in Nodes[node].keys()):
            Nodes[node]['SignalsID'] = [0 for i in range(
                Nodes[node]['NumncomingLinks'] + 1)]
        if len(Nodes[node]['SignalsID']) != Nodes[node]['NumIncomingLinks'] + 1:
            Nodes[node]['SignalsID'].append(0)

            # (f) FIFO ---
        if not("FIFO" in Nodes[node].keys()):
            Nodes[node].update({"FIFO": Traffic["FIFO"]})
            Nodes[node].update({"LaneAllocation": []})
        elif Nodes[node]["FIFO"] == 1:
            Nodes[node].update({"LaneAllocation": []})
        else:
            if Nodes[node]["Type"] == 1 or Nodes[node]["Type"] == 2:
                Nodes[node].update({"LaneAllocation": []})
            else:
                DownstreamLanes = [Links[link]["NumLanes"]
                                   for link in Nodes[node]["OutgoingLinksID"]]
                UpstreamLane = Links[Nodes[node]
                                     ["IncomingLinksID"][0]]["NumLanes"]
                if not(sum(Nodes[node]["LaneAllocation"]) == UpstreamLane):
                    # The lane allocation is not correct
                    LaneRatio = np.array(DownstreamLanes) / \
                        sum(DownstreamLanes)
                    LaneAllocation = np.round(LaneRatio * UpstreamLane)
                    if sum(LaneAllocation) > UpstreamLane:
                        LaneAllocation[0] = LaneAllocation[0] - 1
                    elif sum(LaneAllocation) < UpstreamLane:
                        LaneAllocation[0] = LaneAllocation[0] + 1
                    Nodes[node]["LaneAllocation"] = LaneAllocation  # by default

        # (g) Capacity Drop ---
        if type(Nodes[node]["CapacityDrop"]) == str and Nodes[node]["CapacityDrop"] == 'auto':
            InCapacites = np.array([Links[link]["Capacite"] for link in Nodes[node]["IncomingLinksID"]]) / \
                np.array([Links[link]["Capacite"]
                          for link in Nodes[node]["NumLanes"]])
            Nodes[node]["CapacityDrop"] = 1 - InCapacites / max(InCapacites)
        elif len(Nodes[node]["CapacityDrop"]) < Nodes[node]["NumIncomingLinks"]:
            Drop = np.max(Nodes[node]["CapacityDrop"])
            Nodes[node]["CapacityDrop"] = np.zeros(
                Nodes[node]["NumIncomingLinks"])
            list_speeds = [Links[link]["Speed"]
                           for link in Nodes[node]["IncomingLinksID"]]
            IN = np.where(np.array(list_speeds) < max(list_speeds))[0]
            if len(list_speeds) > 0:
                Nodes[node]["CapacityDrop"][IN] = Drop
        #Nodes[node]["CapacityDrop"] = [Nodes[node]["CapacityDrop"], 0]

        # (h) transit times ---
        if len(Nodes[node]["IncomingLinksID"]) == 0 or len(Nodes[node]["OutgoingLinksID"]) == 0:
            Nodes[node]["TransitTime"] = 0
        else:
            Points = np.zeros((0, 2))
            Speeds = []
            # ...
            for ilink in Nodes[node]["IncomingLinksID"]:
                Points = np.vstack((Points, Links[ilink]["Points"][:, -1]))
                Speeds.append(Links[ilink]["Speed"])
            # ...
            for out in range(len(Nodes[node]["OutgoingLinksID"])):
                ilink = Nodes[node]["OutgoingLinksID"][out]
                Points = np.vstack((Points, Links[ilink]["Points"][:, 0]))
                Speeds.append(Links[ilink]["Speed"])
            # ...
            Points = Points.T
            X = np.max(Points[0, :]) - np.min(Points[0, :])
            Y = np.max(Points[1, :]) - np.min(Points[1, :])
            Dist = np.sqrt(X**2 + Y**2)
            Speed = np.min(Speeds)
            Nodes[node]["TransitTime"] = Dist/Speed
            if np.isnan(Nodes[node]["TransitTime"]):
                Nodes[node]["TransitTime"] = 0

        # (i) Capacity forced ---
        if not(Nodes[node]["CapacityForced"]):
            Nodes[node]["CapacityForced"] = np.inf

    return Nodes


def complete_exits(Nodes, Exits, General):
    #    if not(Exits):
    #        exit = {"NodeID" : [],
    #                "IncomingLinksID" : [],
    #                "Supply" : {"Time" : [], "Data" : []}}
    #        Exits = [exit]
    for exit in list(Exits.keys()):
        if not("Supply" in list(Exits[exit].keys())):
            Exits[exit].update({"Supply": {"Time": [], "Data": []}})
    for node in list(Nodes.keys()):
        if Nodes[node]["Type"] == 2:  # exit
            Exits[node]["IncomingLinksID"] = Nodes[node]["IncomingLinksID"]
            if not("Supply" in Exits[node].keys()) or len(Exits[node]["Supply"]["Time"]) == 0 or len(Exits[node]["Supply"]["Data"]) == 0:
                Exits[node]["Supply"]["Time"] = [
                    0, General["SimulationDuration"][-1]]
                Exits[node]["Supply"]["Data"] = np.inf * np.ones(2)
            else:
                if Exits[node]["Supply"]["Time"][-1] < General["SimulationDuration"][-1]:
                    Exits[node]["Supply"]["Time"].append(86400)
                    Exits[node]["Supply"]["Data"].append(np.inf)

    return Exits

# def complete_entries(Nodes, Links, Entries, Exits, VehicleClass):
#    # (1) Adding lacking items
#    for entry in list(Entries.keys()):
#        if not("DistributionPerDestination" in list(Entries[entry].keys())):
#            entry["DistributionPerDestination"] = []
#        if not("DistributionPerVehClass" in list(Entries[entry].keys())):
#            entry["DistributionPerVehClass"] = []
#
#    # (2) Completing Entry variables
#    NumNodes = len(Nodes)
#    for node in list(Nodes.keys()):
#        if Nodes[node]["Type"] == 1:
#            if not(Nodes[node]["BoundaryID"]):
#                Entries[Nodes[node]["BoundaryID"]]["NodeID"] = node
#                Entrie[Nodes[node]["BoundaryID"]]["OutGoingLinks"]  = Nodes[node]["OutgoingLinksID"]
#
#    # (3) By default OD distribution
#
#    # --- matrice d'adjacence
#    Adjacency = zeros([NumNodes, NumNodes])
#    for link in list(Links.keys()):
#        if not(Links[link]["NodeupID"]) and not(Links[link]["NodeUpID"] == 0) and not(Links[link]["NodeDownID"]) and not(Links[link]["NodeDownID"] == 0):
#            Adjacency[Links[link]["NodeupID"], Links[link]["NodeDownID"]] = 1
#
#    # --- matrice d'accès
#    Accessibility = np.zeros(Adjacency.shape)
#    Adjacency_tmp = np.identity(Adjacency.shape[0])
#    for link in list(Links.keys()):
#        Adjacency_tmp = np.dot(Adjacency_tmp, Adjacency_tmp)
#        Accessibility = Accessibility + Adjacency_tmp
#
#    # completion
#    NumEntries = len(Entries)
#    NumExits = len(Exits)
#    list_node_exit = [exit["NodeID"] for exit in Exits]
#    NumVehClasses = max(1, len(VehicleClass))
#    for entry in list(Entries.keys()):
#        if Entries[entry]["Demand"]["Time"][-1] < 86400:
#            Entries[entry]["Demand"]["Time"].append(86400)
#            Entries[entry]["Demand"]["Data"].append(0)
#        if not(Entries[entry]["DistributionPerDestination"]):
#            list_accessible_destinations = np.where(Accessibility[Entries[entry]["NodeID"], liste_node_exit] > 0)[0]
#            Entries[entry]["DistributionPerDestination"] = np.zeros([1, NumExits])
#            Entries[entry]["DistributionPerDestination"][list_accessible_destinations] = (1 / len(list_accessible_destinations))
#        if not(Entries[entry]["DistributionPerVehClass"]):
#            Entries[entry]["DistributionPerVehClass"] = np.hstack(np.array([1]), np.zeros([1, NumVehClasses - 1]))
#    return Entries

# def complete_routes(Routes):
#    if len(Routes)==0:
#        print("The routes used are defined by the user only : possible bug...")
#    return


def validation(Links, Nodes, Entries, Exits, warning="print"):

    # Validation of network connection
    for link in list(Links.keys()):
        if not("NumLanes" in Links[link].keys()):
            if warning == "print":
                print("The number of lanes for link " +
                      str(link) + "must be defined.")
            else:
                sys.exit("The number of lanes for link " +
                         str(link) + "must be defined.")
        if not("NodeDownID" in Links[link].keys()):
            if warning == "print":
                print("The link " + str(link) +
                      " is not connected with any downstream node.")
            else:
                sys.exit("The link " + str(link) +
                         " is not connected with any downstream node.")
        if not("NodeUpID" in Links[link].keys()):
            if warning == "print":
                print("The link " + str(link) +
                      " is not connected with any upstream node.")
            else:
                sys.exit("The link " + str(link) +
                         " is not connected with any upstream node.")
    # ...
    # Validation of specific nodes
    for node in list(Nodes.keys()):
        # An entry nodes must have 0 upstream link and 1 link downstream
        if Nodes[node]["Type"] == 1:
            if Nodes[node]["IncomingLinksID"]:
                if warning == "print":
                    print("The node " + str(node) +
                          " is an entry node : it cannot have an upstream link.")
                else:
                    sys.exit("The node " + str(node) +
                             " is an entry node : it cannot have an upstream link.")
            if len(Nodes[node]["OutgoingLinksID"]) > 1:
                if warning == "print":
                    print("The node " + str(node) +
                          " is an entry node : it cannot have more than one downstream link.")
                else:
                    sys.exit("The node " + str(node) +
                             " is an entry node : it cannot have more than one downstream link.")

        # An exit node must have 1 upstream link and 0 downstream link
        elif Nodes[node]["Type"] == 2:
            if Nodes[node]["OutgoingLinksID"]:
                if warning == "print":
                    print("The node " + str(node) +
                          " is an exit node : it cannot have a downstream link.")
                else:
                    sys.exit("The node " + str(node) +
                             " is an exit node : it cannot have a downstream link.")
            if len(Nodes[node]["IncomingLinksID"]) > 1:
                if warning == "print":
                    print("The node " + str(node) +
                          " is an exit node : it cannot have more than one upstream link.")
                else:
                    sys.exit("The node " + str(node) +
                             " is an exit node : it cannot have more than one upstream link.")

        # Merge and diverge
        if len(Nodes[node]["IncomingLinksID"]) > 1:
            if len(Nodes[node]["AlphaOD"]) != len(Nodes[node]["IncomingLinksID"]) + 1:
                if warning == "print":
                    print("The node " + str(node) +
                          " AlphaOD is uncorrectly defined")
                else:
                    sys.exit("The node " + str(node) +
                             " AlphaOD is uncorrectly defined")

        # traffic light...

        # Sensors...
    return
