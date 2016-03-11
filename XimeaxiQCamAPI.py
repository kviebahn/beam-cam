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


'''Enum containing information about output image format'''

ImageFormat = {
    0:  'XI_MONO8'                   , # 8 bits per pixel
    1:  'XI_MONO16'                  , # 16 bits per pixel
    2:  'XI_RGB24'                   , # RGB data format
    3:  'XI_RGB32'                   , # RGBA data format
    4:  'XI_RGB_PLANAR'              , # RGB planar data format
    5:  'XI_RAW8'                    , # 8 bits per pixel raw data from sensor
    6:  'XI_RAW16'                   , # 16 bits per pixel raw data from sensor
    7:  'XI_FRM_TRANSPORT_DATA'      , # Data from transport layer (e.g. packed). Format see XI_PRM_TRANSPORT_PIXEL_FORMAT
}


# structure containing information about buffer policy(can be safe, data will be copied to user/app buffer 
# or unsafe, user will get internally allocated buffer without data copy).

XI_BP_UNSAFE = c_int(0)
XI_BP_SAFE = c_int(1)


class ImageDescription(Structure):
    '''Struct that holds the image description of areas'''

    _fields_ = [
    ('Area0Left',c_ulong),  # Pixels of Area0 of image left.
    ('Area1Left',c_ulong),  # Pixels of Area1 of image left.
    ('Area2Left',c_ulong),  # Pixels of Area2 of image left.
    ('Area3Left',c_ulong),  # Pixels of Area3 of image left.
    ('Area4Left',c_ulong),  # Pixels of Area4 of image left.
    ('Area5Left',c_ulong),  # Pixels of Area5 of image left.
    ('ActiveAreaWidth',c_ulong),    # Width of active area.
    ('Area5Right',c_ulong), # Pixels of Area5 of image right.
    ('Area4Right',c_ulong), # Pixels of Area4 of image right.
    ('Area3Right',c_ulong), # Pixels of Area3 of image right.
    ('Area2Right',c_ulong), # Pixels of Area2 of image right.
    ('Area1Right',c_ulong), # Pixels of Area1 of image right.
    ('Area0Right',c_ulong), # Pixels of Area0 of image right.
    ('Area0Top',c_ulong),   # Pixels of Area0 of image top.
    ('Area1Top',c_ulong),   # Pixels of Area1 of image top.
    ('Area2Top',c_ulong),   # Pixels of Area2 of image top.
    ('Area3Top',c_ulong),   # Pixels of Area3 of image top.
    ('Area4Top',c_ulong),   # Pixels of Area4 of image top.
    ('Area5Top',c_ulong),   # Pixels of Area5 of image top.
    ('ActiveAreaHeight',c_ulong),   # Height of active area.
    ('Area5Bottom',c_ulong),    # Pixels of Area5 of image bottom.
    ('Area4Bottom',c_ulong),    # Pixels of Area4 of image bottom.
    ('Area3Bottom',c_ulong),    # Pixels of Area3 of image bottom.
    ('Area2Bottom',c_ulong),    # Pixels of Area2 of image bottom.
    ('Area1Bottom',c_ulong),    # Pixels of Area1 of image bottom.
    ('Area0Bottom',c_ulong),    # Pixels of Area0 of image bottom.
    ('format',c_ulong), # Current format of pixels. XI_GenTL_Image_Format_e.
    ('flags',c_ulong)   # description of areas and image.
    ]

    def __init__(self):
        pass


class Image(Structure):
    '''Struct that holds the image'''

    _fields_ = [
    ('size',c_ulong),       # Size of current structure on application side. When xiGetImage is called and size>=SIZE_XI_IMG_V2 then GPI_level, tsSec and tsUSec are filled.
    ('bp',c_void_p),        # pointer to data. If NULL, xiApi allocates new buffer.
    ('bp_size',c_ulong),    # Filled buffer size. When buffer policy is set to XI_BP_SAFE, xiGetImage will fill this field with current size of image data received.
    ('frm',c_uint),    # format of incoming data.
    ('width',c_ulong),      # width of incoming image.
    ('height',c_ulong),     # height of incoming image.
    ('nframe',c_ulong),     # frame number(reset by exposure, gain, downsampling change).
    ('tsSec',c_ulong),      # TimeStamp in seconds
    ('tsUSec',c_ulong),     # TimeStamp in microseconds
    ('GPI_level',c_ulong),  # Input level
    ('black_level',c_ulong),# Black level of image (ONLY for MONO and RAW formats)
    ('padding_x',c_ulong),  # Number of extra bytes provided at the end of each line to facilitate image alignment in buffers. 
    ('AbsoluteOffsetX',c_ulong),# Horizontal offset of origin of sensor and buffer image first pixel.
    ('AbsoluteOffsetY',c_ulong),# Vertical offset of origin of sensor and buffer image first pixel.
    ('transport_frm',c_ulong),  # Current format of pixels on transport layer. XI_GenTL_Image_Format_e.
    ('img_desc',ImageDescription),          # description of image areas and format.
    ('DownsamplingX',c_ulong),  # Horizontal downsampling
    ('DownsamplingY',c_ulong),  # Vertical downsampling
    ('flags',c_ulong),      # description of XI_IMG.
    ('exposure_time_us',c_ulong),   # Exposure time of this image in microseconds
    ('gain_db',c_float),           # Gain used for this image in deci-bells
    ('acq_nframe',c_ulong)  # Number of frames acquired from acquisition start
    ]

    def __init__(self):
        pass



