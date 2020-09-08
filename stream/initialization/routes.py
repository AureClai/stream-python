from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

import numpy as np

# Return matrix and ID, num correspondance


def getMatrix(sce):  # scr = scenario dictionnary
    # Loop over the nodes to initialize the matrix of Cost
    coresp = {}
    icoresp = {}
    count = 0
    for node in list(sce["Nodes"].keys()):
        coresp.update({node: count})
        icoresp.update({count: node})
        count = count+1
    costMat = np.ones([len(coresp)]*2) * np.Inf

    # Loop over the links
    links = sce["Links"]
    for link in list(links.keys()):
        # Add the corresponding cost in matrix IF AND ONLY IF it is less than the existing value
        newValue = links[link]["Length"]/links[link]["FD"]["u"]
        if newValue < costMat[coresp[links[link]["NodeUpID"]], coresp[links[link]
                                                                      ["NodeDownID"]]]:
            costMat[coresp[links[link]["NodeUpID"]], coresp[links[link]
                                                            ["NodeDownID"]]] = newValue

    return (costMat, coresp, icoresp)


def getGraph(matrix):
    return csr_matrix(matrix)


def calculateShortestsPaths(matrix, method='D'):
    # Calculate the distance and the predecessors matrix
    D, Pr = shortest_path(matrix, directed=True,
                          method=method, return_predecessors=True)
    return (D, Pr)


def getPathByOD(Pr, coresp, icoresp, entry, exit):
    # Exploring the predecessors matrix and construct the shortest path
    path = [exit]
    k = [coresp[exit]]
    while Pr[coresp[entry], k] != -9999:
        #path.append(icoresp[int(Pr[coresp[entry], k])])
        path.append(icoresp[int(Pr[coresp[entry], k])])
        k = Pr[coresp[entry], k]
    return path[::-1]


def filterLinksByVehicleClass(links, vehClass):
    # Init the output dict to copy
    outputLinks = {}
    # For each link
    for link in links:
        # If the current link is not reserved to a certain class OR the current link is reserved to the vehicle Class
        if len(links[link]["IsReservedTo"]) == 0 or vehClass in links[link]["IsReservedTo"]:
            # Add it
            outputLinks.update({link: links[link]})
    return outputLinks


def getRoutes(sce):
    routes = {}
    baseLinks = sce["Links"]
    for vehClass in list(sce["VehicleClass"].keys()):
        # filter links for exclusive access to the current class
        filteredLinks = filterLinksByVehicleClass(baseLinks, vehClass)
        sce["Links"] = filteredLinks
        matrix, coresp, icoresp = getMatrix(sce)
        D, Pr = calculateShortestsPaths(matrix)
        classRoute = {}
        id = 0
        for entry in list(sce["Entries"].keys()):
            for exit in list(sce["Exits"].keys()):
                path = getPathByOD(Pr, coresp, icoresp, entry, exit)
                # if the path is possible...
                if not len(path) == 1:
                    # find the path in terms of links
                    classRoute.update({id: {"EntryID": entry, "ExitID": exit,
                                            "NodeList": path, "Path": __getLinkPath(path, sce)}})
                    id = id + 1
        routes.update({vehClass: classRoute})
    return routes


def getPathByNodes(sce, node1, node2):
    matrix, coresp, icoresp = getMatrix(sce)
    D, Pr = calculateShortestsPaths(matrix)
    path = getPathByOD(Pr, coresp, icoresp, node1, node2)
    return path


def __getLinkPath(nodePath, sce):
    linksPath = []
    for i in range(len(nodePath) - 1):
        goodLink = -1
        goodTravelTime = np.Inf
        # Find next the good next Link
        for potentialLink in sce["Nodes"][nodePath[i]]["OutgoingLinksID"]:
            if potentialLink in list(sce["Links"].keys()):
                #print("Searching if link " + str(potentialLink) + " is the good path link for node " + str(nodePath[i]) + " to " + str(nodePath[i+1]))
                if sce["Links"][potentialLink]["NodeDownID"] == nodePath[i+1] and sce["Links"][potentialLink]["Length"]/sce["Links"][potentialLink]["Speed"] < goodTravelTime:
                    goodLink = potentialLink
                    goodTravelTime = sce["Links"][potentialLink]["Length"] / \
                        sce["Links"][potentialLink]["Speed"]
        # Add the link into the path
        if goodLink < 0:
            print("ERROR  : INVALID LINK")
        else:
            linksPath.append(goodLink)
    return linksPath


def getLinkPath(nodePath, sce):
    return __getLinkPath(nodePath, sce)
