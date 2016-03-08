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
        self.cameramenu, self.settingsmenu = self.CreateMenuBar()

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
        exitAction.triggered.connect(QtGui.qApp.quit)
        fileMenu.addAction(exitAction)

        cameraMenu = self.menubar.addMenu('&Camera')
        settingsMenu = self.menubar.addMenu('&Settings')
        # refreshAction = QtGui.QAction('Refresh', cameraMenu)
        # cameraMenu.addAction(refreshAction)
        # cameraMenu.addSeparator()

        
        

        ### TODO: Outsource this menu in other class!!!
        # vrmagicMenu = cameraMenu.addMenu('VRmagic')
        # self.mainwin.connect(refreshAction,QtCore.SIGNAL('triggered()'), lambda: RefreshCameras(vrmagicMenu,self.ui))
        ###############################################

        self.mainwin.setMenuBar(self.menubar)

        return cameraMenu, settingsMenu


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

        return vLine,hLine

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

        self.RealData = True


        self.gui = Ui_Window()
        self.VRmMenu = self.InitializeCamSearch()
        self.InitializeSettings()
        
        self.camera = None
        self.imagearray = None
        self.databuffer = self.CreateDataBuffer()
        self.rotangle = 0
        self.starttime = time.time()
        self.origroisize = None
        self.simulation = None


        # Start timer for the loop
        self.viewtimer = QtCore.QTimer()
        #???
        # self.VRmCam = None

        self.saturationvalue = None
        self.saturationthreshold = 5

        self.SearchCameras()

        self.runApp()





    def InitializeCam(self):
        '''Initializes the camera, update the exposure time and gain value fields'''
        
        ExpoTime = self.camera.GetExposureTime()
        self.gui.ui.exposureSpin.setProperty("value", ExpoTime)
        GainValue = self.camera.GetGainValue()
        self.gui.ui.gainSpin.setProperty("value", GainValue)

        self.saturationvalue = self.camera.GetSaturationValue()
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


    def ChangeCamera(self,camindex=0):
        '''
        Stops old camera, starts new camera
        TODO: Adapt for multiple camera types
        '''
        self.camera.StopCamera()
        self.camera.StartCamera(camindex=camindex)
        self.InitializeCam()


    def InitializeCamSearch(self):
        '''
        This method initializes the camera menu and return the menu for each camera type.
        TODO: Adapt for multiple camera types
        '''

        refreshAction = QtGui.QAction('Refresh', self.gui.cameramenu)
        self.gui.cameramenu.addAction(refreshAction)
        self.gui.cameramenu.addSeparator()

        
        vrmagicMenu = self.gui.cameramenu.addMenu('VRmagic')

        self.gui.mainwin.connect(refreshAction,QtCore.SIGNAL('triggered()'), lambda: self.RefreshCameras())

        return vrmagicMenu


    def InitializeSettings(self):

        saturationMenu = self.gui.settingsmenu.addMenu('Saturation')
        thresholdAction = QtGui.QAction('Threshold',saturationMenu)
        saturationMenu.addAction(thresholdAction)

        self.gui.mainwin.connect(thresholdAction,QtCore.SIGNAL('triggered()'), lambda: self.AdjustSaturationThreshold())

    def AdjustSaturationThreshold(self):

        number,ok = QtGui.QInputDialog.getInt(self.gui.win,"Adjust Saturation Threshold","Enter new minimal pixel number:",value=self.saturationthreshold)
        
        if ok:
            self.saturationthreshold = number




    def SearchCameras(self):
        '''
        Searches all available supported cameras (of all supported types).
        Creates menu.
        Starts first available camera.
        TODO: Adapt for multiple camera types
        '''

        totalcamnumber = 0
        camfound = False

        #################################################

        VRmCam = VRmagicAPI.VRmagicUSBCam_API()
        cameralist = VRmCam.CreateCameraList()
        numbercams = len(cameralist)
        totalcamnumber += numbercams
        
        self.RealData = True

        # ADD HANDLING IF NO CAMERA IS AVAILABLE/PLUGGED TO THE PC
        if numbercams != 0:
            if not camfound:
                self.camera = VRmCam
                self.camera.StartCamera(camindex=0)
                self.InitializeCam()
                camfound = True
            for i in range(numbercams):
                name = cameralist[i]
                # testaction = QtGui.QAction(name, mainwin)
                changeaction = self.VRmMenu.addAction(name)
                self.gui.mainwin.connect(changeaction,QtCore.SIGNAL('triggered()'), lambda i=i: self.ChangeCamera(camindex=i))
                self.VRmMenu.addAction(changeaction)
                
        
        if camfound:
            self.viewtimer.start()
        if not camfound:
            self.MessageNoCamFound()
            self.camera = None
            # print 'ERROR -- No cameras found!!'


    def RefreshCameras(self):
        '''
        Refreshes the camera list.
        TODO: Adapt for multiple camera types
        '''

        if self.camera != None:
            self.viewtimer.stop()
            if self.RealData:
                self.camera.StopCamera()

            for i in self.VRmMenu.actions():
                self.VRmMenu.removeAction(i)

        
        self.SearchCameras()
        self.InitializeCam()




    def StartDemo(self):
        '''
        Starts a demo.
        '''

        self.RealData = False
        self.camera = "Simulation in use"
        self.simulation = Sim.GaussBeamSimulation()
        self.simulation.CreateImages()
        self.viewtimer.start(0)





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


    def CreateDataBuffer(self):
        '''
        Creates the data buffer needed for time evolution plots.
        the databuffer is returned.
        '''

        buffersize = 40000 # Change this number for showing a longer period in time evolution plots
        databuffer = np.zeros([7,buffersize])
        bufferrange = np.arange(buffersize)
        databuffer[0,:] = bufferrange

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
                except: # Show last image if grab failed -> Does not work (?)
                    self.imagearray = np.rot90(imagearray,-1*self.rotangle)

            self.imagearray = np.rot90(self.imagearray,self.rotangle)
            
            if self.rotangle==0 or self.rotangle==2:
                # view.setRange(QtCore.QRectF(0, 0, 754, 480))
                self.gui.ui.x0Spin.setRange(0.,754.)
                self.gui.ui.y0Spin.setRange(0.,480.)
                bounds = QtCore.QRectF(0,0,753,479)
                self.gui.roi.maxBounds = bounds
                roisize = self.gui.roi.size()
                roipos = self.gui.roi.pos()

                # ADAPT TO IMAGE SIZE!!!!!
                if roisize[1] >= 480:
                    # print roisize, roipos, 'ROI'
                    self.gui.roi.setSize([200,200],finish=False)
                if roipos[1] >= (480-roisize[1]):
                    # print roisize, roipos, 'ROI'
                    self.gui.roi.setPos([200,200],finish=False)
                    self.gui.roi.setSize([200,200],finish=False)
                    

                
            elif self.rotangle==1 or self.rotangle==3:
                # view.setRange(QtCore.QRectF(0, 0, 480, 754))
                self.gui.ui.x0Spin.setRange(0.,480.)
                self.gui.ui.y0Spin.setRange(0.,754.)
                bounds = QtCore.QRectF(0,0,479,753)
                self.gui.roi.maxBounds = bounds
                roisize = self.gui.roi.size()
                roipos = self.gui.roi.pos()
                if roisize[0] >= 480:
                    self.gui.roi.setSize([200,200],finish=False)
                if roipos[0] >= (480-roisize[0]):
                    self.gui.roi.setPos([200,200],finish=False)
                    self.guiroi.setSize([200,200],finish=False)


            '''
            To implement: Set only if value is changed!!
            '''  

            if self.RealData:
                self.camera.SetExposureTime(self.gui.ui.exposureSpin.value())
                self.camera.SetGainValue(self.gui.ui.gainSpin.value())

            self.gui.img.setImage(self.imagearray.T.astype(float))
            self.CheckSaturation()

            if self.gui.ui.connect.isChecked():
                sel.upddateroipos(self.databuffer[3,-1],self.databuffer[4,-1])
            
            self.updateRoi()

        else:
            if self.RealData:
                self.camera.GetNextImage()



    def updaterotangleccw(self):
        '''
        In this method the variable 'rotangle', indicating the rotation of the image is
        shifted forward by one in the counterclockwise direction.
        '''
        
        self.rotangle = self.rotangle + 3
        self.rotangle = self.rotangle % 4


    def updaterotanglecw(self):
        '''
        In this method the variable 'rotangle', indicating the rotation of the image is
        shifted forward by one in the clockwise direction.
        '''

        self.rotangle = self.rotangle + 1
        self.rotangle = self.rotangle % 4


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
        selected = self.gui.roi.getArrayRegion(self.imagearray.T, self.gui.img)

        # Calculate amplitude
        amplitude = selected.sum()
        
        # Shift buffer one step forward and store amplitude and time stamp
        self.databuffer[1:,:-1] = self.databuffer[1:,1:]
        actualtime = time.time()
        self.databuffer[1,-1] = actualtime - self.starttime
        self.databuffer[2,-1] = amplitude


        # Plot sum in horizontal direction and fit gaussian
        datahor = selected.sum(axis=1)
        self.gui.p2.plot(datahor, clear=True)
        FittedParamsHor = MatTools.FitGaussian(datahor)[0]
        xhor = np.arange(datahor.size)

        if self.gui.ui.fitCheck.isChecked():
            self.gui.p2.plot(MatTools.gaussian(xhor,*FittedParamsHor), pen=(0,255,0))

        # Plot amplitude
        xamp = np.array([1.,2.])
        yamp = np.array([amplitude])
        self.gui.amphist.plot(xamp, yamp, stepMode=True, clear=True, fillLevel=0, brush=(0,0,255,150))

        # Plot sum in vertical direction and fit gaussian, save fit results in buffer and show in text box
        datavert = selected.sum(axis=0)
        self.gui.p3.plot(datavert, clear=True).rotate(90)
        FittedParamsVert = MatTools.FitGaussian(datavert)[0]
        xvert = np.arange(datavert.size)

        if self.gui.ui.fitCheck.isChecked():
            self.gui.p3.plot(MatTools.gaussian(xvert,*FittedParamsVert), pen=(0,255,0)).rotate(90)
            poshor = FittedParamsHor[2]+self.gui.roi.pos()[0]
            posvert = FittedParamsVert[2]+self.gui.roi.pos()[1]
            waistx = FittedParamsHor[1]
            waisty = FittedParamsVert[1]

            self.databuffer[3,-1] = poshor
            self.databuffer[4,-1] = posvert
            self.databuffer[5,-1] = waistx
            self.databuffer[6,-1] = waisty

            self.updatetext(amplitude,poshor,posvert,waistx,waisty)


        if self.gui.ui.trackCheck.isChecked():

            
            # Adjust cross hair
            self.gui.hLine.setPos(FittedParamsVert[2]+self.gui.roi.pos()[1])
            self.gui.vLine.setPos(FittedParamsHor[2]+self.gui.roi.pos()[0])

            self.gui.vLine.show()
            self.gui.hLine.show()

            # Plot peak
            pos = np.array([[(FittedParamsHor[2]+self.gui.roi.pos()[0]),(FittedParamsVert[2]+self.gui.roi.pos()[1])]])           
            self.gui.peak.setData(pos,clear=True)

            # Plot contour
            x = np.linspace(-(FittedParamsHor[1]),(FittedParamsHor[1]),1000)
            sigmax = FittedParamsHor[1]
            sigmay = FittedParamsVert[1]
            y = ellipse(x,sigmax,sigmay)

            x = np.append(x,-x)
            y = np.append(y,-y)
            
            x += FittedParamsHor[2]+self.gui.roi.pos()[0]
            y += FittedParamsVert[2]+self.gui.roi.pos()[1]
            # X,Y = np.meshgrid(x,y)
            # contour.clear()
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
                self.gui.timeplot.plot(timescale,self.databuffer[2,:],clear=True)
                self.gui.timeplot.setLabel('left', "Amplitude", units='')

            if self.gui.ui.poshorRadio.isChecked():
                self.gui.timeplot.plot(timescale,self.databuffer[3,:],clear=True)
                self.gui.timeplot.setLabel('left', "Horizontal Position", units='px')

            if self.gui.ui.posvertRadio.isChecked():
                self.gui.timeplot.plot(timescale,self.databuffer[4,:],clear=True)
                self.gui.timeplot.setLabel('left', "Vertical Position", units='px')

            if self.gui.ui.waisthorRadio.isChecked():
                self.gui.timeplot.plot(timescale,self.databuffer[5,:],clear=True)
                self.gui.timeplot.setLabel('left', "Horizontal Waist", units='px')

            if self.gui.ui.waistvertRadio.isChecked():
                self.gui.timeplot.plot(timescale,self.databuffer[6,:],clear=True)
                self.gui.timeplot.setLabel('left', "Vertical Waist", units='px')

            if self.gui.ui.distRadio.isChecked():
                distance = np.sqrt((self.databuffer[3,:]-self.gui.ui.x0Spin.value())**2+\
                    (self.databuffer[4,:]-self.gui.ui.y0Spin.value())**2)
                self.gui.timeplot.plot(timescale,distance,clear=True)
                self.gui.timeplot.setLabel('left', "Distance to reference peak", units='px')

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
        
        imagesize = self.imagerray.shape
        xpos = x-int(self.origroisize[0]/2.)
        xsize = self.origroisize[0]
        ysize = self.origroisize[1]
        if xpos < 0:
            xpos = 0
        ypos = y-int(self.origroisize[1]/2.)
        if ypos < 0:
            ypos = 0
        if xpos + self.origroisize[0] >= imagesize[1]:
            xsize = imagesize[1] - xpos - 1
        if ypos + self.origroisize[1] >= imagesize[0]:
            ysize = imagesize[0] - ypos - 1


        self.gui.roi.setPos([xpos,ypos],finish=False)
        self.gui.roi.setSize([xsize,ysize],finish=False)
        # roi.stateChanged()


    def runApp(self):
        '''
        Run the beam profiling application.
        '''

        if self.RealData==False:
            self.simulation = Sim.GaussBeamSimulation()
            self.simulation.CreateImages()

        

        # When the 'Connect ROI' button is pressed, 'saveroisize' is called
        self.gui.ui.connect.toggled.connect(self.saveroisize)
    
        # When the ROI region has been changed, 'updateRoi' is called
        self.gui.roi.sigRegionChangeFinished.connect(self.updateRoi)

        # When the 'Rotate counterclockwise' button is clicked, call 'updaterotangleccw'
        self.gui.ui.rotccw.clicked.connect(self.updaterotangleccw)

        # When the 'Rotate clockwise' button is clicked, call 'updaterotanglecw'
        self.gui.ui.rotcw.clicked.connect(self.updaterotanglecw)

        # When the timer is timed out, 'updateview' is called
        self.viewtimer.timeout.connect(self.updateview)
        
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






