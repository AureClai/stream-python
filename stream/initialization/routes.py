from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

import numpy as np

# Return matrix and ID, num correspondance
def getMatrix(sce): #scr = scenario dictionnary
    """
    This function generates a matrix and a dictionary of ID and number correspondence 
    from a given scenario.

    Parameters:
    sce (dict): A dictionary containing a scenario.

    Returns:
    tuple: A tuple containing the cost matrix, correspondence dictionary, and inverse correspondence dictionary.
    """
    # Loop over the nodes to initialize the matrix of Cost
    coresp = {}
    icoresp = {}
    count = 0
    for node in list(sce["Nodes"].keys()):
        coresp.update({node : count})
        icoresp.update({count : node})
        count = count+1
    costMat = np.zeros([len(coresp)]*2)

    # Loop over the link
    links = sce["Links"]
    for link in list(links.keys()):
        # Add the corresponding cost in matrix
        costMat[coresp[links[link]["NodeUpID"]], coresp[links[link]["NodeDownID"]]] = links[link]["Length"]/links[link]["FD"]["u"]

    return (costMat, coresp, icoresp)

def getGraph(matrix):
    """
    This function generates a compressed sparse row (CSR) matrix from a given matrix.

    Parameters:
    matrix (np.array): A numpy array.

    Returns:
    csr_matrix: A CSR matrix.
    """
    return csr_matrix(matrix)

def calculateShortestsPaths(matrix, method = 'D'):
    """
    This function calculates the shortest paths in the given matrix.

    Parameters:
    matrix (np.array): A numpy array.
    method (str): The method to use for calculating the shortest paths. Default is 'D'.

    Returns:
    tuple: A tuple containing the distance and the predecessors matrix.
    """
    # Calculate the distance and the predecessors matrix
    D, Pr = shortest_path(matrix, directed=True, method = method, return_predecessors=True)
    return (D, Pr)

def getPathByOD(Pr, coresp, icoresp, entry, exit):
    """
    This function constructs the shortest path by exploring the predecessors matrix.

    Parameters:
    Pr (np.array): The predecessors matrix.
    coresp (dict): The correspondence dictionary.
    icoresp (dict): The inverse correspondence dictionary.
    entry (int): The entry node.
    exit (int): The exit node.

    Returns:
    list: A list containing the shortest path.
    """
    # Exploring the predecessors matrix and construct the shortest path
    path = [exit]
    k = [coresp[exit]]
    while Pr[coresp[entry], k] != -9999:
        #path.append(icoresp[int(Pr[coresp[entry], k])])
        path.append(icoresp[int(Pr[coresp[entry], k])])
        k = Pr[coresp[entry], k]
    return path[::-1]

def getRoutes(sce):
    """
    This function generates routes from a given scenario.

    Parameters:
    sce (dict): A dictionary containing a scenario.

    Returns:
    dict: A dictionary containing the routes.
    """
    matrix, coresp, icoresp = getMatrix(sce)
    D, Pr = calculateShortestsPaths(matrix)
    routes = {}
    id = 0
    for entry in list(sce["Entries"].keys()):
        for exit in list(sce["Exits"].keys()):
            path = getPathByOD(Pr, coresp, icoresp, entry, exit)
            #if the path is possible...
            if not len(path)==1:
                #find the path in terms of links
                routes.update({id : {"EntryID" : entry, "ExitID" : exit, "NodeList" :path , "Path" : __getLinkPath(path, sce)}})
                id = id + 1
    return routes

def getPathByNodes(sce, node1, node2):
    """
    This function generates a path between two nodes from a given scenario.

    Parameters:
    sce (dict): A dictionary containing a scenario.
    node1 (int): The first node.
    node2 (int): The second node.

    Returns:
    list: A list containing the path.
    """
    matrix, coresp, icoresp = getMatrix(sce)
    D, Pr = calculateShortestsPaths(matrix)
    path = getPathByOD(Pr, coresp, icoresp ,node1, node2)
    return path

def __getLinkPath(nodePath, sce):
    """
    This function generates a link path from a given node path and scenario.

    Parameters:
    nodePath (list): A list containing the node path.
    sce (dict): A dictionary containing a scenario.

    Returns:
    list: A list containing the link path.
    """
    linksPath = []
    for i in range(len(nodePath) - 1):
        goodLink = -1
        # Find next the good next Link
        for potentialLink in sce["Nodes"][nodePath[i]]["OutgoingLinksID"]:
            #print("Searching if link " + str(potentialLink) + " is the good path link for node " + str(nodePath[i]) + " to " + str(nodePath[i+1]))
            if sce["Links"][potentialLink]["NodeDownID"]==nodePath[i+1]:
                goodLink = potentialLink
                break
        # Add the link into the path
        if goodLink < 0:
            print("ERROR  : INVALID LINK")
        else :
            linksPath.append(goodLink)
    return linksPath

def getLinkPath(nodePath, sce):
    """
    This function returns the link path from a given node path and scenario.

    Parameters:
    nodePath (list): A list containing the node path.
    sce (dict): A dictionary containing a scenario.

    Returns:
    list: A list containing the link path.
    """
    return __getLinkPath(nodePath, sce)
