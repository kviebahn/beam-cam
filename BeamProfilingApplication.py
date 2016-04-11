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

'''!!COMMENT OUT THE OPTIONS THAT YOU DO NOT WANT!!'''

# '''Using both camera types (VRmagic and Ximea)'''
# cameratypes = ['VRmagic USB','Ximea xiQ']
# cameraapinames = ['VRmagicUsbCamAPI','XimeaxiQCamAPI']


# '''Using VRmagic cameras only'''
# cameratypes = ['VRmagic USB']
# cameraapinames = ['VRmagicUsbCamAPI']


# '''Using Ximea xiQ cameras only'''
# cameratypes = ['Ximea xiQ']
# cameraapinames = ['XimeaxiQCamAPI']


'''Only use demo'''
cameratypes = []
cameraapinames = []

'''-----------------------------------------------'''



# import os
# os.environ.setdefault('LANG','en_US')

import importlib

'''
WORKAROUND FOR ERROR USING XIMEA CAMERA!!! TRY TO AVOID!!!
For Ximea Cameras, error when executing ROI.getArrayRegion().
in scipy.ndimage.filters fails to execute "from . import _ni_support"
According to test in debug mode: at this point __name__ = None.
-Maybe install pyqtgraph properly, no just copy folder.
-Or 64bit issue.
NOT UNDERSTOOD AT THE MOMENT!!
The same error occurs when trying to print numpy arrays.
'''
import scipy.ndimage.filters
'''----------------------------------------------------------'''
'''----------------------------------------------------------'''




import GaussBeamSimulation as Sim
reload(Sim)
import MathematicalTools as MatTools
reload(MatTools)
# import VRmagicUsbCamAPI as VRmagicAPI
# reload(VRmagicAPI)

# import XimeaxiQCamAPI as VRmagicAPI
# reload (VRmagicAPI)

# import XimeaxiQCamAPI as XimeaAPI
# reload (XimeaAPI)

# cameramodules = map(__import__, cameraapinames)
cameramodules = []
for i in cameraapinames:
    tempmodule = importlib.import_module(i)
    cameramodules.append(tempmodule)

for i in range(len(cameramodules)):
    reload (cameramodules[i])


# VRmagicAPI = cameramodules[0]
# reload (VRmagicAPI)



from ctypes import *
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import pyqtgraph.ptime as ptime
import pyqtgraph.exporters
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import sys
import time
import os
from PIL import Image
# from scipy.misc import toimage

from tempfile import NamedTemporaryFile
import shutil
import csv

from ImageViewerTemplate import Ui_Form
# reload(ImageViewerTemplate)






'''
For RealData = False a simple simulation of a gaussian beam profile is started for testing purpses.
For RealData = True the USB hubs are scanned for available cameras. The camera can be choosen in the
according menu window. The images of the choosen camera are displayed and can be analysed.
'''



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
        self.filemenu, self.cameramenu, self.settingsmenu, self.viewmenu = self.CreateMenuBar()

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
        self.vLine,self.hLine = self.CreateCrossHair()
        self.view.addItem(self.vLine, ignoreBounds=True)
        self.view.addItem(self.hLine, ignoreBounds=True)

        self.vLinecut,self.hLinecut = self.CreateCrossHairCut()
        self.view.addItem(self.vLinecut, ignoreBounds=True)
        self.view.addItem(self.hLinecut, ignoreBounds=True)
        self.vLinecut.hide()
        self.hLinecut.hide()
        self.ui.maxbeforeRadio.setChecked(False)
        self.ui.absmaxRadio.setChecked(False)
        self.ui.selfmaxRadio.setChecked(False)
        self.ui.maxbeforeRadio.setCheckable(False)
        self.ui.absmaxRadio.setCheckable(False)
        self.ui.selfmaxRadio.setCheckable(False)


        self.p3 = self.CreateSumHorizontalPlot()
        self.amphist = self.CreateAmplitudeHist()
        self.timeplot = self.CreateTimePlot()

        # Go to the next row
        self.imagewidget.nextRow()

        self.p2 = self.CreateSumVerticalPlot()
        self.text = self.CreateBeamPropsTextBox()
        self.satwarning = self.CreateSaturationWarningTextBox()



        self.mainwin.show()





    def InitializeMainwin(self):
        '''
        Initializes Main Window
        '''

        self.mainwin.resize(1550, 1050)
        self.mainwin.setWindowTitle('Beam Profiling Tool')




    def CreateMenuBar(self):
        '''
        Creates the menu bar and returns the camera menu.
        '''

        fileMenu = self.menubar.addMenu('&File')
        exitAction = QtGui.QAction('Exit', self.mainwin)
        exitAction.setShortcut('Ctrl+Q')    
        exitAction.setStatusTip('Exit application')    
        exitAction.triggered.connect(QtGui.qApp.quit)

        fileMenu.addAction(exitAction)
        fileMenu.addSeparator()

        cameraMenu = self.menubar.addMenu('&Camera')
        settingsMenu = self.menubar.addMenu('&Settings')
        viewMenu = self.menubar.addMenu('&View')
        # refreshAction = QtGui.QAction('Refresh', cameraMenu)
        # cameraMenu.addAction(refreshAction)
        # cameraMenu.addSeparator()

        
        

        ### TODO: Outsource this menu in other class!!!
        # vrmagicMenu = cameraMenu.addMenu('VRmagic')
        # self.mainwin.connect(refreshAction,QtCore.SIGNAL('triggered()'), lambda: RefreshCameras(vrmagicMenu,self.ui))
        ###############################################

        self.mainwin.setMenuBar(self.menubar)

        return fileMenu, cameraMenu, settingsMenu, viewMenu


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
        # pos = np.array([0.0,0.5,1.0])
        # color = np.array([[0,0,0,255],[255,128,0,255],[255,255,0,255]],dtype=np.ubyte)
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
        roi = pg.ROI([160, 40], [400, 400],pen='b',movable=False) # First lower left edge in pxl [x,y], then Size in pxl 
        roi.addScaleHandle([0.5, 1], [0.5, 0.5])
        roi.addScaleHandle([0, 0.5], [0.5, 0.5])
        roi.addTranslateHandle([0,1])
        roi.addTranslateHandle([1,1])
        roi.addTranslateHandle([0,0])
        roi.addTranslateHandle([1,1])
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

        return vLine,hLine

    def CreateCrossHairCut(self):
        '''
        Creates cross hair to mark cutted lines and returns tuple of (vlinecut,hlinecut)
        '''

        vLinecut = pg.InfiniteLine(angle=90, movable=False, pen='b')
        hLinecut = pg.InfiniteLine(angle=0, movable=False, pen='b')

        return vLinecut,hLinecut

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


    def CreateSaturationWarningTextBox(self):
        '''
        Create text box used for saturation warnings
        '''

        text = pg.TextItem(text="Warning: Saturated pixels", color='w', anchor=(0.,0.), border='w', fill='w')
        textbox = self.imagewidget.addPlot()
        textbox.addItem(text)
        textbox.setMaximumWidth(150)
        textbox.setMaximumHeight(200)
        textbox.setMinimumWidth(200)
        textbox.setMinimumHeight(200)
        textbox.hideAxis('left')
        textbox.hideAxis('bottom')
        text.setTextWidth(140)
        text.setPos(0.02,0.75)

        font = QtGui.QFont()
        font.setPointSize(20)
        text.setFont(font)
        return text
    


    # def MessageNoCamFound(self):
    #     '''
    #     Creates the messagebox that is shown when no camera is found.
    #     '''


    #     message = QtGui.QMessageBox()
    #     message.setIcon(QtGui.QMessageBox.Warning)
    #     message.setText("No cameras found!")
    #     message.setInformativeText("Please connect a supported camera to the computer and press the Search button.")
    #     message.setStandardButtons(QtGui.QMessageBox.Close)

    #     retval = message.exec_()
    #     print retval, "Retval"


############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################




