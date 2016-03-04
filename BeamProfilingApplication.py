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



'''
Tools needed for main classes.
'''

def Create2DGaussian(RoiShape,*Parameters):
    '''Creates a 2D gaussian'''

    x = np.arange(RoiShape[1])
    y = np.arange(RoiShape[0])

    XY = np.meshgrid(x,y)

    XYflat = np.array(XY).reshape(2,RoiShape[1]*RoiShape[0]).T

    # params = [amplitude,sigmax,position[0],position[1],sigmay,rotationangle,offset]


    gaussflat = gaussian2(XYflat,*Parameters)
    gauss = np.array(gaussflat).reshape(ny,nx)

    return gauss

def ellipse(x,sigmax,sigmay):
    '''Creates an ellipse'''
    return np.sqrt((sigmay**2)*(1-((x**2)/(sigmax**2))))






class Ui_Window(object):
    '''Main application window.'''

    def __init__(self):

        self.app = QtGui.QApplication([])
        self.mainwin = QtGui.QMainWindow()

        self.menubar = QtGui.QMenuBar(self.mainwin)
        self.CreateMenuBar()

        self.win = QtGui.QWidget()

        self.mainwin.setCentralWidget(self.win)
        self.InitializeMainwin()

        self.ui = Ui_Form()
        self.ui.setupUi(self.win)


        # Create new image widget
        self.imagewidget = self.ui.plot

        # Add view box for displaying the image
        self.view = self.imagewidget.addViewBox()
        self.view.setAspectLocked(True)

        #Create image and add it to the view box
        self.img = pg.ImageItem(border='k')
        self.view.addItem(self.img)
        self.SetRangeViewbox()

        self.SetColorMap()

        self.roi = self.CreateROI()
        self.view.addItem(self.roi)
        self.peak = self.CreateMarkerBeamPos()
        self.view.addItem(self.peak)
        self.peakpos = self.CreateMarkerRefPeak()
        self.view.addItem(self.peakpos)
        self.contour = self.CreateBeamContour()
        self.view.addItem(self.contour)
        self.refcontour = self.CreateRefContour()
        self.view.addItem(self.refcontour)
        self.vline,self.hline = self.CreateCrossHair()
        view.addItem(self.vLine, ignoreBounds=True)
        view.addItem(self.hLine, ignoreBounds=True)


        self.p3 = CreateSumHorizontalPlot()
        self.amphist = CreateAmplitudeHist()
        self.timeplot = CreateTimePlot()

        # Go to the next row
        imagewidget.nextRow()

        self.p2 = CreateSumVerticalPlot()
        self.text = CreateBeamPropsTextBox()



        self.mainwin.show()





    def InitializeMainwin(self):
        '''
        Initializes Main Window
        '''

        self.mainwin.resize(1550, 1050)
        self.mainwin.setWindowTitle('Beam Profiling Tool')




    def CreateMenuBar(self):
        '''
        Creates the menu bar.
        '''

        fileMenu = self.menubar.addMenu('&File')
        exitAction = QtGui.QAction('Exit', self.mainwin)        
        exitAction.triggered.connect(QtGui.qApp.quit)
        fileMenu.addAction(exitAction)

        cameraMenu = self.menubar.addMenu('&Camera')
        refreshAction = QtGui.QAction('Refresh', cameraMenu)
        cameraMenu.addAction(refreshAction)
        cameraMenu.addSeparator()

        vrmagicMenu = cameraMenu.addMenu('VRmagic')
        

        ### TODO: Outsource this menu in other class!!!
        self.mainwin.connect(refreshAction,QtCore.SIGNAL('triggered()'), lambda: RefreshCameras(vrmagicMenu,self.ui))
        ###############################################

        self.mainwin.setMenuBar(self.menubar)


    def SetRangeViewbox(self):
        '''
        Setting the range of the Viewbox (self.view).
        '''

        self.view.setRange(QtCore.QRectF(0, 0, 754, 754))


    def SetColorMap(self):
        '''
        Setting the used colormap.
        '''

        #Add color (test)
        pos = np.array([0.0,0.5,1.0])
        color = np.array([[0,0,0,255],[255,128,0,255],[255,255,0,255]],dtype=np.ubyte)
        ## OR Copy from matplotlib
        pos = np.linspace(0,1,256)
        color = np.array([cm.afmhot(i) for i in range(256)])
        ####
        map1 = pg.ColorMap(pos,color)
        lut = map1.getLookupTable(0.0,1.0,256)
        self.img.setLookupTable(lut)
        self.img.setLevels([0,1])


    def CreateROI(self):
        '''
        Creates and initializes ROI.
        The roi is returned.
        '''
        roi = pg.ROI([160, 40], [400, 400],pen='b') # First lower left edge in pxl [x,y], then Size in pxl 
        roi.addScaleHandle([0.5, 1], [0.5, 0.5])
        roi.addScaleHandle([0, 0.5], [0.5, 0.5])
        roi.setZValue(10)  # Make sure ROI is drawn above
        bounds = QtCore.QRectF(0,0,753,479) # Set bounds of the roi
        roi.maxBounds = bounds

        return roi

    def CreateMarkerBeamPos(self):
        '''
        Create marker of the peak position of the beam and returns it.
        '''

        symbol = ['x']
        peak = pg.PlotDataItem(symbol = symbol,symbolPen='g',Pen=None,symbolBrush='g',symbolSize=25)
        peak.setZValue(20)

        return peak

    def CreateMarkerRefPeak(self):
        '''
        Create marker of the reference peak and returns it.
        '''

        symbol = ['x']
        peakpos = pg.PlotDataItem(symbol = symbol,symbolPen='r',Pen=None,symbolBrush='r',symbolSize=25)
        peakpos.setZValue(20)

        return peakpos

    def CreateBeamContour(self):
        '''
        Creates contour of the beam and returns it.
        '''

        contour = pg.PlotDataItem()
        contour.setPen('g')
        contour.setZValue(30)

        return contour

    def CreateRefContour(self):
        '''
        Creates contour of the reference beam and returns it.
        '''

        refcontour = pg.PlotDataItem()
        refcontour.setPen('r')
        refcontour.setZValue(25)

        return refcontour

    def CreateCrossHair(self):
        '''
        Creates cross hair and returns tuple of (vline,hline)
        '''

        vLine = pg.InfiniteLine(angle=90, movable=False)
        hLine = pg.InfiniteLine(angle=0, movable=False)

        return vline,hline

    def CreateSumHorizontalPlot(self):
        '''
        Add plot of the horizontal sum of the ROI and returns it.
        '''

        p3 = self.imagewidget.addPlot(colspan=1,title='Sum Horizontal')
        # p3.rotate(90)
        p3.setMaximumWidth(200)
        p3.setLabel('left',"Vertical Position",units='px')
        p3.setLabel('bottom',"Intensity",units='')

        return p3

    def CreateAmplitudeHist(self):
        '''
        Create histogram to visualize the amplitude and return it.
        '''

        amphist = self.imagewidget.addPlot(colspan=1,title='Amplitude<br>in ROI')
        amphist.setMaximumWidth(100)
        amphist.hideAxis('bottom')
        amphist.setLabel('left',"Amplitude",units='')

        return amphist

    def CreateTimePlot(self):
        '''
        Add plot of the time evolution of beam properties and returns it.
        '''

        timeplot = self.imagewidget.addPlot(colspan=1,title='Time Evolution')
        timeplot.setMaximumWidth(400)
        timeplot.setLabel('bottom', "Time", units='s')

        return timeplot

    def CreateSumVerticalPlot(self):
        '''
        Add plot of the vertical sum of the ROI and returns it.
        '''

        p2 = self.imagewidget.addPlot(colspan=1,title='Sum Vertical')
        p2.setMaximumHeight(200)
        p2.setLabel('bottom',"Horizontal Position",units='px')
        p2.setLabel('left',"Intensity",units='')

        return p2

    def CreateBeamPropsTextBox(self):
        '''
        Set text box for showing the beam properties and return text.
        '''

        texthtml = '<div style="text-align: center"><span style="color: #FFF; font-size: 16pt;">Beam Properties</span><br>\
        <span style="color: #FFF; font-size: 10pt;">Horizontal Position: 233,2</span><br>\
        <span style="color: #FFF; font-size: 10pt;">Vertical Position: 233,2</span><br>\
        <span style="color: #FFF; font-size: 10pt;">Horizontal Waist: 233,2</span><br>\
        <span style="color: #FFF; font-size: 10pt;">Vertical Waist: 233,2</span></div>'

        text = pg.TextItem(html=texthtml, anchor=(0.,0.), border='w', fill=(0, 0, 255, 100))
        textbox = self.imagewidget.addPlot()
        textbox.addItem(text)
        textbox.setMaximumWidth(200)
        textbox.setMaximumHeight(200)
        textbox.setMinimumWidth(200)
        textbox.setMinimumHeight(200)
        textbox.hideAxis('left')
        textbox.hideAxis('bottom')
        text.setTextWidth(190)
        text.setPos(0.02,0.75)

        return text







