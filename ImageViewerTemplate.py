# -*- coding: utf-8 -*-
'''
This file is part of beam-cam, a camera project to monitor and characterise laser beams.
Copyright (C) 2015 Christian Gross <christian.gross@mpq.mpg.de>, Timon Hilker <timon.hilker@mpq.mpg.de>, Michael Hoese <michael.hoese@physik.lmu.de> and Konrad Viebahn <kv291@cam.ac.uk> 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

Please see the README.md file for a copy of the GNU General Public License, or otherwise find it on <http://www.gnu.org/licenses/>.

'''

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s



class Ui_Form(object):
    
    def setupUi(self, Form):
        '''Defines the general properties of the window'''
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(1500, 1000)

        # self.myQMenuBar = QtGui.QMenuBar(Form)
        # exitMenu = self.myQMenuBar.addMenu('File')
        # exitAction = QtGui.QAction('Exit', Form)        
        # exitAction.triggered.connect(QtGui.qApp.quit)
        # exitMenu.addAction(exitAction)

        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))


        # self.statusBar()


        # extractAction = QtGui.QAction("&GET TO THE CHOPPAH!!!", self)
        # extractAction.setShortcut("Ctrl+Q")
        # extractAction.setStatusTip('Leave The App')
        # extractAction.triggered.connect(QtGui.qApp.quit)

        # '''Set up the menu bar'''
        # self.mainMenu = QtGui.QMenuBar(Form)
        # self.mainMenu.setNativeMenuBar(False)
        # fileMenu = self.mainMenu.addMenu('&amp;File')
        # fileMenu.addAction(extractAction)

        # self.myQMenuBar = QtGui.QMenuBar(Form)
        # exitMenu = self.myQMenuBar.addMenu('File')
        # exitAction = QtGui.QAction('Exit', Form)        
        # exitAction.triggered.connect(QtGui.qApp.quit)
        # exitMenu.addAction(exitAction)

        # Form.setMenuBar(self.myQMenuBar)

        # self.gridLayout.addWidget(self.myQMenuBar, 0, 0, 1, 0)



        
        '''Defines the text label for reference beam properties'''
        self.refbeamlabel = QtGui.QLabel(Form)
        self.refbeamlabel.setObjectName(_fromUtf8("refbeamlabel"))
        self.gridLayout.addWidget(self.refbeamlabel, 2, 0, 1, 1)

        '''Defines the spin box for x0'''
        self.x0Spin = QtGui.QDoubleSpinBox(Form)
        self.x0Spin.setRange(0.,754.)
        self.x0Spin.setProperty("value", 350)
        self.x0Spin.setObjectName(_fromUtf8("x0Spin"))
        self.gridLayout.addWidget(self.x0Spin, 3, 0, 1, 1)
        
        '''Defines the label for the x0 spin box'''
        self.x0label = QtGui.QLabel(Form)
        self.x0label.setObjectName(_fromUtf8("x0label"))
        self.gridLayout.addWidget(self.x0label, 3, 1, 1, 1)

        '''Defines the spin box for y0'''
        self.y0Spin = QtGui.QDoubleSpinBox(Form)
        self.y0Spin.setRange(0.,480.)
        self.y0Spin.setProperty("value", 240)
        self.y0Spin.setObjectName(_fromUtf8("y0Spin"))
        self.gridLayout.addWidget(self.y0Spin, 4, 0, 1, 1)
        
        '''Defines the label for the y0 spin box'''
        self.y0label = QtGui.QLabel(Form)
        self.y0label.setObjectName(_fromUtf8("y0label"))
        self.gridLayout.addWidget(self.y0label, 4, 1, 1, 1)

        '''Defines the spin box for the horizontal waist'''
        self.sigmaxSpin = QtGui.QDoubleSpinBox(Form)
        self.sigmaxSpin.setRange(0.,500.)
        self.sigmaxSpin.setProperty("value", 30.)
        self.sigmaxSpin.setObjectName(_fromUtf8("sigmaxSpin"))
        self.gridLayout.addWidget(self.sigmaxSpin, 5, 0, 1, 1)

        '''Defines the label for the horizontal waist spin box'''
        self.sigmaxlabel = QtGui.QLabel(Form)
        self.sigmaxlabel.setObjectName(_fromUtf8("sigmaxlabel"))
        self.gridLayout.addWidget(self.sigmaxlabel, 5, 1, 1, 1)

        '''Defines the spin box for the vertical waist'''
        self.sigmaySpin = QtGui.QDoubleSpinBox(Form)
        self.sigmaySpin.setRange(0.,500.)
        self.sigmaySpin.setProperty("value", 50.)
        self.sigmaySpin.setObjectName(_fromUtf8("sigmaySpin"))
        self.gridLayout.addWidget(self.sigmaySpin, 6, 0, 1, 1)

        '''Defines the label for the vertical waist spin box'''
        self.sigmaylabel = QtGui.QLabel(Form)
        self.sigmaylabel.setObjectName(_fromUtf8("sigmaylabel"))
        self.gridLayout.addWidget(self.sigmaylabel, 6, 1, 1, 1)

        # self.rotangleSpin = QtGui.QDoubleSpinBox(Form)
        # self.rotangleSpin.setProperty("value", 200.)
        # self.rotangleSpin.setObjectName(_fromUtf8("rotangleSpin"))
        # self.gridLayout.addWidget(self.rotangleSpin, 5, 0, 1, 1)

        # self.rotanglelabel = QtGui.QLabel(Form)
        # self.rotanglelabel.setObjectName(_fromUtf8("rotanglelabel"))
        # self.gridLayout.addWidget(self.rotanglelabel, 5, 1, 1, 1)


        # '''Defines the label for the camera'''
        # self.camlabel = QtGui.QLabel(Form)
        # self.camlabel.setObjectName(_fromUtf8("camlabel"))
        # self.gridLayout.addWidget(self.camlabel, 2, 2, 1, 1)


        # '''Defines the field to choose a camera'''
        # self.choosecam = QtGui.QComboBox()
        # self.choosecam.setObjectName(_fromUtf8("choosecam"))
        # self.gridLayout.addWidget(self.choosecam, 3, 2, 1, 1)
        # self.choosecam.addItem("Test 1")
        # self.choosecam.addItem("Test 2")


        '''Defines the text label for camera settings'''
        self.camsettingslabel = QtGui.QLabel(Form)
        self.camsettingslabel.setObjectName(_fromUtf8("camsettingslabel"))
        self.gridLayout.addWidget(self.camsettingslabel, 5, 2, 1, 2)

        '''Defines the spin box for the exposure time'''
        self.exposureSpin = QtGui.QDoubleSpinBox(Form)
        # self.exposureSpin.setRange(0.,100.)
        # self.exposureSpin.setProperty("value", 1.)
        self.exposureSpin.setDecimals(3)
        # self.exposureSpin.setSingleStep(0.1)
        self.exposureSpin.setObjectName(_fromUtf8("exposureSpin"))
        self.gridLayout.addWidget(self.exposureSpin, 6, 2, 1, 1)

        '''Defines the label for the exposure time spin box'''
        self.exposurelabel = QtGui.QLabel(Form)
        self.exposurelabel.setObjectName(_fromUtf8("exposurelabel"))
        self.gridLayout.addWidget(self.exposurelabel, 6, 3, 1, 1)

        '''Defines the spin box for the gain value'''
        self.gainSpin = QtGui.QDoubleSpinBox(Form)
        # self.gainSpin.setRange(16.,64.)
        # self.gainSpin.setProperty("value", 16.)
        self.gainSpin.setDecimals(3)
        # self.gainSpin.setSingleStep(0.1)
        self.gainSpin.setObjectName(_fromUtf8("gainSpin"))
        self.gridLayout.addWidget(self.gainSpin, 7, 2, 1, 1)

        '''Defines the label for the gain value spin box'''
        self.gainlabel = QtGui.QLabel(Form)
        self.gainlabel.setObjectName(_fromUtf8("gainlabel"))
        self.gridLayout.addWidget(self.gainlabel, 7, 3, 1, 1)


        '''Defines the 'Save actual beam properties' push button'''
        self.saveprops =  QtGui.QPushButton('Save Current Beam Properties')
        self.saveprops.setObjectName(_fromUtf8("saveprops"))
        self.gridLayout.addWidget(self.saveprops, 3, 3, 2, 1)
        self.saveprops.setToolTip('Save the current beam properties into the corresponding .csv-file')



        '''Defines the heading for the 'fit options' column'''
        self.fitoptionslabel = QtGui.QLabel(Form)
        self.fitoptionslabel.setObjectName(_fromUtf8("fitoptionslabel"))
        self.gridLayout.addWidget(self.fitoptionslabel, 2, 4, 1, 1)

        self.fitoptgroup = QtGui.QButtonGroup(Form)
        '''Defines the 'Sum over ROI' push button'''
        self.fitsum =  QtGui.QPushButton('Sum Over ROI')
        self.fitsum.setObjectName(_fromUtf8("fitsum"))
        self.gridLayout.addWidget(self.fitsum, 3, 4, 1, 1)
        self.fitsum.setCheckable(True)
        self.fitsum.setToolTip('For fitting a gaussian the vertically/horizontally summed up data of the ROI is used')
        self.fitsum.setChecked(True)

        '''Defines the 'Select Data at Peak' push button'''
        self.fitline =  QtGui.QPushButton('Select Data at Peak')
        self.fitline.setObjectName(_fromUtf8("fitline"))
        self.gridLayout.addWidget(self.fitline, 4, 4, 1, 1)
        self.fitline.setCheckable(True)
        self.fitline.setToolTip('For fitting a gaussian the vertical/horizontal line of data at the peak is selec')

        self.fitoptgroup.addButton(self.fitsum)
        self.fitoptgroup.addButton(self.fitline)


        '''Defines the buttons for the method for select data at peak fit'''
        self.plotselectedmethodgroup = QtGui.QButtonGroup(Form)

        '''Defines the max before radio button'''
        self.maxbeforeRadio = QtGui.QRadioButton(Form)
        # if self.fitline.isChecked():
        #     self.maxbeforeRadio.setChecked(True)
        # self.maxbeforeRadio.setChecked(True)
        self.maxbeforeRadio.setObjectName(_fromUtf8("maxbeforeRadio"))
        self.gridLayout.addWidget(self.maxbeforeRadio, 5, 4, 1, 1)

        '''Defines the abs max radio button'''
        self.absmaxRadio = QtGui.QRadioButton(Form)
        self.absmaxRadio.setChecked(True)
        self.absmaxRadio.setObjectName(_fromUtf8("absmaxRadio"))
        self.gridLayout.addWidget(self.absmaxRadio, 6, 4, 1, 1)
        # self.absmaxRadio.setCheckable(False)

        '''Defines the self max radio button'''
        self.selfmaxRadio = QtGui.QRadioButton(Form)
        self.selfmaxRadio.setObjectName(_fromUtf8("selfmaxRadio"))
        self.gridLayout.addWidget(self.selfmaxRadio, 7, 4, 1, 1)

        '''Adds buttons to group'''
        self.plotselectedmethodgroup.addButton(self.maxbeforeRadio)
        self.plotselectedmethodgroup.addButton(self.absmaxRadio)
        self.plotselectedmethodgroup.addButton(self.selfmaxRadio)


        '''Defines the 'Autoscale ROI' push button'''
        self.autoscale =  QtGui.QPushButton('Autoscale ROI')
        self.autoscale.setObjectName(_fromUtf8("autoscale"))
        self.gridLayout.addWidget(self.autoscale, 2, 5, 1, 1)
        self.autoscale.setCheckable(False)
        self.autoscale.setToolTip('Automatically scale the ROI to three times the beam waist')

        '''Defines the 'Connect ROI' push button'''
        self.connect =  QtGui.QPushButton('Connect ROI')
        self.connect.setObjectName(_fromUtf8("connect"))
        self.gridLayout.addWidget(self.connect, 3, 5, 1, 1)
        self.connect.setCheckable(True)
        self.connect.setToolTip('Connect position of ROI<br>with the position of the peak')

        '''Defines the 'Hold' push button'''
        self.hold =  QtGui.QPushButton('Hold')
        self.hold.setObjectName(_fromUtf8("hold"))
        self.gridLayout.addWidget(self.hold, 4, 5, 1, 1)
        self.hold.setCheckable(True)
        self.hold.setToolTip('Pause the live view')
        # self.hold.setChecked(False)
        
        '''Analysis combo'''
        self.anaCombo = QtGui.QComboBox()
        self.anaCombo.setObjectName(_fromUtf8('analysis type'))
        self.gridLayout.addWidget(self.anaCombo, 3, 4, 1, 1)
        self.anaCombo.setToolTip('choose a analysis type')



        # '''Defins the text box for the 'orientation' heading'''
        # self.orientationlabel = QtGui.QLabel(Form)
        # self.orientationlabel.setObjectName(_fromUtf8("orientationlabel"))
        # self.gridLayout.addWidget(self.orientationlabel, 5, 4, 1, 1)

        # '''Defines the buttons for choosing the orientation'''
        # self.OrientationGroup = QtGui.QButtonGroup(Form)
        # self.horRadio = QtGui.QRadioButton(Form)
        # self.horRadio.setChecked(True)
        # self.horRadio.setObjectName(_fromUtf8("horRadio"))
        # self.gridLayout.addWidget(self.horRadio, 4, 4, 1, 1)
        # self.vertRadio = QtGui.QRadioButton(Form)
        # # self.vertRadio.setChecked(True)
        # self.vertRadio.setObjectName(_fromUtf8("vertRadio"))
        # self.gridLayout.addWidget(self.vertRadio, 5, 4, 1, 1)
        # # self.stack = QtGui.QStackedWidget(Form)
        # # self.stack.setObjectName(_fromUtf8("stack"))
        # self.OrientationGroup.addButton(self.horRadio)
        # self.OrientationGroup.addButton(self.vertRadio)


        # '''Defines the 'Rotate counterclockwise' push button'''
        # self.rotccw =  QtGui.QPushButton('Rotate counterclockwise')
        # self.rotccw.setObjectName(_fromUtf8("rotccw"))
        # self.gridLayout.addWidget(self.rotccw, 6, 4, 1, 1)
        # self.rotccw.setToolTip('Rotate the image 90 degrees counterclockwise')
        # self.hold.setChecked(False)


        # '''Defines the 'Rotate clockwise' push button'''
        # self.rotcw =  QtGui.QPushButton('Rotate clockwise')
        # self.rotcw.setObjectName(_fromUtf8("rotcw"))
        # self.gridLayout.addWidget(self.rotcw, 7, 4, 1, 1)
        # self.rotcw.setToolTip('Rotate the image 90 degrees clockwise')



        '''Defines the heading for the 'options' column'''
        self.optionslabel = QtGui.QLabel(Form)
        self.optionslabel.setObjectName(_fromUtf8("optionslabel"))
        self.gridLayout.addWidget(self.optionslabel, 5, 5, 1, 1)

        '''Defines the check box for fitting'''
        self.fitCheck = QtGui.QCheckBox(Form)
        self.fitCheck.setObjectName(_fromUtf8("fitCheck"))
        self.gridLayout.addWidget(self.fitCheck, 6, 5, 1, 1)
        self.fitCheck.setChecked(True)

        '''Defines the check box for tracking'''
        self.trackCheck = QtGui.QCheckBox(Form)
        self.trackCheck.setObjectName(_fromUtf8("trackCheck"))
        self.gridLayout.addWidget(self.trackCheck, 7, 5, 1, 1)
        self.trackCheck.setChecked(True)

        '''Defines the check box for the reference beam'''
        self.refCheck = QtGui.QCheckBox(Form)
        self.refCheck.setObjectName(_fromUtf8("refCheck"))
        self.gridLayout.addWidget(self.refCheck, 8, 5, 1, 1)
        self.refCheck.setChecked(True)


        '''Defines the heading for the 'time evolution plot' column'''
        self.evplotlabel = QtGui.QLabel(Form)
        self.evplotlabel.setObjectName(_fromUtf8("evplotlabel"))
        self.gridLayout.addWidget(self.evplotlabel, 2, 6, 1, 1)

        '''Defines the buttons for the time evolution plot'''
        self.TimeEvGroup = QtGui.QButtonGroup(Form)
        self.ampRadio = QtGui.QRadioButton(Form)
        self.ampRadio.setChecked(True)
        self.ampRadio.setObjectName(_fromUtf8("ampRadio"))
        self.gridLayout.addWidget(self.ampRadio, 3, 6, 1, 1)

        self.poshorRadio = QtGui.QRadioButton(Form)
        # self.poshorRadio.setChecked(True)
        self.poshorRadio.setObjectName(_fromUtf8("poshorRadio"))
        self.gridLayout.addWidget(self.poshorRadio, 4, 6, 1, 1)

        self.posvertRadio = QtGui.QRadioButton(Form)
        self.posvertRadio.setObjectName(_fromUtf8("posvertRadio"))
        self.gridLayout.addWidget(self.posvertRadio, 5, 6, 1, 1)

        self.waisthorRadio = QtGui.QRadioButton(Form)
        self.waisthorRadio.setObjectName(_fromUtf8("waisthorRadio"))
        self.gridLayout.addWidget(self.waisthorRadio, 6, 6, 1, 1)

        self.waistvertRadio = QtGui.QRadioButton(Form)
        self.waistvertRadio.setObjectName(_fromUtf8("waistvertRadio"))
        self.gridLayout.addWidget(self.waistvertRadio, 7, 6, 1, 1)

        self.distRadio = QtGui.QRadioButton(Form)
        self.distRadio.setObjectName(_fromUtf8("distRadio"))
        self.gridLayout.addWidget(self.distRadio, 8, 6, 1, 1)
        
        self.TimeEvGroup.addButton(self.ampRadio)
        self.TimeEvGroup.addButton(self.poshorRadio)
        self.TimeEvGroup.addButton(self.posvertRadio)
        self.TimeEvGroup.addButton(self.waisthorRadio)
        self.TimeEvGroup.addButton(self.waistvertRadio)
        self.TimeEvGroup.addButton(self.distRadio)





        '''Defines the plot widget'''
        self.plot = GraphicsLayoutWidget(Form)
        self.plot.setObjectName(_fromUtf8("plot"))
        self.gridLayout.addWidget(self.plot, 1, 0, 1, 7)


        '''Puts everything together'''
        self.retranslateUi(Form)
        # self.stack.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        '''Sets the right names to the objects'''

        # Form.setWindowTitle(QtGui.QApplication.translate("Form", "VRmagic USB Cam Live View", None, QtGui.QApplication.UnicodeUTF8))
        # self.pixelModeCheck.setText(QtGui.QApplication.translate("Form", "pixel mode", None, QtGui.QApplication.UnicodeUTF8))
        self.refbeamlabel.setText(QtGui.QApplication.translate("Form", "Reference Beam", None, QtGui.QApplication.UnicodeUTF8))
        self.x0label.setText(QtGui.QApplication.translate("Form", "x(0)", None, QtGui.QApplication.UnicodeUTF8))
        self.y0label.setText(QtGui.QApplication.translate("Form", "y(0)", None, QtGui.QApplication.UnicodeUTF8))
        self.sigmaxlabel.setText(QtGui.QApplication.translate("Form", "Waist horizontal", None, QtGui.QApplication.UnicodeUTF8))
        self.sigmaylabel.setText(QtGui.QApplication.translate("Form", "Waist vertical", None, QtGui.QApplication.UnicodeUTF8))
        # self.rotanglelabel.setText(QtGui.QApplication.translate("Form", "Rotation angle", None, QtGui.QApplication.UnicodeUTF8))
        # self.camlabel.setText(QtGui.QApplication.translate("Form", "Camera", None, QtGui.QApplication.UnicodeUTF8))
        self.camsettingslabel.setText(QtGui.QApplication.translate("Form", "Camera settings", None, QtGui.QApplication.UnicodeUTF8))
        self.exposurelabel.setText(QtGui.QApplication.translate("Form", "Exposure time [ms]", None, QtGui.QApplication.UnicodeUTF8))
        self.gainlabel.setText(QtGui.QApplication.translate("Form", "Gain", None, QtGui.QApplication.UnicodeUTF8))
        

        # self.orientationlabel.setText(QtGui.QApplication.translate("Form", "Orientation", None, QtGui.QApplication.UnicodeUTF8))
        # self.horRadio.setText(QtGui.QApplication.translate("Form", "horizontal", None))
        # self.vertRadio.setText(QtGui.QApplication.translate("Form", "vertical", None))

        self.fitoptionslabel.setText(QtGui.QApplication.translate("Form", "Fit Options", None, QtGui.QApplication.UnicodeUTF8))
        self.maxbeforeRadio.setText(QtGui.QApplication.translate("Form", "Maximum Before", None))
        self.absmaxRadio.setText(QtGui.QApplication.translate("Form", " Absolute Maximum", None))
        self.selfmaxRadio.setText(QtGui.QApplication.translate("Form", " Self Defined Maximum", None))

        self.optionslabel.setText(QtGui.QApplication.translate("Form", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.fitCheck.setText(QtGui.QApplication.translate("Form", "Show Fit", None, QtGui.QApplication.UnicodeUTF8))
        self.trackCheck.setText(QtGui.QApplication.translate("Form", "Track Beam", None, QtGui.QApplication.UnicodeUTF8))
        self.refCheck.setText(QtGui.QApplication.translate("Form", "Show Reference Beam", None, QtGui.QApplication.UnicodeUTF8))

        self.evplotlabel.setText(QtGui.QApplication.translate("Form", "Time Evolution Plot", None, QtGui.QApplication.UnicodeUTF8))
        self.ampRadio.setText(QtGui.QApplication.translate("Form", "Amplitude", None))
        self.poshorRadio.setText(QtGui.QApplication.translate("Form", "Horizontal Position", None))
        self.posvertRadio.setText(QtGui.QApplication.translate("Form", "Vertical Position", None))
        self.waisthorRadio.setText(QtGui.QApplication.translate("Form", "Horizontal Waist", None))
        self.waistvertRadio.setText(QtGui.QApplication.translate("Form", "Vertical Waist", None))
        self.distRadio.setText(QtGui.QApplication.translate("Form", "Distance", None))


from pyqtgraph import GraphicsLayoutWidget
