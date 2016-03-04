# -*- coding: utf-8 -*-
"""
Created on Thu Mar 03 15:51:13 2016

This script starts the image viewer GUI for VRmagic USB Cameras.

TO DO: -test with more than one camera and add error handling
       -implement the option to save data
       -implement the possibility to choose a different colormap for the image

@author: Michael

This file is part of beam-cam, a camera project to monitor and characterise laser beams.
Copyright (C) 2015 Christian Gross <christian.gross@mpq.mpg.de>, Timon Hilker <timon.hilker@mpq.mpg.de>, Michael Hoese <michael.hoese@physik.lmu.de>, and Konrad Viebahn <kv291@cam.ac.uk> 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

Please see the README.md file for a copy of the GNU General Public License, or otherwise find it on <http://www.gnu.org/licenses/>.
"""


import GaussBeamSimulation as Sim
reload(Sim)
import MathematicalTools as MatTools
reload(MatTools)
import VRmagicUsbCamAPI as VRmagicAPI
reload(VRmagicAPI)

from ctypes import *
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import pyqtgraph.ptime as ptime
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import sys
import time
import os

from ImageViewerTemplate import Ui_Form
# reload(ImageViewerTemplate)


'''
For RealData = False a simple simulation of a gaussian beam profile is started for testing purpses.
For RealData = True the USB hubs are scanned for available cameras. The camera can be choosen in the
according menu window. The images of the choosen camera are displayed and can be analysed.
'''
RealData = True