class App_Launcher(object):
    '''
    Class to launch the beam profiling application

    STILL TO IMPLEMENT:
    -handling of different manufacturers (camera types) via list

    '''


    def __init__(self):
        
        self.camera = None





    def InitializeCam(self,ui):
        '''Initializes the camera, update the exposure time and gain value fields'''
        
        ExpoTime = self.camera.GetExposureTime()
        ui.exposureSpin.setProperty("value", ExpoTime)
        GainValue = self.camera.GetGainValue()
        ui.gainSpin.setProperty("value", GainValue)
        # Switch off status LED
        # camera.SetStatusLED(camera.CamIndex,False)

    def CreateFile(self,name='test'):
        '''
        creates an empty .txt file; intended for saving
        not in use yet!
        '''
        if not os.path.exists(name):
            f = open(name+'.txt', 'w')
            f.close()
        else:
            print 'A file with this name already exists!'


    def ChangeCamera(self,ui,camindex=0):
        '''
        Stops old camera, starts new camera
        '''
        self.camera.StopCamera()
        self.camera.StartCamera(camindex=camindex)
        InitializeCam(self.camera,ui)

    def SearchCameras(self,+VRmMenu,ui):
        '''
        Searches all available supported cameras (of all supported types).
        Creates menu.
        Starts first available camera.
        '''

        global VRmCam

        totalcamnumber = 0
        camfound = False

        #################################################

        VRmCam = VRmagicAPI.VRmagicUSBCam_API()
        cameralist = VRmCam.CreateCameraList()
        numbercams = len(cameralist)
        totalcamnumber += numbercams
        
        if numbercams != 0:
            if not camfound:
                camera = VRmCam
                camera.StartCamera(camindex=0)
                InitializeCam(camera,ui)
                camfound = True
            for i in range(numbercams):
                name = cameralist[i]
                # testaction = QtGui.QAction(name, mainwin)
                changeaction = VRmMenu.addAction(name)
                mainwin.connect(changeaction,QtCore.SIGNAL('triggered()'), lambda i=i: ChangeCamera(camera,ui,camindex=i))
                VRmMenu.addAction(changeaction)
                
        
       
        if not camfound:
            camera='Simulation is used'
            print 'ERROR -- No cameras found!!'


    def RefreshCameras(self,VRmMenu,ui):
        '''
        Refreshes the camera list.
        '''


        self.camera.StopCamera()

        for i in VRmMenu.actions():
            VRmMenu.removeAction(i)

        
        SearchCameras(VRmMenu,ui)
        InitializeCam(self.camera,ui)












        