class App_Launcher(object):
    '''
    Class to launch the beam profiling application

    STILL TO IMPLEMENT:
    -handling of different manufacturers (camera types) via list

    '''


    def __init__(self):
        '''
        Initializes the main class that runs the application.
        '''

        self.RealData = True


        self.gui = Ui_Window()
        self.InitializeSaveOptions()
        self.cameratypemenu = self.InitializeCamSearch()
        self.InitializeSettings()
        self.InitializeView()
        
        self.cameratypeobj = []
        self.cameratotallist = []
        self.camera = None
        if len(cameratypes) > 0:
            self.activecamtype = cameratypes[0]
        else:
            self.activecamtype = None
        self.activecamserial = None

        self.imagearray = None

        self.databuffersize = 40000
        self.databufferfilling = 0
        self.databuffer = self.CreateDataBuffer()
        
        self.rotangle = 0
        self.starttime = time.time()
        self.origroisize = None
        self.simulation = None

        self.starttimefile = time.localtime()

        # Start timer for the loop
        self.viewtimer = QtCore.QTimer()

        self.session = 1
        self.distancesession = 1
        self.autosavesession = 1

        self.autosavetimer = QtCore.QTimer()
        self.autosaveAction
        #???
        # self.VRmCam = None

        # The image size as tuple (width,height)
        self.imagesize = (754,754)

        self.colormap = cm.afmhot

        self.saturationvalue = None
        self.saturationthreshold = 5

        self.muperpxl = None

        self.path = self.InitializeDirectory()

        self.SearchCameras()

        self.amprange = None
        self.poshorrange = None
        self.posvertrange = None
        self.waisthorrange = None
        self.waistvertrange = None
        self.distrange = None


        self.runApp()





    def InitializeCam(self):
        '''Initializes the camera, update the exposure time and gain value fields'''

        success = self.InitializeCamProps()
        
        if not success:
            ExpoTime = self.camera.GetExposureTime()
            print ExpoTime, "ExpoTime"
            # self.gui.ui.exposureSpin.setProperty("value", ExpoTime)
            self.gui.ui.exposureSpin.setValue(ExpoTime)
        ExpoTimeRange = self.camera.GetExposureTimeRange()
        self.gui.ui.exposureSpin.setRange(ExpoTimeRange[0],ExpoTimeRange[1])
        # This applies only to steps shown in GUI (for better handling);
        # internal stepsize of device is different.
        # Can be modified by changing the division factor.
        ExpoSteps = (ExpoTimeRange[1] - ExpoTimeRange[0])/50
        ExpoStepsReal = self.camera.GetExposureTimeSteps()
        if ExpoStepsReal >= ExpoSteps:
            ExpoSteps = ExpoStepsReal
        self.gui.ui.exposureSpin.setSingleStep(ExpoSteps) 

        if not success:
            GainValue = self.camera.GetGainValue()
            print GainValue, "Gain Value"
            # self.gui.ui.gainSpin.setProperty("value", GainValue)
            self.gui.ui.gainSpin.setValue(GainValue)
        GainRange = self.camera.GetGainRange()
        self.gui.ui.gainSpin.setRange(GainRange[0],GainRange[1])
        # This applies only to steps shown in GUI (for better handling);
        # internal stepsize of device is different.
        # Can be modified by changing the division factor.
        GainSteps = (GainRange[1] - GainRange[0])/50
        GainStepsReal = self.camera.GetGainSteps()
        if GainStepsReal >= GainSteps:
            GainSteps = GainStepsReal
        self.gui.ui.gainSpin.setSingleStep(GainSteps) 


        self.imagesize = self.camera.GetImageSize()
        self.InitializeViewBoxSize()

        self.gui.roi.setPos([int(self.imagesize[0]/8.),int(self.imagesize[1]/8.)],finish=False)
        self.gui.roi.setSize([int(self.imagesize[0]*3/4.),int(self.imagesize[1]*3/4.)],finish=False)

        self.saturationvalue = self.camera.GetSaturationValue()
        # print self.saturationvalue, "Saturation Value"
        # Switch off status LED
        # camera.SetStatusLED(camera.CamIndex,False)

        





    def InitializeCamProps(self):
        '''
        If a CameraConfig.csv file exists, this method adjusts the settings of the camera (only if
        the camera serial occurs in the config file).
        '''

        if os.path.exists('CameraConfig.csv'):
            types,serials = np.loadtxt("CameraConfig.csv",delimiter=",",dtype=str,usecols=(0,1),unpack=True)
            expo,gain = np.loadtxt("CameraConfig.csv",delimiter=",",dtype=float,usecols=(2,3),unpack=True)

            if isinstance(types,basestring):
                types = np.array([types])
            if isinstance(serials,basestring):
                serials = np.array([serials])
            if isinstance(expo,float):
                expo = np.array([expo])
            if isinstance(gain,float):
                gain = np.array([gain])
            index = np.where(serials == self.activecamserial)

            # print index, "Index"

            if len(index[0]) == 1:
                # print expo, "New expo and gain"
                self.camera.SetExposureTime(expo[index])
                ExpoTime = self.camera.GetExposureTime()
                self.gui.ui.exposureSpin.setProperty("value", ExpoTime)
                self.camera.SetGainValue(self.gui.ui.gainSpin.value())
                GainValue = self.camera.GetGainValue()
                self.gui.ui.gainSpin.setProperty("value", GainValue)
                self.updatecameraconfigfile()
                
                return True
            elif len(index[0]) > 1:
                print "Detection error: Same serial appears several times!"
                return False
            else:
                return False
        else:
            return False




    def InitializeViewBoxSize(self):
        '''
        Adapts the viewbox size to the actual image and changes other image size dependent settings.
        '''

        self.gui.view.setRange(QtCore.QRectF(0, 0, self.imagesize[0], self.imagesize[1]))

        self.gui.ui.x0Spin.setRange(0.,self.imagesize[0])
        self.gui.ui.y0Spin.setRange(0.,self.imagesize[1])

        bounds = QtCore.QRectF(0,0,self.imagesize[0]-1,self.imagesize[1]-1)
        self.gui.roi.maxBounds = bounds

        roisize = self.gui.roi.size()
        roipos = self.gui.roi.pos()

        if roisize[0] >= self.imagesize[0] or roisize[1] >= self.imagesize[1]:
            self.gui.roi.setSize([int(self.imagesize[0]/2.),int(self.imagesize[1]/2.)],finish=False)
        if roipos[0] >= (self.imagesize[0]-roisize[0]) or roipos[1] >= (self.imagesize[1]-roisize[1]):
            self.gui.roi.setPos([int(self.imagesize[0]/4.),int(self.imagesize[1]/4.)],finish=False)
            self.gui.roi.setSize([int(self.imagesize[0]/2.),int(self.imagesize[1]/2.)],finish=False)


    # def CreateFile(self,name='test'):
    #     '''
    #     creates an empty .txt file; intended for saving
    #     not in use yet!
    #     '''
    #     if not os.path.exists(name):
    #         f = open(name+'.txt', 'w')
    #         f.close()
    #     else:
    #         print 'A file with this name already exists!'

    def InitializeDirectory(self):
        '''
        Creates a "Data" folder as default directory for saving data.
        '''

        datadir = os.path.join(os.getcwd(),'Data')

        if not os.path.exists(datadir):
            os.makedirs(datadir)

        return datadir


    def ChangeCamera(self,camindex=0):
        '''
        Stops old camera, starts new camera.
        '''
        # print camindex, "Camindex"
        self.camera.StopCamera()

        totcamnr = 0
        camset = False
        for i in range(len(cameratypes)):
            # print "Enter Loop"
            # print "index before", len(self.cameratotallist[i])+totcamnr-1
            if (len(self.cameratotallist[i])+totcamnr) > camindex:
                # print "index", len(self.cameratotallist[i])+totcamnr-1
                if not camset:
                    self.camera = self.cameratypeobj[i]
                    # print self.camera, "Check Cam"
                    camindex = camindex-totcamnr
                    camset = True

                    self.activecamtype = cameratypes[i]
                    self.activecamserial = self.cameratotallist[i][camindex]
                else: 
                    pass
                
            else:
                totcamnr += len(self.cameratotallist[i])
                # print "Totcamnr:", totcamnr

        # print "Camera", self.camera

        self.camera.StartCamera(camindex=camindex)
        self.InitializeCam()


    def InitializeCamSearch(self):
        '''
        This method initializes the camera menu and return the menu for each camera type.
        '''

        refreshAction = QtGui.QAction('Refresh', self.gui.cameramenu)
        refreshAction.setShortcut('Ctrl+N')
        self.gui.cameramenu.addAction(refreshAction)
        self.gui.cameramenu.addSeparator()

        cameratypemenu = []
        for i in range(len(cameratypes)):
            cameratypemenutemp = self.gui.cameramenu.addMenu(cameratypes[i])
            cameratypemenu.append(cameratypemenutemp)
        
        # vrmagicMenu = self.gui.cameramenu.addMenu('VRmagic')

        self.gui.mainwin.connect(refreshAction,QtCore.SIGNAL('triggered()'), lambda: self.RefreshCameras())

        return cameratypemenu


    def InitializeSaveOptions(self):
        '''
        Initializes the save options in the file menu.
        '''

        setPathAction = QtGui.QAction('Change Directory', self.gui.filemenu)
        setPathAction.setShortcut('Ctrl+D')
        self.gui.filemenu.addAction(setPathAction)
        self.gui.mainwin.connect(setPathAction,QtCore.SIGNAL('triggered()'), lambda: self.SetPath())

        self.gui.filemenu.addSeparator()

        saveImageAction = QtGui.QAction('Save Image', self.gui.filemenu)
        saveImageAction.setShortcut('Ctrl+I')
        self.gui.filemenu.addAction(saveImageAction)
        self.gui.mainwin.connect(saveImageAction,QtCore.SIGNAL('triggered()'), lambda: self.SaveImage())

        saveImageAsAction = QtGui.QAction('Save Image as..', self.gui.filemenu)
        self.gui.filemenu.addAction(saveImageAsAction)
        self.gui.mainwin.connect(saveImageAsAction,QtCore.SIGNAL('triggered()'), lambda: self.SaveImageAs())

        saveImageRawAction = QtGui.QAction('Save Image Raw Data', self.gui.filemenu)
        saveImageRawAction.setShortcut('Ctrl+K')
        self.gui.filemenu.addAction(saveImageRawAction)
        self.gui.mainwin.connect(saveImageRawAction,QtCore.SIGNAL('triggered()'), lambda: self.SaveImageRaw())

        saveImageRawAsAction = QtGui.QAction('Save Image Raw Data as..', self.gui.filemenu)
        self.gui.filemenu.addAction(saveImageRawAsAction)
        self.gui.mainwin.connect(saveImageRawAsAction,QtCore.SIGNAL('triggered()'), lambda: self.SaveImageRawAs())

        saveWidgetAction = QtGui.QAction('Save Image Widget', self.gui.filemenu)
        saveWidgetAction.setShortcut('Ctrl+W')
        self.gui.filemenu.addAction(saveWidgetAction)
        self.gui.mainwin.connect(saveWidgetAction,QtCore.SIGNAL('triggered()'), lambda: self.SaveImageWidget())

        saveWidgetAsAction = QtGui.QAction('Save Image Widget as..', self.gui.filemenu)
        self.gui.filemenu.addAction(saveWidgetAsAction)
        self.gui.mainwin.connect(saveWidgetAsAction,QtCore.SIGNAL('triggered()'), lambda: self.SaveImageWidgetAs())

        saveDataBufferAction = QtGui.QAction('Save Data Buffer', self.gui.filemenu)
        saveDataBufferAction.setShortcut('Ctrl+B')
        self.gui.filemenu.addAction(saveDataBufferAction)
        self.gui.mainwin.connect(saveDataBufferAction,QtCore.SIGNAL('triggered()'), lambda: self.SaveDataBuffer())

        saveDataBufferAsAction = QtGui.QAction('Save Data Buffer as..', self.gui.filemenu)
        self.gui.filemenu.addAction(saveDataBufferAsAction)
        self.gui.mainwin.connect(saveDataBufferAsAction,QtCore.SIGNAL('triggered()'), lambda: self.SaveDataBufferAs())

        saveActualBeamPropsAction = QtGui.QAction('Save Current Beam Properties', self.gui.filemenu)
        saveActualBeamPropsAction.setShortcut('Ctrl+S')
        self.gui.filemenu.addAction(saveActualBeamPropsAction)
        self.gui.mainwin.connect(saveActualBeamPropsAction,QtCore.SIGNAL('triggered()'), lambda: self.SaveDataSimple())

        saveActualDataDistAction = QtGui.QAction('Save Properties with Distance Stamp', self.gui.filemenu)
        saveActualDataDistAction.setShortcut('Ctrl+X')
        self.gui.filemenu.addAction(saveActualDataDistAction)
        self.gui.mainwin.connect(saveActualDataDistAction,QtCore.SIGNAL('triggered()'), lambda: self.SaveDataDistanceStamp())

        self.autosaveAction = QtGui.QAction('Autosave', self.gui.filemenu)
        self.autosaveAction.setShortcut('Ctrl+A')
        self.gui.filemenu.addAction(self.autosaveAction)
        self.autosaveAction.setCheckable(True)
        # autosaveAction.triggered.connect(self.AutosavePressAction(autosaveAction.isChecked()))
        self.gui.mainwin.connect(self.autosaveAction,QtCore.SIGNAL('triggered()'), lambda: self.AutosavePressAction())

        self.gui.filemenu.addSeparator()

        newSessionAction = QtGui.QAction('New Session', self.gui.filemenu)
        self.gui.filemenu.addAction(newSessionAction)
        self.gui.mainwin.connect(newSessionAction,QtCore.SIGNAL('triggered()'), lambda: self.NewDataAcquisitionSession())

        newDistSessionAction = QtGui.QAction('New Distance Session', self.gui.filemenu)
        self.gui.filemenu.addAction(newDistSessionAction)
        self.gui.mainwin.connect(newDistSessionAction,QtCore.SIGNAL('triggered()'), lambda: self.NewDistanceSession())


    def SetPath(self):
        '''
        Sets the new path when changing the directory.
        '''

        dialog = QtGui.QFileDialog(directory=self.path)
        pathtemp = str(QtGui.QFileDialog.getExistingDirectory(dialog, "Select Directory"))

        if os.path.isdir(pathtemp):
            self.path = pathtemp

        # print "Path", self.path


    def EnterFileName(self):
        '''
        Opens a window to enter a file name.
        '''

        name,ok = QtGui.QInputDialog.getText(self.gui.win,"Save as ...",\
            "Enter name for data to be saved:")

        if ok:
            return ok, name
        else:
            return ok, None




    def SaveImage(self,name=None):
        '''
        Saves the image as .png file
        '''

        # color = np.array([[0,0,0,255],[255,128,0,255],[255,255,0,255]],dtype=np.ubyte)
        # color = cm.hot
        # img =toimage(self.imagearray,pal=color,mode='P')
        # img =toimage(self.imagearray,mode='L')

        # print name, 'Name'

        if name == None:
            # t = time.mktime(t)
            name = time.strftime("%b-%d-%Y_%H-%M-%S",time.localtime())
            name = "Image" + name
        else:
            name = str(name)

        # Change colormap here (any matplotlib colormap possible)
        # if self.RealData:
        #     imgraw = np.uint8(cm.afmhot(self.imagearray*1./self.saturationvalue)*self.saturationvalue)
        # if not self.RealData:
        #     imgraw = np.uint8(cm.afmhot(self.imagearray*1./255.)*255)


        # cmap = cm.afmhot
        cmap = self.colormap

        m = cm.ScalarMappable(norm=None, cmap=cmap)
        if self.RealData:
            colormapped = m.to_rgba(self.imagearray/float(self.saturationvalue))*self.saturationvalue
        if not self.RealData:
            colormapped = m.to_rgba(self.imagearray/255.)*255
        img = Image.fromarray(np.uint8(colormapped))


        # img = Image.fromarray(imgraw)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img.save(os.path.join(self.path,name + '.png'))


        # exporter = pg.exporters.ImageExporter(self.gui.img)
        # exporter.export('test.png')

        # self.gui.view.export('test.png')

    def SaveImageAs(self):
        '''
        Saves the image as .png with self defined name.
        '''
        
        ok,name = self.EnterFileName()
        if ok:
            self.SaveImage(name=name)


    def SaveImageRaw(self,name=None):
        '''
        Saves raw data of image as .npy.
        '''

        if name == None:
            # t = time.mktime(t)
            name = time.strftime("%b-%d-%Y_%H-%M-%S",time.localtime())
            name = "ImageRawData" + name
        else:
            name = str(name)

        np.save(os.path.join(self.path,name),self.imagearray)

    def SaveImageRawAs(self):
        '''
        Saves raw data of image as .npy with self defined name.
        '''
        
        ok,name = self.EnterFileName()
        if ok:
            self.SaveImageRaw(name=name)


    def SaveImageWidget(self,name=None):
        '''
        Saves a part of the image widget as .png.
        '''

        if name == None:
            name = time.strftime("%b-%d-%Y_%H-%M-%S",time.localtime())
            name = "Widget" + name
        else:
            name = str(name)

        recti = self.gui.p2.boundingRect()
        # rectii = self.gui.text.boundingRect()
        rectii = self.gui.p3.boundingRect()

        # viewrange = self.gui.view.viewRange()
        # viewwidth = viewrange[0][1]-viewrange[0][0]

        # recti = recti.toRect()
        # rectii = rectii.toRect()

        # print recti.width(), "image width"
        # print rectii.width(), "plot width"
        # print viewwidth, "view width"

        width = recti.width() + rectii.width() + 15 # Number ensures nicer images. Can be changed individually.

        pic = QtGui.QPixmap.grabWidget(self.gui.ui.plot,width=width)
        pic.save(os.path.join(self.path,name + '.png'))

    def SaveImageWidgetAs(self):
        '''
        Saves a part of the image widget as .png with self defined name.
        '''

        ok,name = self.EnterFileName()
        if ok:
            self.SaveImageWidget(name=name)



    def SaveDataBuffer(self,name=None):
        '''
        Saves the databuffer as .csv.
        '''

        if name == None:
            name = time.strftime("%b-%d-%Y_%H-%M-%S",time.localtime())
            name = "DataBuffer-" + name
        else:
            name = str(name)

        np.savetxt(os.path.join(self.path,name + '.csv'),self.databuffer.T,fmt='%.7e',header='Index, Timestamp, Amplitude, Horizontal Position, Vertical Position, Horizontal Waist, Vertical Waist, Distance to Rererence Beam')

    def SaveDataBufferAs(self):
        '''
        Saves the databuffer as .csv with self defined name.
        '''

        ok,name = self.EnterFileName()
        if ok:
            self.SaveDataBufferAs(name=name)

    def SaveDataSimple(self):
        '''
        Appends the current beam properties to a .csv file and creates this if it doesn't exist yet.
        '''

        name = "BeamData-" + str(self.session) + "-" + time.strftime("%b-%d-%Y_%H-%M-%S",self.starttimefile)

        if not os.path.isfile(os.path.join(self.path,name + '.csv')):

            datatowrite = np.copy(self.databuffer[:,-1])
            datatowrite[0] = 1.0
            # print datatowrite, "Written data"
            np.savetxt(os.path.join(self.path,name + '.csv'),datatowrite[None],fmt='%.7e',header='Index, Timestamp, Amplitude, Horizontal Position, Vertical Position, Horizontal Waist, Vertical Waist, Distance to Rererence Beam')

        else:
            tempfile = NamedTemporaryFile(delete=False)

            olddata = np.genfromtxt(os.path.join(self.path,name + '.csv'),delimiter=' ',dtype=float)
            datatoadd = np.copy(self.databuffer[:,-1])
            newdata = np.vstack((olddata,datatoadd))
            newdata[-1,0] = newdata[-2,0] + 1
            # print newdata, 'Newdata'

            np.savetxt(tempfile.name + '.csv',newdata,header='Index, Timestamp, Amplitude, Horizontal Position, Vertical Position, Horizontal Waist, Vertical Waist, Distance to Rererence Beam')

            shutil.move(tempfile.name + '.csv', os.path.join(self.path,name + '.csv'))


    def SaveDataDistanceStamp(self):
        '''
        Appends the current beam properties with a distance stamp (has to be entered) to a .csv file and
        creates this if it doesn't exist yet.
        '''

        number,ok = QtGui.QInputDialog.getDouble(self.gui.win,"Save Beam Properties with Distance Stamp",\
            "Enter a distance stamp:",decimals=4)

        if ok:
            name = "BeamDataDist-" + str(self.distancesession) + "-" + time.strftime("%b-%d-%Y_%H-%M-%S",self.starttimefile)

            if not os.path.isfile(os.path.join(self.path,name + '.csv')):

                datatowrite = np.copy(self.databuffer[:,-1])
                datatowrite[0] = 1.0
                datatowrite = np.append(number,datatowrite)
                # print datatowrite, "Written data"
                np.savetxt(os.path.join(self.path,name + '.csv'),datatowrite[None],fmt='%.7e',header='Distance Stamp, Index, Timestamp, Amplitude, Horizontal Position, Vertical Position, Horizontal Waist, Vertical Waist, Distance to Rererence Beam')

            else:
                tempfile = NamedTemporaryFile(delete=False)

                olddata = np.genfromtxt(os.path.join(self.path,name + '.csv'),delimiter=' ',dtype=float)
                datatoadd = np.copy(self.databuffer[:,-1])
                datatoadd = np.append(number,datatoadd)
                newdata = np.vstack((olddata,datatoadd))
                newdata[-1,1] = newdata[-2,1] + 1
                # print newdata, 'Newdata'

                np.savetxt(tempfile.name + '.csv',newdata,header='Distance Stamp, Index, Timestamp, Amplitude, Horizontal Position, Vertical Position, Horizontal Waist, Vertical Waist, Distance to Rererence Beam')

                shutil.move(tempfile.name + '.csv', os.path.join(self.path,name + '.csv'))

    def AutosavePressAction(self):
        '''
        Manages start and stop of autosave.
        '''

        if self.autosaveAction.isChecked():
            self.StartAutosave()
        else:
            self.StopAutosave()

    def StartAutosave(self):
        '''
        Starts autosave: the current beam props are saved in a .csv file after a specified time interval.
        '''

        number,ok = QtGui.QInputDialog.getDouble(self.gui.win,"Start Autosave",\
            "Enter a time interval (in seconds):",decimals=3,min=0.001,value=1.000)

        if ok:
            self.autosavetimer.timeout.connect(self.AutosaveBeamProps)
            self.autosavetimer.start(int(number*1000))
            self.AutosaveBeamProps()
        else:
            self.autosaveAction.setChecked(False)
        

    def StopAutosave(self):
        '''
        Stop autosave.
        '''

        if self.autosavetimer.isActive():
        # if True:
            self.autosavetimer.stop()
            self.autosavesession += 1
        



    def AutosaveBeamProps(self):
        '''
        The current beam props are saved in a .csv file after a specified time interval.
        '''

        timeinterval = self.autosavetimer.interval()/1000.

        name = "AutosaveBeamProps-" + str(self.autosavesession) + "-" + time.strftime("%b-%d-%Y_%H-%M-%S",self.starttimefile)

        if not os.path.isfile(os.path.join(self.path,name + '.csv')):

            datatowrite = np.copy(self.databuffer[:,-1])
            # print self.databuffer[:,-1], "Databuffer Time 1"
            datatowrite[0] = 0.0
            datatowrite[1] = datatowrite[0]*timeinterval
            # print self.databuffer[:,-1], "Databuffer Time 2"
            # print datatowrite, "Written data"
            np.savetxt(os.path.join(self.path,name + '.csv'),datatowrite[None],fmt='%.7e',header='Index, Timestamp(s), Amplitude, Horizontal Position, Vertical Position, Horizontal Waist, Vertical Waist, Distance to Rererence Beam')

        else:
            tempfile = NamedTemporaryFile(delete=False)

            olddata = np.genfromtxt(os.path.join(self.path,name + '.csv'),delimiter=' ',dtype=float)
            datatoadd = np.copy(self.databuffer[:,-1])
            newdata = np.vstack((olddata,datatoadd))
            newdata[-1,0] = newdata[-2,0] + 1
            newdata[-1,1] = newdata[-1,0]*timeinterval
            # print newdata, 'Newdata'

            np.savetxt(tempfile.name + '.csv',newdata,header='Index, Timestamp(s), Amplitude, Horizontal Position, Vertical Position, Horizontal Waist, Vertical Waist, Distance to Rererence Beam')

            shutil.move(tempfile.name + '.csv', os.path.join(self.path,name + '.csv'))

    def NewDataAcquisitionSession(self):
        '''
        Starts a new file to save current beam props.
        '''

        self.session += 1

    def NewDistanceSession(self):
        '''
        Starts a new file to save current beam props with distance stamp.
        '''

        self.distancesession += 1



    def InitializeSettings(self):
        '''
        Initializes the settings menu.
        '''

        saturationMenu = self.gui.settingsmenu.addMenu('Saturation')
        thresholdAction = QtGui.QAction('Threshold',saturationMenu)
        saturationMenu.addAction(thresholdAction)

        buffersizeAction = QtGui.QAction('Buffer Size',self.gui.settingsmenu)
        self.gui.settingsmenu.addAction(buffersizeAction)

        clearbufferAction = QtGui.QAction('Clear Buffer',self.gui.settingsmenu)
        self.gui.settingsmenu.addAction(clearbufferAction)


        self.gui.mainwin.connect(thresholdAction,QtCore.SIGNAL('triggered()'),\
         lambda: self.AdjustSaturationThreshold())
        self.gui.mainwin.connect(buffersizeAction,QtCore.SIGNAL('triggered()'),\
         lambda: self.AdjustBufferSize())
        self.gui.mainwin.connect(clearbufferAction,QtCore.SIGNAL('triggered()'),\
         lambda: self.ClearBuffer())


    def InitializeView(self):
        '''
        Initializes the View menu.
        '''

        rotatemenu = self.gui.viewmenu.addMenu('Rotate View')
        clockwiseAction = QtGui.QAction('Clockwise',rotatemenu)
        clockwiseAction.setShortcut('Ctrl+R')
        rotatemenu.addAction(clockwiseAction)
        counterclockwiseAction = QtGui.QAction('Counterclockwise',rotatemenu)
        counterclockwiseAction.setShortcut('Ctrl+L')
        rotatemenu.addAction(counterclockwiseAction)

        self.gui.mainwin.connect(clockwiseAction,QtCore.SIGNAL('triggered()'), lambda: self.updaterotanglecw())
        self.gui.mainwin.connect(counterclockwiseAction,QtCore.SIGNAL('triggered()'), lambda: self.updaterotangleccw())


        colorAction = QtGui.QAction('Colormap',self.gui.viewmenu)
        self.gui.viewmenu.addAction(colorAction)
        self.gui.mainwin.connect(colorAction,QtCore.SIGNAL('triggered()'), lambda: self.ChangeColorMap())

        scalingAction = QtGui.QAction('Scaling',self.gui.viewmenu)
        self.gui.viewmenu.addAction(scalingAction)
        self.gui.mainwin.connect(scalingAction,QtCore.SIGNAL('triggered()'), lambda: self.AdjustScaling())






    def AdjustScaling(self):
        '''
        Adjusts the scaling according to pixelsize.
        '''

        oldmuperpxl = self.muperpxl
        number,ok = QtGui.QInputDialog.getDouble(self.gui.win,"Adjust Scaling","Enter the value for scaling in micrometer per pixel:",decimals=3)
        
        if ok:
            self.muperpxl = number
            self.gui.p2.setLabel('bottom',"Horizontal Position",units='mu m')
            self.gui.p3.setLabel('left',"Vertical Position",units='mu m')
            if oldmuperpxl == None:
                self.databuffer[3:,] = self.RescaleParameter(self.databuffer[3:,])
            # print self.muperpxl


    def RescaleParameter(self,parameter):
        '''
        Rescales a parameter (in pixel) using the muperpxl variable.
        Returns parameter in micrometer.
        '''

        retvalue = parameter*self.muperpxl
        return retvalue




    def AdjustSaturationThreshold(self):
        '''
        Adjusts the saturation threshold (minimal number of pixel that has to be saturated 
        before warning shows up).
        '''

        number,ok = QtGui.QInputDialog.getInt(self.gui.win,"Adjust Saturation Threshold",\
            "Enter new minimal pixel number:",value=self.saturationthreshold)
        
        if ok:
            self.saturationthreshold = number


    def AdjustBufferSize(self):
        '''
        Changes the size of the data buffer
        '''

        number,ok = QtGui.QInputDialog.getInt(self.gui.win,"Adjust Size of Data Buffer",\
            "Enter new length of data buffer (number of saved values):",value=self.databuffersize,min=10,max=10000000)

        if ok:
            oldbuffersize = self.databuffersize
            self.databuffersize = number
            newdatabuffer = self.CreateDataBuffer()
            if self.databuffersize < oldbuffersize:
                newdatabuffer[1:,] = self.databuffer[1:,-self.databuffersize:]
            elif self.databuffersize == oldbuffersize:
                newdatabuffer[1:,] = self.databuffer[1:,]
            elif self.databuffersize > oldbuffersize:
                newdatabuffer[1:,-oldbuffersize:] = self.databuffer[1:,]
            self.databuffer = newdatabuffer

    def ClearBuffer(self):
        '''
        Clears the databuffer.
        '''

        self.databuffer = self.CreateDataBuffer()
        self.databufferfilling = 0


    def ChangeColorMap(self):
        '''
        Changing the used colormap.
        '''
        # For adding new colormaps: append the matplotlib.cm name in the cmaps list and specify a name,
        # displayed in the menu in cmapnames.
        cmaps = [cm.afmhot,cm.binary,cm.jet,cm.cool,cm.copper,cm.spectral,cm.winter,cm.autumn]
        cmapnames = ['afmhot','binary','jet','cool','copper','spectral','winter','autumn']

        act = cmaps.index(self.colormap)

        item,ok = QtGui.QInputDialog.getItem(self.gui.win,"Change the Colormap",\
            "Choose a colormap:",cmapnames,act,False)

        if ok:
            chosen = cmapnames.index(item)
            self.colormap = cmaps[chosen]

            pos = np.linspace(0,1,256)
            color = np.array([self.colormap(i) for i in range(256)])
            ####
            map1 = pg.ColorMap(pos,color)
            lut = map1.getLookupTable(0.0,1.0,256)
            self.gui.img.setLookupTable(lut)
            self.gui.img.setLevels([0,1])




    def SearchCameras(self):
        '''
        Searches all available supported cameras (of all supported types).
        Creates menu.
        Starts first available camera.
        '''
        # del self.camera

        totalcamnumber = 0
        camfound = False

        self.cameratypeobj = []
        self.cameratotallist = []


        for i in range(len(self.cameratypemenu)):
            cameratypeobjtemp = cameramodules[i].CameraTypeSpecific_API()
            self.cameratypeobj.append(cameratypeobjtemp)

            # print self.cameratypeobj

        for obj in self.cameratypeobj:
            tempcamlist = obj.CreateCameraList()
            self.cameratotallist.append(tempcamlist)
            totalcamnumber += len(tempcamlist)
            # del tempcamlist

        # o1 = self.cameratypeobj[0]
        # o2 = self.cameratypeobj[1]

        # o1 = cameramodules[0].CameraTypeSpecific_API()
        # o2 = cameramodules[1].CameraTypeSpecific_API()
        
        # o1 = VRmagicAPI.CameraTypeSpecific_API()
        # o2 = XimeaAPI.CameraTypeSpecific_API()

        # l2 = o2.CreateCameraList()
        # self.cameratotallist.append(l2)
        # l1 = o1.CreateCameraList()
        # self.cameratotallist.append(l1)
        # l2 = o2.CreateCameraList()
        # self.cameratotallist.append(l2)


        # self.cameratotallist = map(cameratypeobj[i].CreateCameraList,cameratypeobj)

        # print self.cameratotallist, "Total Camera List"

        self.RealData = True

        if totalcamnumber != 0:
            if self.activecamtype != None:
                camtypeindex = cameratypes.index(self.activecamtype)
            else:
                camtypeindex = 0
            if self.activecamserial in self.cameratotallist[camtypeindex]:
                self.camera = self.cameratypeobj[camtypeindex]
                self.camera.StartCamera(camindex=self.cameratotallist[camtypeindex].index(self.activecamserial))
                self.activecamtype = self.activecamtype
                self.activecamserial = self.activecamserial
                self.InitializeCam()
                camfound = True

            for i in range(len(cameratypes)):
                if not camfound:
                    if len(self.cameratotallist[i]) != 0:
                        self.camera = self.cameratypeobj[i]
                        self.camera.StartCamera(camindex=0)
                        self.activecamtype = cameratypes[i]
                        self.activecamserial = self.cameratotallist[i][0]
                        self.InitializeCam()
                        camfound = True

                for j in range(len(self.cameratotallist[i])):
                    name = self.cameratotallist[i][j]
                    changeaction = self.cameratypemenu[i].addAction(name)
                    self.gui.mainwin.connect(changeaction,QtCore.SIGNAL('triggered()'), lambda i=i: self.ChangeCamera(camindex=i))
                    self.cameratypemenu[i].addAction(changeaction)


        # if self.cameratypemenu[0].isVisible():
        #     print "IS VISIBLE!!"





        #################################################   OLD PROCEDURE!!
        # del self.cameratypeobj
        # totalcamnumber = 0

        # VRmCam = VRmagicAPI.CameraTypeSpecific_API()
        # VRmCam = self.cameratypeobj[0]
        # cameralist = VRmCam.CreateCameraList()
        # cameralist = self.cameratotallist[0]
        # print "Length Cameralist", len(cameralist)
        # numbercams = len(cameralist)
        # totalcamnumber += numbercams

        # print "Camera before", VRmCam
        
        # print numbercams, 'Number Cams'

        # self.RealData = True

        # ADD HANDLING IF NO CAMERA IS AVAILABLE/PLUGGED TO THE PC
        # if numbercams != 0:
        #     if not camfound:
        #         self.camera = VRmCam
        #         self.camera.StartCamera(camindex=0)
        #         self.InitializeCam()
        #         camfound = True
        #         del VRmCam
        #     for i in range(numbercams):
        #         name = cameralist[i]
        #         # testaction = QtGui.QAction(name, mainwin)
        #         changeaction = self.VRmMenu.addAction(name)
        #         self.gui.mainwin.connect(changeaction,QtCore.SIGNAL('triggered()'), lambda i=i: self.ChangeCamera(camindex=i))
        #         self.VRmMenu.addAction(changeaction)
                
        
        if camfound:
            self.viewtimer.start()
        if not camfound:
            self.camera = None
            self.activecamtype = None
            self.activecamserial = None
            self.MessageNoCamFound()
            
            # print 'ERROR -- No cameras found!!'

        # print "Camera", self.camera


    def RefreshCameras(self):
        '''
        Refreshes the camera list.
        '''

        if self.camera != None:
            self.viewtimer.stop()
            if self.RealData:
                self.camera.StopCamera()

            for i in range(len(cameratypes)):
                for j in self.cameratypemenu[i].actions():
                    self.cameratypemenu[i].removeAction(j)

        
        self.SearchCameras()
        # self.InitializeCam()




    def StartDemo(self):
        '''
        Starts a demo.
        '''

        self.RealData = False
        self.camera = "Simulation in use"
        self.simulation = Sim.GaussBeamSimulation()
        self.simulation.CreateImages()
        self.imagesize = (754,480)
        self.gui.view.setRange(QtCore.QRectF(0, 0, self.imagesize[0], self.imagesize[1]))
        self.gui.roi.setPos([int(self.imagesize[0]/8.),int(self.imagesize[1]/8.)],finish=False)
        self.gui.roi.setSize([int(self.imagesize[0]*3/4.),int(self.imagesize[1]*3/4.)],finish=False)
        self.viewtimer.start()





    def MessageNoCamFound(self):
        '''
        Creates the messagebox that is shown when no camera is found.
        '''


        message = QtGui.QMessageBox()
        message.setIcon(QtGui.QMessageBox.Warning)
        message.setText("No cameras found!")
        message.setInformativeText("Please connect a supported camera to the computer and press the Search button.")
        message.setStandardButtons(QtGui.QMessageBox.Close)
        # message.addButton(QtGui.QMessageBox.Yes)
        searchbutton = message.addButton("Search",QtGui.QMessageBox.YesRole)
        # message.connect(searchbutton,QtCore.SIGNAL('clicked()'),self.RefreshCameras)
        demobutton = message.addButton("Start Demo",QtGui.QMessageBox.NoRole)



        retval = message.exec_()
        if message.clickedButton() == searchbutton:
            print "Search cameras!!"
            self.SearchCameras()

        if message.clickedButton() == demobutton:
            print "Start Demo!!"
            self.StartDemo()
            
        # print retval, "Retval"


    def MessageNoImageReceived(self):
        '''
        Creates the messagebox that is shown when no image is received from the camera.
        '''


        message = QtGui.QMessageBox()
        message.setIcon(QtGui.QMessageBox.Warning)
        message.setText("No image received!")
        message.setInformativeText("Make sure the camera is still connected and ready to use. How do you want to continue?")
        # message.setStandardButtons(QtGui.QMessageBox.Close)
        closebutton = message.addButton("Close",QtGui.QMessageBox.DestructiveRole)
        # message.addButton(QtGui.QMessageBox.Yes)
        searchbutton = message.addButton("Search",QtGui.QMessageBox.YesRole)
        # message.connect(searchbutton,QtCore.SIGNAL('clicked()'),self.RefreshCameras)
        demobutton = message.addButton("Start Demo",QtGui.QMessageBox.NoRole)



        retval = message.exec_()
        if message.clickedButton() == closebutton:
            self.viewtimer.stop()

        if message.clickedButton() == searchbutton:
            print "Search cameras!!"
            self.SearchCameras()

        if message.clickedButton() == demobutton:
            print "Start Demo!!"
            self.StartDemo()


    def CreateDataBuffer(self):
        '''
        Creates the data buffer needed for time evolution plots.
        the databuffer is returned.
        '''

        databuffer = np.zeros([7,self.databuffersize])
        bufferrange = np.arange(self.databuffersize)
        databuffer[0,:] = bufferrange

        if self.databufferfilling > self.databuffersize:
            self.databufferfilling = self.databuffersize

        return databuffer



    def CheckSaturation(self):
        '''
        Checks if pixel are saturated.
        '''

        if self.camera != None:
            if self.RealData:
                satpxl = np.where(self.imagearray == self.saturationvalue)
                # print satpxl, "Sat pxl"
                if len(satpxl[0]) > self.saturationthreshold:
                    self.gui.satwarning.setText("Warning: Pixel saturated!",color='r')
                else:
                    self.gui.satwarning.setText("Warning: Pixel saturated!",color='w')

        else:
            pass


    def InitializeSumFit(self):
        '''
        Initializes the fit using sum over ROI
        '''

        self.gui.ui.maxbeforeRadio.setChecked(False)
        self.gui.ui.absmaxRadio.setChecked(False)
        self.gui.ui.selfmaxRadio.setChecked(False)
        self.gui.ui.maxbeforeRadio.setCheckable(False)
        self.gui.ui.absmaxRadio.setCheckable(False)
        self.gui.ui.selfmaxRadio.setCheckable(False)
        self.gui.vLinecut.hide()
        self.gui.hLinecut.hide()


    def InitializeLineFit(self):
        '''
        Initializes the fit using single line of ROI.
        '''

        self.gui.ui.maxbeforeRadio.setCheckable(True)
        self.gui.ui.absmaxRadio.setCheckable(True)
        self.gui.ui.selfmaxRadio.setCheckable(True)
        self.gui.ui.maxbeforeRadio.setChecked(False)
        self.gui.ui.absmaxRadio.setChecked(True)
        self.gui.ui.selfmaxRadio.setChecked(False)
        self.gui.vLinecut.show()
        self.gui.hLinecut.show()

    def InitializeSelfLineFit(self):
        '''
        Initializes the line fit using self defined line.
        '''
        self.gui.vLinecut.setMovable(True)
        self.gui.hLinecut.setMovable(True)


    def InitializeAutoLineFit(self):
        '''
        Initializes the line fit using automatically determined line line.
        '''

        self.gui.vLinecut.setMovable(False)
        self.gui.hLinecut.setMovable(False)


    def CheckSaturationData(self,xdata,ydata):
        '''
        Checks if values in the fit data stem from saturated pixels and marks them.
        '''

        if self.RealData:
            indices = np.argwhere(ydata>=self.saturationvalue)
            # xdatanew = np.delete(xdata,indices)
            # ydatanew = np.delete(ydata,indices)
            ydata[indices] = -1
            
            # Exception when new arrays contain not enough data!!
            # if len(xdatanew) <= 5:

            #     print "ERROR - too many saturated pixel for proper fit!"

            #     xdatanew = np.zeros(10)
            #     ydatanew = np.zeros(10)
            return xdata, ydata
        else:
            return xdata, ydata





    #################################################################################################
    #################################################################################################
    # Methods for updating the image and the analysis plots.
    #################################################################################################
    #################################################################################################


    def updateview(self):
        '''
        This method upadates the image that is shown. 
        The orientation chosen is taken into account and the ROI boundaries are set properly.
        When the 'Hold' Button is pressed, the image is not updated.
        After updating the image, the method 'updateRoi' is called.
        '''

        
        hold = False
        hold = self.gui.ui.hold.isChecked()

        if hold==False:
            if self.RealData==False:
                self.simulation.ChooseImage()
                self.imagearray = self.simulation.image
            else:
                try:
                    self.camera.GetNextImage()
                    self.imagearray = self.camera.GiveImage()
                    # print self.camera.GiveImage(), "Image Array"
                except: # Show last image if grab failed -> Does not work (?)
                    self.MessageNoImageReceived()
                    # self.imagearray = np.rot90(self.imagearray,-1*self.rotangle)

                # self.camera.GetNextImage()
                # self.imagearray = self.camera.GiveImage()

            # print 'Image before updateROI: ',self.imagearray[23,65]

            self.imagearray = np.rot90(self.imagearray,self.rotangle)
            
            # if self.rotangle==0 or self.rotangle==2:
            #     # view.setRange(QtCore.QRectF(0, 0, 754, 480))
            #     self.gui.ui.x0Spin.setRange(0.,754.)
            #     self.gui.ui.y0Spin.setRange(0.,480.)
            #     bounds = QtCore.QRectF(0,0,753,479)
            #     self.gui.roi.maxBounds = bounds
            #     roisize = self.gui.roi.size()
            #     roipos = self.gui.roi.pos()

            #     # ADAPT TO IMAGE SIZE!!!!!
            #     if roisize[1] >= 480:
            #         # print roisize, roipos, 'ROI'
            #         self.gui.roi.setSize([200,200],finish=False)
            #     if roipos[1] >= (480-roisize[1]):
            #         # print roisize, roipos, 'ROI'
            #         self.gui.roi.setPos([200,200],finish=False)
            #         self.gui.roi.setSize([200,200],finish=False)
                    

                
            # elif self.rotangle==1 or self.rotangle==3:
            #     # view.setRange(QtCore.QRectF(0, 0, 480, 754))
            #     self.gui.ui.x0Spin.setRange(0.,480.)
            #     self.gui.ui.y0Spin.setRange(0.,754.)
            #     bounds = QtCore.QRectF(0,0,479,753)
            #     self.gui.roi.maxBounds = bounds
            #     roisize = self.gui.roi.size()
            #     roipos = self.gui.roi.pos()
            #     if roisize[0] >= 480:
            #         self.gui.roi.setSize([200,200],finish=False)
            #     if roipos[0] >= (480-roisize[0]):
            #         self.gui.roi.setPos([200,200],finish=False)
            #         self.gui.roi.setSize([200,200],finish=False)


            # if self.RealData:
            #     self.camera.SetExposureTime(self.gui.ui.exposureSpin.value())
            #     self.camera.SetGainValue(self.gui.ui.gainSpin.value())

            self.gui.img.setImage(self.imagearray.T.astype(float))
            # print "name", __name__
            self.CheckSaturation()

            if self.gui.ui.connect.isChecked():
                if self.muperpxl == None:
                    self.upddateroipos(self.databuffer[3,-1],self.databuffer[4,-1])
                else:
                    self.upddateroipos(self.databuffer[3,-1]/self.muperpxl,self.databuffer[4,-1]/self.muperpxl)

            # print "name", __name__

            self.updateRoi()

        else:
            if self.RealData:
                self.camera.GetNextImage()


    def updateexposuretime(self):
        '''
        Writes exposure time in config file when changed and updates GUI.
        '''

        if self.RealData:
            self.camera.SetExposureTime(self.gui.ui.exposureSpin.value())
            ExpoTime = self.camera.GetExposureTime()
            self.gui.ui.exposureSpin.setProperty("value", ExpoTime)
            self.updatecameraconfigfile()


    def updategainvalue(self):
        '''
        Writes gain value in config file when changed and updates GUI.
        '''

        if self.RealData:
            self.camera.SetGainValue(self.gui.ui.gainSpin.value())
            GainValue = self.camera.GetGainValue()
            self.gui.ui.gainSpin.setProperty("value", GainValue)
            self.updatecameraconfigfile()


    def updatecameraconfigfile(self):
        '''
        Updates the camera config file.
        '''

        ExpoTime = self.camera.GetExposureTime()
        GainValue = self.camera.GetGainValue()
            
        if not os.path.exists("CameraConfig.csv"):
            data = np.array([self.activecamtype,self.activecamserial,ExpoTime,GainValue])
            np.savetxt("CameraConfig.csv",data[None],fmt='%s',delimiter=",",header='Type, Serial, Exposure time, Gain')

        else:
            types,serials = np.loadtxt("CameraConfig.csv",delimiter=",",dtype=str,usecols=(0,1),unpack=True)
            expo,gain = np.loadtxt("CameraConfig.csv",delimiter=",",dtype=float,usecols=(2,3),unpack=True)

            # print types, "length types"
            if isinstance(types,basestring):
                types = np.array([types])
            if isinstance(serials,basestring):
                serials = np.array([serials])
            if isinstance(expo,float):
                expo = np.array([expo])
            if isinstance(gain,float):
                gain = np.array([gain])

                
            index = np.where(serials == self.activecamserial)
            # print index[0], 'Index where'

            if len(index[0]) == 0:
                print "Does not exist!"
                index = None
            elif len(index[0]) > 1:
                print "multiple serials exist! should not happen"
                index = None
            elif types[index] != self.activecamtype:
                # print types[index], self.activecamtype, "Match?"
                print "ERROR: Camera type and serial do not match! index set to None"
                index = None
                

            if index != None:
                types[index] = self.activecamtype
                # print types, "Types new"
                serials[index] = self.activecamserial
                expo[index] = ExpoTime
                gain[index] = GainValue
                data = np.array([types,serials,expo,gain]).T
            else:
                data = np.array([types,serials,expo,gain]).T
                # print data, "Data"
                newdata = np.array([self.activecamtype,self.activecamserial,ExpoTime,GainValue])
                # print newdata, "Newdata"
                data = np.vstack((data,newdata))
            np.savetxt("CameraConfig.csv",data,fmt='%s',delimiter=",",header='Type, Serial, Exposure time, Gain')





    def updaterotangleccw(self):
        '''
        In this method the variable 'rotangle', indicating the rotation of the image is
        shifted forward by one in the counterclockwise direction.
        '''
        
        self.rotangle = self.rotangle + 3
        self.rotangle = self.rotangle % 4

        oldimagesize = self.imagesize
        self.imagesize = (oldimagesize[1],oldimagesize[0])
        self.InitializeViewBoxSize()


    def updaterotanglecw(self):
        '''
        In this method the variable 'rotangle', indicating the rotation of the image is
        shifted forward by one in the clockwise direction.
        '''

        self.rotangle = self.rotangle + 1
        self.rotangle = self.rotangle % 4

        oldimagesize = self.imagesize
        self.imagesize = (oldimagesize[1],oldimagesize[0])
        self.InitializeViewBoxSize()


    def updateRoi(self):
        '''
        In this method the Roi data is updated. It is called when the Roi position and/or shape changes
        and when the image is updated. The ROI data is summed up in vertical and horizontal directions 
        and plotted in the according diagrams. The total sum of the ROI is seen as Amplitude and displayed
        in the plot. A gaussian is fitted to the sums in horizontal and vertical direction. The fit results 
        are used to plot the peak position and contour. The beam properties are stored in a buffer and can
        be plotted in the time evolution plot.
        '''

        # Get ROI data
        # print 'Image: ',self.imagearray.T.dtype

        # print "name", __name__

        selected,coorddata = self.gui.roi.getArrayRegion(self.imagearray.T, self.gui.img,returnMappedCoords=True)
        xhor = coorddata[0][:,0]
        xhortot = xhor
        if self.muperpxl != None:
            xhor = self.RescaleParameter(xhor)
        xvert = coorddata[1][0,:]
        xverttot = xvert
        if self.muperpxl != None:
            xvert = self.RescaleParameter(xvert)
        # print 'horizontal data', xhor


        # Calculate amplitude
        amplitude = selected.sum()
        
        # Shift buffer one step forward and store amplitude and time stamp
        self.databuffer[1:,:-1] = self.databuffer[1:,1:]
        actualtime = time.time()
        self.databuffer[1,-1] = actualtime - self.starttime
        self.databuffer[2,-1] = amplitude


        # Plot sum in horizontal direction and fit gaussian
        if self.gui.ui.fitsum.isChecked():
            datahor = selected.sum(axis=1)
            datavert = selected.sum(axis=0)
            # self.gui.ui.maxbeforeRadio.isCheckable(False)
            # self.gui.ui.absmaxRadio.isCheckable(False)
            # self.gui.ui.selfmaxRadio.isCheckable(False)
        elif self.gui.ui.fitline.isChecked():
            if self.gui.ui.maxbeforeRadio.isChecked():
                posroi = self.gui.roi.pos()
                datavertindex = round(self.databuffer[3,-1]) - posroi[0]
                datahorindex = round(self.databuffer[4,-1]) - posroi[1]
                datahor = selected[:,datahorindex]
                datavert = selected[datavertindex,:]

                xhor,datahor = self.CheckSaturationData(xhor,datahor)
                xvert,datavert = self.CheckSaturationData(xvert,datavert)

                self.gui.hLinecut.setPos(self.databuffer[4,-1])
                self.gui.vLinecut.setPos(self.databuffer[3,-1])
            elif self.gui.ui.absmaxRadio.isChecked():
                posroi = self.gui.roi.pos()
                maxindex = np.unravel_index(selected.argmax(), selected.shape)
                datahor = selected[:,maxindex[1]]
                datavert = selected[maxindex[0],:]

                xhor,datahor = self.CheckSaturationData(xhor,datahor)
                xvert,datavert = self.CheckSaturationData(xvert,datavert)

                self.gui.hLinecut.setPos(maxindex[1]+posroi[1])
                self.gui.vLinecut.setPos(maxindex[0]+posroi[0])
            elif self.gui.ui.selfmaxRadio.isChecked():
                posroi = self.gui.roi.pos()
                sizeroi = self.gui.roi.size()
                self.gui.vLinecut.setBounds((posroi[0],posroi[0]+sizeroi[0]-1))
                self.gui.hLinecut.setBounds((posroi[1],posroi[1]+sizeroi[1]-1))
                datahor = selected[:,int(self.gui.hLinecut.value()-posroi[1])]
                datavert = selected[int(self.gui.vLinecut.value()-posroi[0]),:]

                xhor,datahor = self.CheckSaturationData(xhor,datahor)
                xvert,datavert = self.CheckSaturationData(xvert,datavert)

        self.gui.p2.plot(xhor,datahor, clear=True)
        FittedParamsHor = MatTools.FitGaussian(datahor,xhor)[0]
        # FittedParamsHor = [3000,30,300,0]
        # xhor = np.arange(datahor.size)

        if self.gui.ui.fitCheck.isChecked():
            self.gui.p2.plot(xhortot,MatTools.gaussian(xhortot,*FittedParamsHor), pen=(0,255,0))

        # Plot amplitude
        xamp = np.array([1.,2.])
        yamp = np.array([amplitude])
        self.gui.amphist.plot(xamp, yamp, stepMode=True, clear=True, fillLevel=0, brush=(0,0,255,150))

        # Plot sum in vertical direction and fit gaussian, save fit results in buffer and show in text box
        
        self.gui.p3.plot(xvert,datavert, clear=True).rotate(90)
        FittedParamsVert = MatTools.FitGaussian(datavert,xvert)[0]
        # FittedParamsVert = [3000,30,300,0]
        # xvert = np.arange(datavert.size)

        if self.gui.ui.fitCheck.isChecked():
            self.gui.p3.plot(xverttot,MatTools.gaussian(xverttot,*FittedParamsVert), pen=(0,255,0)).rotate(90)
            poshor = FittedParamsHor[2]
            posvert = FittedParamsVert[2]
            waistx = FittedParamsHor[1]
            waisty = FittedParamsVert[1]

            # if self.muperpxl != None:
            #     poshor = self.RescaleParameter(poshor)
            #     posvert = self.RescaleParameter(posvert)
            #     waistx = self.RescaleParameter(waistx)
            #     waisty = self.RescaleParameter(waisty)

            self.databuffer[3,-1] = poshor
            self.databuffer[4,-1] = posvert
            self.databuffer[5,-1] = waistx
            self.databuffer[6,-1] = waisty

            if self.databufferfilling < self.databuffersize:
                self.databufferfilling += 1

            self.updatetext(amplitude,poshor,posvert,waistx,waisty)


        if self.gui.ui.trackCheck.isChecked():

            
            # Adjust cross hair
            if self.muperpxl == None:
                self.gui.hLine.setPos(FittedParamsVert[2])
                self.gui.vLine.setPos(FittedParamsHor[2])
            else:
                self.gui.hLine.setPos(FittedParamsVert[2]/self.muperpxl)
                self.gui.vLine.setPos(FittedParamsHor[2]/self.muperpxl)


            self.gui.vLine.show()
            self.gui.hLine.show()

            # Plot peak
            if self.muperpxl == None:
                pos = np.array([[(FittedParamsHor[2]),(FittedParamsVert[2])]])  
            else:
                pos = np.array([[(FittedParamsHor[2]/self.muperpxl),(FittedParamsVert[2]/self.muperpxl)]])        
            self.gui.peak.setData(pos,clear=True)

            # Plot contour
            if self.muperpxl == None:
                x = np.linspace(-(FittedParamsHor[1]),(FittedParamsHor[1]),1000)
                sigmax = FittedParamsHor[1]
                sigmay = FittedParamsVert[1]
                y = ellipse(x,sigmax,sigmay)

                x = np.append(x,-x)
                y = np.append(y,-y)
                
                x += FittedParamsHor[2]
                y += FittedParamsVert[2]
            else:
                x = np.linspace(-(FittedParamsHor[1]/self.muperpxl),(FittedParamsHor[1]/self.muperpxl),1000)
                sigmax = FittedParamsHor[1]/self.muperpxl
                sigmay = FittedParamsVert[1]/self.muperpxl
                y = ellipse(x,sigmax,sigmay)

                x = np.append(x,-x)
                y = np.append(y,-y)
                
                x += FittedParamsHor[2]/self.muperpxl
                y += FittedParamsVert[2]/self.muperpxl

            self.gui.contour.setData(x,y,clear=True)

        else:
            # Hide cross hair, peak and contour if 'Track beam' is not checked
            self.gui.vLine.hide()
            self.gui.hLine.hide()
            self.gui.contour.clear()
            self.gui.peak.clear()

        #When checked, the reference beam peak and contour is plotted   
        if self.gui.ui.refCheck.isChecked():

            peakposition = np.array([[self.gui.ui.x0Spin.value(),self.gui.ui.y0Spin.value()]])
            self.gui.peakpos.setData(peakposition,clear=True)


            sigmax = self.gui.ui.sigmaxSpin.value()
            sigmay = self.gui.ui.sigmaySpin.value()
            x = np.linspace(-(sigmax),(sigmax),1000)
            y = ellipse(x,sigmax,sigmay)

            x = np.append(x,-x)
            y = np.append(y,-y)
            
            x += self.gui.ui.x0Spin.value()
            y += self.gui.ui.y0Spin.value()
            # X,Y = np.meshgrid(x,y)
            # contour.clear()
            self.gui.refcontour.setData(x,y,clear=True)

        else:
            self.gui.peakpos.clear()
            self.gui.refcontour.clear()


        # Update the time evolution plot
        self.updatetimescrolling()


    def updatetext(self,amplitude,x,y,waistx,waisty):
        '''
        The textbox giving information about the beam is updated.
        '''

        self.gui.text.setHtml('<div style="text-align: center"><span style="color: #FFF; font-size: 16pt;">Beam Properties</span><br>\
            <span style="color: #FFF; font-size: 10pt;">Amplitude: %0.2f</span><br>\
            <span style="color: #FFF; font-size: 10pt;">Horizontal Position: %0.2f</span><br>\
            <span style="color: #FFF; font-size: 10pt;">Vertical Position: %0.2f</span><br>\
            <span style="color: #FFF; font-size: 10pt;">Horizontal Waist: %0.2f</span><br>\
            <span style="color: #FFF; font-size: 10pt;">Vertical Waist: %0.2f</span></div>' %(amplitude,x,y,waistx,waisty))



    def timeplotampchanged(self):
        '''
        Initializes timeplot of amplitude with zoom state.
        '''

        if self.gui.ui.ampRadio.isChecked():
            if self.amprange != None:
                self.gui.timeplot.setRange(rect=self.amprange)
            else:
                self.gui.timeplot.enableAutoRange()
        else:
            # print self.gui.timeplot.saveState()['view']['autoRange'], "Autorange State"
            autorangecheck = self.gui.timeplot.saveState()['view']['autoRange']
            if autorangecheck[1] > 0:
                self.amprange = None
            else:
                self.amprange = self.gui.timeplot.viewRect()


    def timeplotposhorchanged(self):
        '''
        Initializes timeplot of horizontal position with zoom state.
        '''

        if self.gui.ui.poshorRadio.isChecked():
            if self.poshorrange != None:
                self.gui.timeplot.setRange(rect=self.poshorrange)
            else:
                self.gui.timeplot.enableAutoRange()
        else:
            # print self.gui.timeplot.saveState()['view']['autoRange'], "Autorange State"
            autorangecheck = self.gui.timeplot.saveState()['view']['autoRange']
            if autorangecheck[1] > 0:
                self.poshorrange = None
            else:
                self.poshorrange = self.gui.timeplot.viewRect()


    def timeplotposvertchanged(self):
        '''
        Initializes timeplot of vertical position with zoom state.
        '''

        if self.gui.ui.posvertRadio.isChecked():
            if self.posvertrange != None:
                self.gui.timeplot.setRange(rect=self.posvertrange)
            else:
                self.gui.timeplot.enableAutoRange()
        else:
            # print self.gui.timeplot.saveState()['view']['autoRange'], "Autorange State"
            autorangecheck = self.gui.timeplot.saveState()['view']['autoRange']
            if autorangecheck[1] > 0:
                self.posvertrange = None
            else:
                self.posvertrange = self.gui.timeplot.viewRect()


    def timeplotwaisthorchanged(self):
        '''
        Initializes timeplot of horizontal waist with zoom state.
        '''

        if self.gui.ui.waisthorRadio.isChecked():
            if self.waisthorrange != None:
                self.gui.timeplot.setRange(rect=self.waisthorrange)
            else:
                self.gui.timeplot.enableAutoRange()
        else:
            # print self.gui.timeplot.saveState()['view']['autoRange'], "Autorange State"
            autorangecheck = self.gui.timeplot.saveState()['view']['autoRange']
            if autorangecheck[1] > 0:
                self.waisthorrange = None
            else:
                self.waisthorrange = self.gui.timeplot.viewRect()


    def timeplotwaistvertchanged(self):
        '''
        Initializes timeplot of vertical waist with zoom state.
        '''

        if self.gui.ui.waistvertRadio.isChecked():
            if self.waistvertrange != None:
                self.gui.timeplot.setRange(rect=self.waistvertrange)
            else:
                self.gui.timeplot.enableAutoRange()
        else:
            # print self.gui.timeplot.saveState()['view']['autoRange'], "Autorange State"
            autorangecheck = self.gui.timeplot.saveState()['view']['autoRange']
            if autorangecheck[1] > 0:
                self.waistvertrange = None
            else:
                self.waistvertrange = self.gui.timeplot.viewRect()


    def timeplotdistchanged(self):
        '''
        Initializes timeplot of distance from ref beam to beam with zoom state.
        '''

        if self.gui.ui.distRadio.isChecked():
            if self.distrange != None:
                self.gui.timeplot.setRange(rect=self.distrange)
            else:
                self.gui.timeplot.enableAutoRange()
        else:
            # print self.gui.timeplot.saveState()['view']['autoRange'], "Autorange State"
            autorangecheck = self.gui.timeplot.saveState()['view']['autoRange']
            if autorangecheck[1] > 0:
                self.distrange = None
            else:
                self.distrange = self.gui.timeplot.viewRect()




    def updatetimescrolling(self):
        '''
        The time evolution plot is updated.
        '''

        timescale = self.databuffer[1,:] - self.databuffer[1,-1]

        if self.gui.ui.fitCheck.isChecked():
            self.gui.ui.poshorRadio.setEnabled(True)
            self.gui.ui.posvertRadio.setEnabled(True)
            self.gui.ui.waisthorRadio.setEnabled(True)
            self.gui.ui.waistvertRadio.setEnabled(True)
            self.gui.ui.distRadio.setEnabled(True)

            if self.gui.ui.ampRadio.isChecked():
                self.gui.timeplot.plot(timescale[-self.databufferfilling:],self.databuffer[2,-self.databufferfilling:],clear=True)
                self.gui.timeplot.setLabel('left', "Amplitude", units='')
                

            if self.gui.ui.poshorRadio.isChecked():
                self.gui.timeplot.plot(timescale[-self.databufferfilling:],self.databuffer[3,-self.databufferfilling:],clear=True)
                if self.muperpxl == None:
                    self.gui.timeplot.setLabel('left', "Horizontal Position", units='px')
                else:
                    self.gui.timeplot.setLabel('left', "Horizontal Position", units='um')


            if self.gui.ui.posvertRadio.isChecked():
                self.gui.timeplot.plot(timescale[-self.databufferfilling:],self.databuffer[4,-self.databufferfilling:],clear=True)
                if self.muperpxl == None:
                    self.gui.timeplot.setLabel('left', "Vertical Position", units='px')
                else:
                    self.gui.timeplot.setLabel('left', "Vertical Position", units='um')

            if self.gui.ui.waisthorRadio.isChecked():
                self.gui.timeplot.plot(timescale[-self.databufferfilling:],self.databuffer[5,-self.databufferfilling:],clear=True)
                if self.muperpxl == None:
                    self.gui.timeplot.setLabel('left', "Horizontal Waist", units='px')
                else:
                    self.gui.timeplot.setLabel('left', "Horizontal Waist", units='um')

            if self.gui.ui.waistvertRadio.isChecked():
                self.gui.timeplot.plot(timescale[-self.databufferfilling:],self.databuffer[6,-self.databufferfilling:],clear=True)
                if self.muperpxl == None:
                    self.gui.timeplot.setLabel('left', "Vertical Waist", units='px')
                else:
                    self.gui.timeplot.setLabel('left', "Vertical Waist", units='um')
            if self.gui.ui.distRadio.isChecked():
                distance = np.sqrt((self.databuffer[3,:]-self.gui.ui.x0Spin.value())**2+\
                    (self.databuffer[4,:]-self.gui.ui.y0Spin.value())**2)
                self.gui.timeplot.plot(timescale[-self.databufferfilling:],distance[-self.databufferfilling:],clear=True)
                if self.muperpxl == None:
                    self.gui.timeplot.setLabel('left', "Distance to reference peak", units='px')
                else:
                    self.gui.timeplot.setLabel('left', "Distance to reference peak", units='um')

        else:
            self.gui.ui.ampRadio.setChecked(True)
            self.gui.timeplot.plot(timescale,self.databuffer[2,:],clear=True)
            self.gui.timeplot.setLabel('left', "Amplitude", units='')
            self.gui.ui.poshorRadio.setEnabled(False)
            self.gui.ui.posvertRadio.setEnabled(False)
            self.gui.ui.waisthorRadio.setEnabled(False)
            self.gui.ui.waistvertRadio.setEnabled(False)
            self.gui.ui.distRadio.setEnabled(False)


    def saveroisize(self):
        '''
        The ROI position is saved.
        '''
        
        self.origroisize = self.gui.roi.size()


    def upddateroipos(self,x,y):
        '''
        The ROI position is updated. The bounds are respected.
        '''
        
        xpos = x-int(self.origroisize[0]/2.)
        xsize = self.origroisize[0]
        ysize = self.origroisize[1]
        if xpos < 0:
            xpos = 0
        if xpos > self.imagesize[0]:
            xpos = self.imagesize[0] - xsize
        ypos = y-int(self.origroisize[1]/2.)
        if ypos < 0:
            ypos = 0
        if ypos > self.imagesize[1]:
            ypos = self.imagesize[1] - ysize
        if xpos + self.origroisize[0] >= self.imagesize[0]:
            xsize = self.imagesize[0] - xpos - 1
        if ypos + self.origroisize[1] >= self.imagesize[1]:
            ysize = self.imagesize[1] - ypos - 1


        self.gui.roi.setPos([xpos,ypos],finish=False)
        self.gui.roi.setSize([xsize,ysize],finish=False)
        # roi.stateChanged()

    def autoadjustroi(self):
        '''
        Automatically adjusts ROI size to 4 times beam waist.
        '''

        waistx = self.databuffer[5,-1]
        waisty = self.databuffer[6,-1]

        sizex = 6*waistx
        sizey = 6*waisty
        posx = self.databuffer[3,-1] - 3*waistx
        posy = self.databuffer[4,-1] - 3*waisty

        if posx < 0:
            posx = 0
        if posx+sizex >= self.imagesize[0]:
            sizex = self.imagesize[0] -posx -1
        if posy < 0:
            posy = 0
        if posy+sizey >= self.imagesize[1]:
            sizey = self.imagesize[1] -posy -1

        self.gui.roi.setPos([posx,posy],finish=False)
        self.gui.roi.setSize([sizex,sizey],finish=False)





    def runApp(self):
        '''
        Run the beam profiling application.
        '''

        if self.RealData==False:
            self.simulation = Sim.GaussBeamSimulation()
            self.simulation.CreateImages()

        

        # When the 'Connect ROI' button is pressed, 'saveroisize' is called
        self.gui.ui.connect.toggled.connect(self.saveroisize)

        self.gui.ui.fitsum.clicked.connect(self.InitializeSumFit)

        self.gui.ui.fitline.clicked.connect(self.InitializeLineFit)

        self.gui.ui.maxbeforeRadio.clicked.connect(self.InitializeAutoLineFit)

        self.gui.ui.absmaxRadio.clicked.connect(self.InitializeAutoLineFit)

        self.gui.ui.selfmaxRadio.clicked.connect(self.InitializeSelfLineFit)
    
        # When the ROI region has been changed, 'updateRoi' is called
        self.gui.roi.sigRegionChangeFinished.connect(self.updateRoi)

        # When the 'Rotate counterclockwise' button is clicked, call 'updaterotangleccw'
        # self.gui.ui.rotccw.clicked.connect(self.updaterotangleccw)

        # When the 'Rotate clockwise' button is clicked, call 'updaterotanglecw'
        # self.gui.ui.rotcw.clicked.connect(self.updaterotanglecw)

        self.gui.ui.saveprops.clicked.connect(self.SaveDataSimple)

        self.gui.ui.autoscale.clicked.connect(self.autoadjustroi)

        self.gui.ui.exposureSpin.valueChanged.connect(self.updateexposuretime)

        self.gui.ui.gainSpin.valueChanged.connect(self.updategainvalue)

        self.gui.ui.ampRadio.toggled.connect(self.timeplotampchanged)
        self.gui.ui.poshorRadio.toggled.connect(self.timeplotposhorchanged)
        self.gui.ui.posvertRadio.toggled.connect(self.timeplotposvertchanged)
        self.gui.ui.waisthorRadio.toggled.connect(self.timeplotwaisthorchanged)
        self.gui.ui.waistvertRadio.toggled.connect(self.timeplotwaistvertchanged)
        self.gui.ui.distRadio.toggled.connect(self.timeplotdistchanged)

        # When the timer is timed out, 'updateview' is called
        self.viewtimer.timeout.connect(self.updateview)

        # self.autosavetimer.timeout.connect(self.AutosaveBeamProps(timeinterval=3.0))


        
        if self.camera != None:
            # Start the timer: time out after 0 ms
            # self.viewtimer.start(0)

            # When the GUI is closed: stop the timer
            self.gui.app.exec_()
            self.viewtimer.stop()
            if self.RealData:
                self.camera.StopCamera()
        else:
            self.gui.app.exec_()




if __name__=="__main__":
    check = App_Launcher()
    # check.runApp()






