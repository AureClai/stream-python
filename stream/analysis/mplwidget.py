# -*- coding: utf-8 -*-
"""
Created on Thu May 16 07:49:05 2019

@author: aurelien.clairais
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout

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