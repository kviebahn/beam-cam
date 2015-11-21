# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 10:18:13 2015

This script starts the image viewer GUI for VRmagic USB Cameras.

TO DO: -test with more than one camera and add error handling
       -implement the option to save data
       -implement the possibility to choose a different colormap for the image

@author: Michael
"""


import GaussBeamSimulation as Sim
reload(Sim)
import MathematicalTools as MatTools
reload(MatTools)
import VRmUsbCamAPI as CamAPI
reload(CamAPI)

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





def StartGUI(camera='Simulation is used'):
    '''Starts the GUI'''

    def InitializeCam(camera,ui):
        '''Initializes the camera, update the exposure time and gain value fields, switch off status LED'''
        ExpoTime = camera.GetExposureTime(camera.CamIndex)
        ui.exposureSpin.setProperty("value", ExpoTime)
        GainValue = camera.GetGainValue(camera.CamIndex)
        ui.gainSpin.setProperty("value", GainValue)
        # Switch off status LED
        camera.SetStatusLED(camera.CamIndex,False)

    def CreateFile(name='test'):
        '''
        creates an empty .txt file; intended for saving
        not in use yet!
        '''
        if not os.path.exists(name):
            f = open(name+'.txt', 'w')
            f.close()
        else:
            print 'A file with this name already exists!'



    global img, databuffer, rotangle

    # Setup UI
    app = QtGui.QApplication([])
    win = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(win)

    # Create new image widget
    imagewidget = ui.plot

    # Add view box for displaying the image
    view = imagewidget.addViewBox()
    view.setAspectLocked(True)

    #Create image and add it to the view box
    img = pg.ImageItem(border='k')
    view.addItem(img)
    view.setRange(QtCore.QRectF(0, 0, 754, 754))

    # Create and add ROI for selecting an image region
    roi = pg.ROI([160, 40], [400, 400],pen='b') # First lower left edge in pxl [x,y], then Size in pxl 
    roi.addScaleHandle([0.5, 1], [0.5, 0.5])
    roi.addScaleHandle([0, 0.5], [0.5, 0.5])
    view.addItem(roi)
    roi.setZValue(10)  # Make sure ROI is drawn above
    bounds = QtCore.QRectF(0,0,753,479) # Set bounds of the roi
    roi.maxBounds = bounds

    # Create marker of the peak position of the beam
    symbol = ['x']
    peak = pg.PlotDataItem(symbol = symbol,symbolPen='g',Pen=None,symbolBrush='g',symbolSize=25)
    view.addItem(peak)
    peak.setZValue(20)

    # Create marker of the reference peak
    symbol = ['x']
    peakpos = pg.PlotDataItem(symbol = symbol,symbolPen='r',Pen=None,symbolBrush='r',symbolSize=25)
    view.addItem(peakpos)
    peakpos.setZValue(20)

    # Create contour of the beam
    contour = pg.PlotDataItem()
    contour.setPen('g')
    view.addItem(contour)
    contour.setZValue(30)

    # Create contour of the reference beam
    refcontour = pg.PlotDataItem()
    refcontour.setPen('r')
    view.addItem(refcontour)
    refcontour.setZValue(25)



    # Add plot of the vertical sum of the ROI
    p3 = imagewidget.addPlot(colspan=1,title='Sum Horizontal')
    # p3.rotate(90)
    p3.setMaximumWidth(200)
    p3.setLabel('left',"Vertical Position",units='px')
    p3.setLabel('bottom',"Intensity",units='')

    # Create histogram to visualize the amplitude
    amphist = imagewidget.addPlot(colspan=1,title='Amplitude<br>in ROI')
    amphist.setMaximumWidth(100)
    amphist.hideAxis('bottom')
    amphist.setLabel('left',"Amplitude",units='')

    # Add plot of the time evolution of beam properties
    timeplot = imagewidget.addPlot(colspan=1,title='Time Evolution')
    timeplot.setMaximumWidth(400)
    timeplot.setLabel('bottom', "Time", units='s')

    # Go to the next row
    imagewidget.nextRow()

    # Add plot of the horizontal sum of the ROI
    p2 = imagewidget.addPlot(colspan=1,title='Sum Vertical')
    p2.setMaximumHeight(200)
    p2.setLabel('bottom',"Horizontal Position",units='px')
    p2.setLabel('left',"Intensity",units='')

    # Set text for the textbox to show the beam properties
    texthtml = '<div style="text-align: center"><span style="color: #FFF; font-size: 16pt;">Beam Properties</span><br>\
    <span style="color: #FFF; font-size: 10pt;">Horizontal Position: 233,2</span><br>\
    <span style="color: #FFF; font-size: 10pt;">Vertical Position: 233,2</span><br>\
    <span style="color: #FFF; font-size: 10pt;">Horizontal Waist: 233,2</span><br>\
    <span style="color: #FFF; font-size: 10pt;">Vertical Waist: 233,2</span></div>'

    # Set text box for showing the beam properties
    text = pg.TextItem(html=texthtml, anchor=(0.,0.), border='w', fill=(0, 0, 255, 100))
    textbox = imagewidget.addPlot()
    textbox.addItem(text)
    textbox.setMaximumWidth(200)
    textbox.setMaximumHeight(200)
    textbox.setMinimumWidth(200)
    textbox.setMinimumHeight(200)
    textbox.hideAxis('left')
    textbox.hideAxis('bottom')
    text.setTextWidth(190)
    text.setPos(0.02,0.75)
    # textbox.setAspectLocked(True)
    # textbox.setRange(xRange=(0,200))
    # textbox.setLimits(xMin=0,xMax=200)




    # Create cross hair
    vLine = pg.InfiniteLine(angle=90, movable=False)
    hLine = pg.InfiniteLine(angle=0, movable=False)
    view.addItem(vLine, ignoreBounds=True)
    view.addItem(hLine, ignoreBounds=True)

    # Set up data buffer for time evolution plots
    buffersize = 40000 # Change this number for showing a longer period in time evolution plots
    databuffer = np.zeros([7,buffersize])
    bufferrange = np.arange(buffersize)
    databuffer[0,:] = bufferrange
    starttime = time.time()


    rotangle = 0




    '''Errorhandling not implemented properly!!'''

    # Check for available cameras and set up menu
    if RealData:

        camera.GetDeviceKeyList()
        NumberCams = camera.GetDeviceKeyListSize()
        if NumberCams != 0:
            for i in range(NumberCams):
                camera.GetDeviceKeyListEntry(camindex=i)
                serial = camera.GetDeviceInformation()
                ui.choosecam.addItem(serial)
                i += 1
            # ui.choosecam.addItem('Test') #only for testing!!



        else:
            print 'ERROR -- No cameras found!!'

        CamIndex = ui.choosecam.currentIndex()
        camera.GetDeviceKeyListEntry(camindex=CamIndex)
        print camera.CamIndex.value, 'Camera Index'
        camera.StartCam()
        InitializeCam(camera,ui)



    # Show the window
    win.show()


                
    def updateview():
        '''
        This method upadates the image that is shown. 
        The orientation chosen is taken into account and the ROI boundaries are set properly.
        When the 'Hold' Button is pressed, the image is not updated.
        After updating the image, the method 'updateRoi' is called.
        '''

        global ImageArray, img

        # simulation.NewImage()
        # simulation.AddWhiteNoise()
        # simulation.AddRandomGauss()
        # simulation.SimulateTotalImage()
        hold = False
        hold = ui.hold.isChecked()

        if hold==False:


            if RealData==False:
                simulation.ChooseImage()
                ImageArray = simulation.image
            else:
                try:
                    camera.GrabNextImage()
                    ImageArray = camera.ImageArray
                except: # Show last image if grab failed -> Does not work (?)
                    ImageArray = np.rot90(ImageArray,-1*rotangle)

            ImageArray = np.rot90(ImageArray,rotangle)
            
            if rotangle==0 or rotangle==2:
                # view.setRange(QtCore.QRectF(0, 0, 754, 480))
                ui.x0Spin.setRange(0.,754.)
                ui.y0Spin.setRange(0.,480.)
                bounds = QtCore.QRectF(0,0,753,479)
                roi.maxBounds = bounds
                roisize = roi.size()
                roipos = roi.pos()
                if roisize[1] >= 480:
                    print roisize, roipos, 'ROI'
                    roi.setSize([200,200],finish=False)
                if roipos[1] >= (480-roisize[1]):
                    print roisize, roipos, 'ROI'
                    roi.setPos([200,200],finish=False)
                    roi.setSize([200,200],finish=False)
                    

                

            elif rotangle==1 or rotangle==3:
                # view.setRange(QtCore.QRectF(0, 0, 480, 754))
                ui.x0Spin.setRange(0.,480.)
                ui.y0Spin.setRange(0.,754.)
                bounds = QtCore.QRectF(0,0,479,753)
                roi.maxBounds = bounds
                roisize = roi.size()
                roipos = roi.pos()
                if roisize[0] >= 480:
                    roi.setSize([200,200],finish=False)
                if roipos[0] >= (480-roisize[0]):
                    roi.setPos([200,200],finish=False)
                    roi.setSize([200,200],finish=False)


               

            if RealData:
                camera.SetExposureTime(camera.CamIndex,ui.exposureSpin.value())
                camera.SetGainValue(camera.CamIndex,ui.gainSpin.value())

            img.setImage(ImageArray.T)

            if ui.connect.isChecked():
                upddateroipos(databuffer[3,-1],databuffer[4,-1])
            
            updateRoi()

        else:
            if RealData:
                camera.GrabNextImage()



    def updaterotangleccw():
        '''
        In this method the variable 'rotangle', indicating the rotation of the image is
        shifted forward by one in the counterclockwise direction.
        '''
        global rotangle

        rotangle = rotangle + 3
        rotangle = rotangle % 4


    def updaterotanglecw():
        '''
        In this method the variable 'rotangle', indicating the rotation of the image is
        shifted forward by one in the clockwise direction.
        '''
        global rotangle

        rotangle = rotangle + 1
        rotangle = rotangle % 4
    


            
            
      

    def updateRoi():
        '''
        In this method the Roi data is updated. It is called when the Roi position and/or shape changes
        and when the image is updated. The ROI data is summed up in vertical and horizontal directions 
        and plotted in the according diagrams. The total sum of the ROI is seen as Amplitude and displayed
        in the plot. A gaussian is fitted to the sums in horizontal and vertical direction. The fit results 
        are used to plot the peak position and contour. The beam properties are stored in a buffer and can
        be plotted in the time evolution plot.
        '''

        global ImageArray, img, databuffer

        # Get ROI data
        selected = roi.getArrayRegion(ImageArray.T, img)

        # Calculate amplitude
        amplitude = selected.sum()
        

        # Shift buffer one step forward and store amplitude and time stamp
        databuffer[1:,:-1] = databuffer[1:,1:]
        actualtime = time.time()
        databuffer[1,-1] = actualtime - starttime
        databuffer[2,-1] = amplitude


        # Plot sum in horizontal direction and fit gaussian
        datahor = selected.sum(axis=1)
        p2.plot(datahor, clear=True)
        FittedParamsHor = MatTools.FitGaussian(datahor)[0]
        xhor = np.arange(datahor.size)

        if ui.fitCheck.isChecked():
            p2.plot(MatTools.gaussian(xhor,*FittedParamsHor), pen=(0,255,0))


        # Plot amplitude
        xamp = np.array([1.,2.])
        yamp = np.array([amplitude])
        amphist.plot(xamp, yamp, stepMode=True, clear=True, fillLevel=0, brush=(0,0,255,150))

        # Plot sum in vertical direction and fit gaussian, save fit results in buffer and show in text box
        datavert = selected.sum(axis=0)
        p3.plot(datavert, clear=True).rotate(90)
        FittedParamsVert = MatTools.FitGaussian(datavert)[0]
        xvert = np.arange(datavert.size)

        if ui.fitCheck.isChecked():
            p3.plot(MatTools.gaussian(xvert,*FittedParamsVert), pen=(0,255,0)).rotate(90)
            poshor = FittedParamsHor[2]+roi.pos()[0]
            posvert = FittedParamsVert[2]+roi.pos()[1]
            waistx = FittedParamsHor[1]
            waisty = FittedParamsVert[1]

            databuffer[3,-1] = poshor
            databuffer[4,-1] = posvert
            databuffer[5,-1] = waistx
            databuffer[6,-1] = waisty

            updatetext(amplitude,poshor,posvert,waistx,waisty)

            

            


        if ui.trackCheck.isChecked():

            
            # Adjust cross hair
            hLine.setPos(FittedParamsVert[2]+roi.pos()[1])
            vLine.setPos(FittedParamsHor[2]+roi.pos()[0])

            vLine.show()
            hLine.show()

            # Plot peak
            pos = np.array([[(FittedParamsHor[2]+roi.pos()[0]),(FittedParamsVert[2]+roi.pos()[1])]])           
            peak.setData(pos,clear=True)

            # Plot contour
            x = np.linspace(-(FittedParamsHor[1]),(FittedParamsHor[1]),1000)
            sigmax = FittedParamsHor[1]
            sigmay = FittedParamsVert[1]
            y = ellipse(x,sigmax,sigmay)

            x = np.append(x,-x)
            y = np.append(y,-y)
            
            x += FittedParamsHor[2]+roi.pos()[0]
            y += FittedParamsVert[2]+roi.pos()[1]
            # X,Y = np.meshgrid(x,y)
            # contour.clear()
            contour.setData(x,y,clear=True)

        else:
            # view.removeItem(hLine)
            # view.removeItem(vLine)

            # Hide cross hair, peak and contour if 'Track beam' is not checked
            vLine.hide()
            hLine.hide()
            contour.clear()
            peak.clear()

        #When checked, the reference beam peak and contour is plotted   
        if ui.refCheck.isChecked():

            peakposition = np.array([[ui.x0Spin.value(),ui.y0Spin.value()]])
            peakpos.setData(peakposition,clear=True)


            sigmax = ui.sigmaxSpin.value()
            sigmay = ui.sigmaySpin.value()
            x = np.linspace(-(sigmax),(sigmax),1000)
            y = ellipse(x,sigmax,sigmay)

            x = np.append(x,-x)
            y = np.append(y,-y)
            
            x += ui.x0Spin.value()
            y += ui.y0Spin.value()
            # X,Y = np.meshgrid(x,y)
            # contour.clear()
            refcontour.setData(x,y,clear=True)

        else:
            peakpos.clear()
            refcontour.clear()


        # Update the time evolution plot
        updatetimescrolling()



    def updatetext(amplitude,x,y,waistx,waisty):
        '''
        The textbox giving information about the beam is updated.
        '''

        text.setHtml('<div style="text-align: center"><span style="color: #FFF; font-size: 16pt;">Beam Properties</span><br>\
            <span style="color: #FFF; font-size: 10pt;">Amplitude: %0.2f</span><br>\
            <span style="color: #FFF; font-size: 10pt;">Horizontal Position: %0.2f</span><br>\
            <span style="color: #FFF; font-size: 10pt;">Vertical Position: %0.2f</span><br>\
            <span style="color: #FFF; font-size: 10pt;">Horizontal Waist: %0.2f</span><br>\
            <span style="color: #FFF; font-size: 10pt;">Vertical Waist: %0.2f</span></div>' %(amplitude,x,y,waistx,waisty))

    def updatehold():
        '''
        Updates the boolean variable 'hold' when the 'Hold' button is pressed.
        '''
        global hold
        hold = True
        print hold, 'Hold'


    def updatecam():
        '''
        Updates the camera, when another one is chosen.
        '''
        camera.StopCam()
        CamIndex = ui.choosecam.currentIndex()
        print ui.choosecam.currentIndex(), 'Current Index'
        camera.GetDeviceKeyListEntry(camindex=CamIndex)
        camera.StartCam()
        InitializeCam(camera,ui)
        # print 'Camera changed!', camera.CamIndex.value


    def updatetimescrolling():
        '''
        The time evolution plot is updated.
        '''

        timescale = databuffer[1,:] - databuffer[1,-1]

        if ui.fitCheck.isChecked():
            ui.poshorRadio.setEnabled(True)
            ui.posvertRadio.setEnabled(True)
            ui.waisthorRadio.setEnabled(True)
            ui.waistvertRadio.setEnabled(True)
            ui.distRadio.setEnabled(True)
            if ui.ampRadio.isChecked():
                timeplot.plot(timescale,databuffer[2,:],clear=True)
                timeplot.setLabel('left', "Amplitude", units='')

            if ui.poshorRadio.isChecked():
                timeplot.plot(timescale,databuffer[3,:],clear=True)
                timeplot.setLabel('left', "Horizontal Position", units='px')

            if ui.posvertRadio.isChecked():
                timeplot.plot(timescale,databuffer[4,:],clear=True)
                timeplot.setLabel('left', "Vertical Position", units='px')

            if ui.waisthorRadio.isChecked():
                timeplot.plot(timescale,databuffer[5,:],clear=True)
                timeplot.setLabel('left', "Horizontal Waist", units='px')

            if ui.waistvertRadio.isChecked():
                timeplot.plot(timescale,databuffer[6,:],clear=True)
                timeplot.setLabel('left', "Vertical Waist", units='px')

            if ui.distRadio.isChecked():
                distance = np.sqrt((databuffer[3,:]-ui.x0Spin.value())**2+\
                    (databuffer[4,:]-ui.y0Spin.value())**2)
                timeplot.plot(timescale,distance,clear=True)
                timeplot.setLabel('left', "Distance to reference peak", units='px')

        else:
            ui.ampRadio.setChecked(True)
            timeplot.plot(timescale,databuffer[2,:],clear=True)
            timeplot.setLabel('left', "Amplitude", units='')
            ui.poshorRadio.setEnabled(False)
            ui.posvertRadio.setEnabled(False)
            ui.waisthorRadio.setEnabled(False)
            ui.waistvertRadio.setEnabled(False)
            ui.distRadio.setEnabled(False)

    def saveroisize():
        '''
        The ROI position is saved.
        '''
        global origroisize
        origroisize = roi.size()


    def upddateroipos(x,y):
        '''
        The ROI position is updated. The bounds are respected.
        '''
        
        imagesize = ImageArray.shape
        xpos = x-int(origroisize[0]/2.)
        xsize = origroisize[0]
        ysize = origroisize[1]
        if xpos < 0:
            xpos = 0
        ypos = y-int(origroisize[1]/2.)
        if ypos < 0:
            ypos = 0
        if xpos + origroisize[0] >= imagesize[1]:
            xsize = imagesize[1] - xpos - 1
        if ypos + origroisize[1] >= imagesize[0]:
            ysize = imagesize[0] - ypos - 1


        roi.setPos([xpos,ypos],finish=False)
        roi.setSize([xsize,ysize],finish=False)
        # roi.stateChanged()




    # Start timer for the loop
    viewtimer = QtCore.QTimer()

    # When another camera is chosen, the method 'updatecam' is called
    ui.choosecam.currentIndexChanged[int].connect(updatecam)

    # When the 'Connect ROI' button is pressed, 'saveroisize' is called
    ui.connect.toggled.connect(saveroisize)
    
    # When the ROI region has been changed, 'updateRoi' is called
    roi.sigRegionChangeFinished.connect(updateRoi)

    # When the 'Rotate counterclockwise' button is clicked, call 'updaterotangleccw'
    ui.rotccw.clicked.connect(updaterotangleccw)

    # When the 'Rotate clockwise' button is clicked, call 'updaterotanglecw'
    ui.rotcw.clicked.connect(updaterotanglecw)

    # When the timer is timed out, 'updateview' is called
    viewtimer.timeout.connect(updateview)
    
    # Start the timer: time out after 0 ms
    viewtimer.start(0)

    # When the GUI is closed: stop the timer
    app.exec_()
    viewtimer.stop()


# Start simulation
if RealData==False:
    simulation = Sim.GaussBeamSimulation()
    simulation.CreateImages()
    StartGUI()

# Start camera (API)
else: 
    camera = CamAPI.VRmagicUSBCam_API()
    # camera.InitializeCam()
    # camera.StartCam()
    StartGUI(camera)
    camera.StopCam()




