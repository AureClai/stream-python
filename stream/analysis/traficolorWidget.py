# ------------------------------------------------------
# ---------------------- main.py -----------------------
# ------------------------------------------------------
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget, QVBoxLayout
from PyQt5 import uic

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import matplotlib as mpl

import numpy as np
import random
import os
import sys

#from .mplwidget import MplWidget
from .traficolor import colorline

custom_cmap = mpl.colors.LinearSegmentedColormap.from_list("", ["maroon","red","orange","yellow","lime"])

from matplotlib.backends.backend_qt5agg import FigureCanvas

from matplotlib.figure import Figure

class MplWidget(QWidget):
    def __init__(self, parent = None):
        
        QWidget.__init__(self, parent)
#        self.setGeometry(9,49, 421, 251)
        
        self.canvas = FigureCanvas(Figure())
        
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.setLayout(vertical_layout)

def getPointsProjection(Simulation, diagsXT):
    _xmin = np.inf
    _xmax = -np.inf
    _ymin = np.inf
    _ymax = -np.inf
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
        lims = {
                                    'xlim' : (_xmin,_xmax),
                                    'ylim' : (_ymin,_ymax)}
        
    return (diagsXT, lims)

def plotTraficolorOnAx(column, diagsXT, ax, drawMain):
    XLIM = ax.get_xlim()
    YLIM = ax.get_ylim()
#    column -= 1
    ax.clear()
    t = diagsXT[list(diagsXT.keys())[0]]["T"][0,column]
    for link in list(diagsXT):
        if not "hasSub" in list(diagsXT[link]):
            Vs = diagsXT[link]["V"][:,column]/diagsXT[link]["FD"]["u"]
            lc = colorline(diagsXT[link]["Xp"], diagsXT[link]["Yp"], Vs, cmap=custom_cmap, ax = ax)
        else:
            hasSub = diagsXT[link]["hasSub"]
            isMain = diagsXT[link]["isMain"]
            if (not hasSub and isMain) or not(hasSub or isMain or drawMain) or (hasSub and isMain and drawMain):
                Vs = diagsXT[link]["V"][:,column]/diagsXT[link]["FD"]["u"]
                lc = colorline(diagsXT[link]["Xp"], diagsXT[link]["Yp"], Vs, cmap=custom_cmap, ax = ax)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Traficolor time = " + convertSecondsTohhmmss(t), color='k')
    #    
    ax.set_xlim(XLIM)
    ax.set_ylim(YLIM)
    return


dir_path = os.path.dirname(os.path.realpath(__file__))
FORM_CLASS, _ = uic.loadUiType(os.path.join(dir_path, 'traficolorWidget.ui'))

def convertSecondsTohhmmss(time):
    hours = int(time/3600)
    minutes = int((time%3600)/60)
    seconds = time%60
    string = str(int(hours/10)) + str(hours%10) + ":" + str(int(minutes/10)) + str(minutes%10) + ":" + str(int(seconds/10)) + str(seconds%10)
    return string
     
class TraficolorWidget(QMainWindow, FORM_CLASS):
    
    def __init__(self, infos):
        
        QMainWindow.__init__(self)

        self.setupUi(self)
        self.infos = infos

        self.setWindowTitle("TRAFICOLOR - ALPHA")
        self.setFixedSize(self.size())
        
        self.fileSimu = infos['fileSimu']
        self.fileXT = infos['fileXT']
        
        self.tbegin.setFixedWidth(60)
        self.tend.setFixedWidth(60)
        
        self.mplWidget = MplWidget(self)
        self.mplWidget.setGeometry(9,39,941,571)
        
        #...
        # draw alternate links instead of mains ?
        self.drawMain = True
        
        #...
        # Toolbar
        self.addToolBar(NavigationToolbar(self.mplWidget.canvas, self))
        
        self.Simulation = np.load(self.fileSimu).item(0)
        self.diagsXT = np.load(self.fileXT).item(0)
        self.diagsXT, self.lims = getPointsProjection(self.Simulation, self.diagsXT)
        
        #...
        firstKey = list(self.diagsXT.keys())[0]
        tBegin = self.diagsXT[firstKey]["T"][0,0]
        tEnd = self.diagsXT[firstKey]["T"][0,-1]
        maximum = self.diagsXT[firstKey]["T"].shape[1] - 1
        
        #...
        #Slider config
#        self.tRange = np.arange(infos['tBegin'], infos['tEnd'] + infos['tTick'], infos['tTick'])
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(maximum)
        self.time_slider.setSingleStep(1)
        self.time_slider.setPageStep(0)
        self.time_slider.setValue(0)
        
        #...
        # signals
        self.time_slider.valueChanged.connect(self.timeChanged)
        self.alt_check.stateChanged.connect(self.altCheckCallback)

        
        self.tbegin.setText(convertSecondsTohhmmss(tBegin))
        self.tend.setText(convertSecondsTohhmmss(tEnd))
        
        self.initLimits()
        self.altCheckCallback()
    
        self.show()
#    def update_graph(self):
#
#        fs = 500
#        f = random.randint(1, 100)
#        ts = 1/fs
#        length_of_signal = 100
#        t = np.linspace(0,1,length_of_signal)
#        
#        cosinus_signal = np.cos(2*np.pi*f*t)
#        sinus_signal = np.sin(2*np.pi*f*t)
#
#        self.MplWidget.canvas.axes.clear()
#        self.MplWidget.canvas.axes.plot(t, cosinus_signal)
#        self.MplWidget.canvas.axes.plot(t, sinus_signal)
#        self.MplWidget.canvas.axes.legend(('cosinus', 'sinus'),loc='upper right')
#        self.MplWidget.canvas.axes.set_title('Cosinus - Sinus Signal')
#        self.MplWidget.canvas.draw()
        
    def timeChanged(self):
#        print(convertSecondsTohhmmss(self.tRange[self.time_slider.value()]))
#        print(self.time_slider.value())
#        print(self.mplWidget.canvas.axes)
        plotTraficolorOnAx(self.time_slider.value(), self.diagsXT, self.mplWidget.canvas.axes, self.drawMain)
        self.mplWidget.canvas.draw()
        self.update()
        
    def initLimits(self):
        self.mplWidget.canvas.axes.set_xlim(self.lims['xlim'])
        self.mplWidget.canvas.axes.set_ylim(self.lims['ylim'])
        
    def altCheckCallback(self):
        self.drawMain = not self.alt_check.isChecked()
        self.timeChanged()
        

#fileSimu, _ = QFileDialog.getOpenFileName(None, "Sélectionner un fichier de simulation", "", "Fichier Numpy (*.npy)")
#fileXT, _ = QFileDialog.getOpenFileName(None, "Sélectionner un fichier d'infos XT","", "Fichier Numpy (*.npy)")
#infos = {
#        'fileSimu' : fileSimu,
#        'fileXT' : fileXT
#        }
#window = TraficolorWidget(infos)