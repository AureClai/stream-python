# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 16:37:18 2019

@author: aurelien.clairais
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 16:59:48 2019

@author: aurelien.clairais
"""

# importation des modules
import numpy as np
import matplotlib.pylab as plt
from matplotlib.animation import FuncAnimation, writers
import matplotlib.collections as mcoll
import matplotlib as mpl

# Global variables : Colormaps
custom_cmap = mpl.colors.LinearSegmentedColormap.from_list("", ["maroon","red","orange","yellow","lime"])
# init xmin, xmax etc
_xmin = np.inf
_xmax = -np.inf
_ymin = np.inf
_ymax = -np.inf
#...

##############################################################################
# functions
def convertSecondsTohhmmss(time):
    hours = int(time/3600)
    minutes = int((time%3600)/60)
    seconds = time%60
    string = str(int(hours/10)) + str(hours%10) + "." + str(int(minutes/10)) + str(minutes%10) + "." + str(int(seconds/10)) + str(seconds%10)
    return string

#    
def _plotTraficolorNetwork(column, diagsXT):
    print(column)
    column -= 1
    plt.cla()
    t = diagsXT[list(diagsXT.keys())[0]]["T"][0,column]
    for link in list(diagsXT):
        Vs = diagsXT[link]["V"][:,column]/diagsXT[link]["FD"]["u"]
        lc = colorline(diagsXT[link]["Xp"], diagsXT[link]["Yp"], Vs, cmap=custom_cmap)
    plt.gca().set_aspect('equal')
    plt.axis('off')
    plt.title("Traficolor time = " + convertSecondsTohhmmss(t), color='w')
    #    
    plt.xlim(_xmin, _xmax)
    plt.ylim(_ymin, _ymax)
    return
#    
def plotTraficolorNetwork(column, diagsXT, Simulation):
    print(column)
    diagsXT = getPointsProjection(Simulation, diagsXT)
    column -= 1
    plt.cla()
    t = diagsXT[list(diagsXT.keys())[0]]["T"][0,column]
    for link in list(diagsXT):
        Vs = diagsXT[link]["V"][:,column]/diagsXT[link]["FD"]["u"]
        lc = colorline(diagsXT[link]["Xp"], diagsXT[link]["Yp"], Vs, cmap=custom_cmap)
    plt.gca().set_aspect('equal')
    plt.axis('off')
    plt.title("Traficolor time = " + convertSecondsTohhmmss(t), color='w')
    #    
    plt.xlim(_xmin, _xmax)
    plt.ylim(_ymin, _ymax)
    return

##############################################################################
def colorline(
    x, y, z=None, cmap='copper', norm=plt.Normalize(0.0, 1.0),
    linewidth=2, alpha=1.0, ax = None):
    """
    Adapted from :
    https://stackoverflow.com/questions/36074455/python-matplotlib-with-a-line-color-gradient-and-colorbar
    
    http://nbviewer.ipython.org/github/dpsanders/matplotlib-examples/blob/master/colorline.ipynb
    http://matplotlib.org/examples/pylab_examples/multicolored_line.html
    Plot a colored line with coordinates x and y
    Optionally specify colors in the array z
    Optionally specify a colormap, a norm function and a line width
    """
    
    # Default colors equally spaced on [0,1]:
    if z is None:
        z = np.linspace(0.0, 1.0, len(x))
    
    # Special case if a single number:
    # to check for numerical input -- this is a hack
    if not hasattr(z, "__iter__"):
        z = np.array([z])
    
    z = np.asarray(z)
    
    segments = make_segments(x, y)
    lc = mcoll.LineCollection(segments, array=z, cmap=custom_cmap, norm=norm,
                              linewidth=linewidth, alpha=alpha)
    if ax == None:
        ax = plt.gca()
    ax.add_collection(lc)
    
    return lc

def make_segments(x, y):
    """
    Adapted from :
    https://stackoverflow.com/questions/36074455/python-matplotlib-with-a-line-color-gradient-and-colorbar
    
    Create list of line segments from x and y coordinates, in the correct format
    for LineCollection: an array of the form numlines x (points per line) x 2 (x
    and y) array
    """
    
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    return segments

def getPointsProjection(Simulation, diagsXT):
    global _xmin
    global _xmax
    global _ymin
    global _ymax
    # Project the lengths on the link curve
    for link in list(diagsXT):
        XTData = diagsXT[link]
        
        # find points corresponding to link points
        points = Simulation["Links"][link]["Points"]
        Xs_link = points[0,:]
        Ys_link = points[1,:]
        Ls_link = np.zeros(len(Xs_link))
        for n in range(len(Xs_link)- 2):
            length = np.sqrt((Xs_link[n+2] - Xs_link[n+1])**2 + (Ys_link[n+2] - Ys_link[n+1])**2)
            cum_length = Ls_link[n] + length
            Ls_link[n+1] = cum_length
        Ls_link[-1] = Simulation["Links"][link]["Length"]
        abs_diag = np.concatenate((XTData["X"][:,0],[Simulation["Links"][link]["Length"]]))
        Xs_diag = np.interp(abs_diag, Ls_link, Xs_link)
        Ys_diag = np.interp(abs_diag, Ls_link, Ys_link)
        _xmin = min(_xmin, Xs_diag.min())
        _ymin = min(_ymin, Ys_diag.min())
        _xmax = max(_xmax, Xs_diag.max())
        _ymax = max(_ymax, Ys_diag.max())
        
        diagsXT[link].update({'Xp' : Xs_diag, 'Yp' : Ys_diag})
        
    return diagsXT
    

def makeAnimation(Simulation=None, diagsXT = None,fps = 60, repeat = True, dx = 50, dt = 60):
    if Simulation == None:
        return
    
    if diagsXT == None:
        from .diagXT import calcXTOnAllLinks
        diagsXT = calcXTOnAllLinks(Simulation, dx, dt)
    
    # get prj
    NEWdiagsXT = getPointsProjection(Simulation, diagsXT)

    fig = plt.figure(figsize=(9.6,5.4),dpi=200,facecolor=[0.1,0.1,0.1])
    #...
    plt.rc('font', family='Cambria', size = 6, style = 'normal', weight = 'light')
    #... 
    # setup animation
    ani = FuncAnimation(fig, _plotTraficolorNetwork, fargs = (NEWdiagsXT,) ,frames=diagsXT[list(diagsXT)[0]]["T"].shape[1], interval=int(1000/fps), repeat=repeat)
    return ani

if __name__ == '__main__':
        
    # load the xtdiags info
    Simulation = np.load('simulation.npy', allow_pickle=True).item(0)
        
    #... 
    # setup animation
    ani = makeAnimation(Simulation = Simulation, dx = 50, dt = 60)
    
    #...
    # Set up formatting for the movie files
    Writer = writers['ffmpeg']
    writer = Writer(fps=60, metadata=dict(artist='Me'), bitrate=1800)
    ani.save('video.mp4', dpi=200, writer = writer, savefig_kwargs={'facecolor':[0.1,0.1,0.1]})






    

    

    

