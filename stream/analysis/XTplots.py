# -*- coding: utf-8 -*-
"""
Created on Thu May 23 14:21:45 2019

@author: aurelien.clairais
"""

#...
# import dependancies
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

import os
import sys

#...
# Global variables : Colormaps
cmaps = {}
colorlist = ["black", "maroon" , "red", "orange","yellow","lime"]
colorlist2 = ["black", "maroon" , "red", "orange","yellow","lime"]
colorlist2.reverse()
cmaps['V'] = mpl.colors.LinearSegmentedColormap.from_list("", colorlist )
cmaps['K'] = mpl.colors.LinearSegmentedColormap.from_list("", colorlist2)
cmaps['Q'] = mpl.colors.LinearSegmentedColormap.from_list("", ['black', 'white'])
#...

def plotXTDiagOnLink(linkXT, idLink, variables = ['Q', 'K', 'V'], cmap = 'jet'):
    cmap = plt.get_cmap(cmap)
    plt.rc('font', family='Cambria', size = 10, style = 'normal', weight = 'light')
    for _var in variables:
        plt.figure( figsize=(8,6), facecolor='w' )
        plt.title(_var + ' values for link ' + str(idLink))
        plt.xlabel('Time (s)')
        plt.ylabel('Space (m)')
        if _var == 'Q':
            plt.pcolormesh(linkXT["T"], linkXT["X"], linkXT["Q"], vmin = 0, vmax = np.max(linkXT["Q"]), cmap=cmap)
        elif _var == 'K':
            plt.pcolormesh(linkXT["T"], linkXT["X"], linkXT["K"], vmin = 0, vmax = linkXT["FD"]["kx"], cmap=cmap)
        elif _var == 'V':
            plt.pcolormesh(linkXT["T"], linkXT["X"], linkXT["V"], vmin = 0, vmax = linkXT["FD"]["u"], cmap=cmap)
        plt.colorbar()
        plt.show()

def plotXTDiagOnPath(linksXT, path, variables = ['Q', 'K', 'V']):
    #...
    # Global variables : Colormaps
    cmaps = {}
    colorlist = ["black", "maroon" , "red", "orange","yellow","lime"]
    colorlist2 = ["black", "maroon" , "red", "orange","yellow","lime"]
    colorlist2.reverse()
    cmaps['V'] = mpl.colors.LinearSegmentedColormap.from_list("", colorlist )
    cmaps['K'] = mpl.colors.LinearSegmentedColormap.from_list("", colorlist2)
    cmaps['Q'] = mpl.colors.LinearSegmentedColormap.from_list("", ['black', 'white'])
    cellsT = linksXT[path[0]]["T"]
    cellsX = linksXT[path[0]]["X"]
    cellsQ = linksXT[path[0]]["Q"]
    cellsK = linksXT[path[0]]["K"]
    cellsV = linksXT[path[0]]["V"]
    cumLengths = [np.max(cellsX)]
    max_u = linksXT[path[0]]["FD"]["u"]
    max_C = linksXT[path[0]]["FD"]["C"]
    max_kx = linksXT[path[0]]["FD"]["kx"]
    tmin = np.min(cellsT)
    tmax = np.max(cellsT)
    if len(path) > 1:
        for link in path[1:]:
            prevLength = cumLengths[-1]
            cellsT = np.vstack((cellsT, linksXT[link]["T"]))
            cellsX = np.vstack((cellsX, linksXT[link]["X"] + prevLength))
            cellsQ = np.vstack((cellsQ, linksXT[link]["Q"]))
            cellsV = np.vstack((cellsV, linksXT[link]["V"]))
            cellsK = np.vstack((cellsK, linksXT[link]["K"]))
            cumLengths.append(prevLength + np.max(linksXT[link]["X"]))
            max_u = max(max_u, linksXT[link]["FD"]["u"])
            max_C = max(max_C, linksXT[link]["FD"]["C"])
            max_kx = max(max_kx, linksXT[link]["FD"]["kx"])
    plt.show()

    #...
    #cmap = plt.get_cmap(cmap)
    plt.rc('font', family='Cambria', size = 10, style = 'normal', weight = 'light')
    for _var in variables:
        plt.figure( figsize=(8,6), facecolor='w' )
        plt.title(_var + ' values for path ' + str(path))
        plt.xlabel('Time (s)')
        plt.ylabel('Space (m)')
        if _var == 'Q':
            plt.pcolormesh(cellsT, cellsX, cellsQ, vmin = 0, vmax = max_C, cmap=cmaps['Q'])
            #...
            for x in cumLengths:
                plt.plot([tmin, tmax],[x, x], 'k--')
        elif _var == 'K':
            plt.pcolormesh(cellsT, cellsX, cellsK, vmin = 0, vmax = max_kx, cmap=cmaps['K'])
            #...
            for x in cumLengths:
                plt.plot([tmin, tmax],[x, x], 'k--')
        elif _var == 'V':
            plt.pcolormesh(cellsT, cellsX, cellsV, vmin = 0, vmax = max_u, cmap=cmaps['V'])
            #...
            for x in cumLengths:
                plt.plot([tmin, tmax],[x, x], 'k--')
        plt.colorbar()
