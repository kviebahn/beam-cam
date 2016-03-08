# -*- coding: utf-8 -*-
"""
Created on Tue Mar 01 11:20:45 2016

@author: Michael

This Script provides a Python interface to VR Magic USB Cameras. It only contains the most relevant methods.
If necessary, other methods can be implemented by using the the header file "vrmusbcam2.h".

This Script defines a subclass to "CameraAPI.py" working with Ximea xiQ cameras.

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
"""

from CameraAPI import Camera_API

from XimeaxiQCamAPIconstants import *

from ctypes import *
import numpy as np
import sys
import matplotlib.pyplot as plt



'''
Add Error Handling!!!
'''






class XimeaxiQCam_API(Camera_API):
    '''Functions for the Ximea xiQ Camera.'''


    def __init__(self, dllPath='xiapi64.dll'):

        # Connect to library
        self.dll = cdll.LoadLibrary(dllPath)

        # Variables herited from Camera_API
        self.imageArray = None

        self.cameraList = None

        self.imageSize = None
        self.saturationValue = None
        self.exposureTime = None
        self.exposureRange = None
        self.exposureSteps = None
        self.gainValue = None
        self.gainRange = None
        self.gainSteps = None

        #Own variables
        self.numberCams = None
        self.camIndex = 0
        self.handle = c_void_p()


    def GetErrorInfo(self,errornum=0):

    	if errornum >= 0:
    		print error_codes[errornum]
    	else:
    		pass




    def GetNumberCams(self):

    	numbercams = c_uint32(0)

    	self.GetErrorInfo(self.dll.xiGetNumberDevices(byref(numbercams)))

    	self.numberCams = numbercams.value

    	print "Number of Cameras: ", numbercams.value
    	


    def GetDeviceInfo(self):



    	camid =c_ulong(self.camIndex)
    	stringsize = c_ulong(0)
    	inf =create_string_buffer(512)
    	inf = c_char_p('')
    	# stringbuffer = create_string_buffer('device_name')
    	parameter = c_wchar_p(XI_PRM_DEVICE_NAME)
    	self.dll.xiGetDeviceInfoString.argtypes = [c_ulong,c_char_p,c_char_p,POINTER(c_ulong)]
    	print 'defined argtypes'

    	self.GetErrorInfo(self.dll.xiGetDeviceInfoString(camid, c_char_p('device_name'), inf, byref(stringsize)))
    	print 'read out info string'

    	# print "Success", stringsize
    	

    	name = string_at(inf)
    	del inf
    	

    	# name =''.join(name)

    	print "Device Name Length: ", stringsize.value
    	print "Device Name", name
    	


    def OpenCamera(self):

    	camid =c_ulong(self.camIndex)
    	
    	self.GetErrorInfo(self.dll.xiOpenDevice(camid,byref(self.handle)))

    	print "Camera opened succesfully"


    def CloseCamera(self):

    	self.GetErrorInfo(self.dll.xiCloseDevice(self.handle))

    	print "Device closed!"


    def GetDeviceName(self):

    	inf2 =create_string_buffer(512)
    	stringsize = c_ulong()
    	inf2 = c_char_p('')

    	self.dll.xiGetParamString.argtypes = [c_void_p,c_char_p,c_char_p,POINTER(c_ulong)]
    	print 'defined argtypes'

    	self.GetErrorInfo(self.dll.xiGetParamString(self.handle, c_char_p('device_id'), inf2, byref(stringsize)))

    	name2 = string_at(inf2)

    	print "Device ID Length: ", stringsize.value
    	print "Device ID", name2




    def GetExposureTime(self):

    	expotime = c_int64(0)

    	self.dll.xiGetParamInt.argtypes = [c_void_p,c_char_p,POINTER(c_int64)]

    	self.GetErrorInfo(self.dll.xiGetParamInt(self.handle, c_char_p('exposure'), byref(expotime)))

    	print expotime.value, "Exposure time"


    def SetExposureTime(self,exposuretime=0):

    	expotime = c_int64(exposuretime)

    	self.dll.xiSetParamInt.argtypes = [c_void_p,c_char_p,c_int64]

    	self.GetErrorInfo(self.dll.xiSetParamInt(self.handle, c_char_p('exposure'), expotime))

    	print "Set Exposure Time to ..."








if __name__=="__main__":
    check = XimeaxiQCam_API()
    check.GetNumberCams()
    
    check.GetDeviceInfo()

    # check.CloseCamera()
    check.OpenCamera()
    check.GetExposureTime()
    check.SetExposureTime(10)
    check.GetExposureTime()
    # check.GetDeviceName()
    check.CloseCamera()

    del check.handle