class ImageShort(Structure):
    '''Struct that holds the image'''

    _fields_ = [
    ('size',c_ulong),       # Size of current structure on application side. When xiGetImage is called and size>=SIZE_XI_IMG_V2 then GPI_level, tsSec and tsUSec are filled.
    ('bp',c_void_p),        # pointer to data. If NULL, xiApi allocates new buffer.
    ('bp_size',c_ulong),    # Filled buffer size. When buffer policy is set to XI_BP_SAFE, xiGetImage will fill this field with current size of image data received.
    ('frm',c_uint),    # format of incoming data.
    ('width',c_ulong),      # width of incoming image.
    ('height',c_ulong),     # height of incoming image.
    ('nframe',c_ulong),     # frame number(reset by exposure, gain, downsampling change).
    ('tsSec',c_ulong),      # TimeStamp in seconds
    ('tsUSec',c_ulong),     # TimeStamp in microseconds
    ('GPI_level',c_ulong),  # Input level
    ('black_level',c_ulong),# Black level of image (ONLY for MONO and RAW formats)
    ('padding_x',c_ulong),  # Number of extra bytes provided at the end of each line to facilitate image alignment in buffers. 
    ('AbsoluteOffsetX',c_ulong)# Horizontal offset of origin of sensor and buffer image first pixel.
    ]

    def __init__(self):
        pass





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
        self.imagecontainer = Image()


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


    def StartAcquisition(self):

        self.imagecontainer.size = SIZE_XI_IMG_V2
        self.imagecontainer.bp = None
        self.imagecontainer.bp_size = 0

        self.GetErrorInfo(self.dll.xiSetParamInt(self.handle,c_char_p('buffer_policy'),XI_BP_SAFE))
        print "Set buffer policy"

        self.GetErrorInfo(self.dll.xiStartAcquisition(self.handle))

        print "Start Acquisition"


    def StopAcquisition(self):

        self.GetErrorInfo(self.dll.xiStopAcquisition(self.handle))

        print "Stop Acquisition"

    def GetNextImage(self):

        timeout = c_ulong(5000)
        # imagecontainer = ImageShort()

        self.dll.xiGetImage.argtypes = [c_void_p,c_ulong,POINTER(Image)]
        self.GetErrorInfo(self.dll.xiGetImage(self.handle,timeout,byref(self.imagecontainer)))

        # if self.imagecontainer.frm == 0 or self.imagecontainer.frm == 5:
        #     img_array = np.asarray(int(self.imagecontainer.bp[:self.imagecontainer.bp_size])).reshape((self.imagecontainer.height,self.imagecontainer.width))
        #     self.imageArray = img_array

        print 'Get Image'
        print ImageFormat[self.imagecontainer.frm] ,"Color Format"
        print self.imagecontainer.width, "image width"
        print self.imagecontainer.height, "image height"
        print 'image', self.imagecontainer.bp

        arraytype = c_ubyte*self.imagecontainer.bp_size

        # imagepointer = np.zeros(self.imagecontainer.bp_size)
        imagepointer = cast(self.imagecontainer.bp,POINTER(arraytype))
        print 'imagepointer', imagepointer
        imagearray = np.frombuffer(imagepointer.contents,dtype=np.uint8)
        # imagearray = np.asarray(imagepointer.contents,dtype=np.uint8)
        # print 'imagedatalist', imagearray
        print 'imagesize', len(imagearray)
        imagearray = imagearray.reshape((int(self.imagecontainer.height),int(self.imagecontainer.width)))
        print 'Imageshape', imagearray.shape
        print 'Image Data Type', imagearray.dtype
        self.imageArray = imagearray.astype(float)
        print 'Imagelist', self.imageArray[588,458]


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

    	expotime = c_int(0)

    	self.dll.xiGetParamInt.argtypes = [c_void_p,c_char_p,POINTER(c_int)]

    	self.GetErrorInfo(self.dll.xiGetParamInt(self.handle, c_char_p('exposure'), byref(expotime)))

    	print expotime.value, "Exposure time"


    def SetExposureTime(self,exposuretime=0):

    	expotime = c_int(exposuretime)

    	self.dll.xiSetParamInt.argtypes = [c_void_p,c_char_p,c_int]

    	self.GetErrorInfo(self.dll.xiSetParamInt(self.handle, c_char_p('exposure'), expotime))

    	print "Set Exposure Time to ..."








if __name__=="__main__":
    check = XimeaxiQCam_API()
    check.GetNumberCams()
    
    check.GetDeviceInfo()

    # check.CloseCamera()
    check.OpenCamera()
    check.StartAcquisition()
    check.GetNextImage()
    image = check.imageArray
    # check.GetExposureTime()
    # check.SetExposureTime(100)
    # check.GetExposureTime()
    check.StopAcquisition()
    # check.GetDeviceName()
    check.CloseCamera()


    plt.figure()
    plt.imshow(image)

    del check.handle




    plt.show()







