# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 11:50:45 2016

@author: Michael

This Script provides a Python interface to VR Magic USB Cameras. It only contains the most relevant methods.
If necessary, other methods can be implemented by using the the header file "vrmusbcam2.h".

This Script defines a subclass to "CameraAPI.py" working with VRmagic USB cameras. It is the improved version of
"VRmUsbCamAPI.py".

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
# reload (CameraAPI)

from ctypes import *
import numpy as np
import sys
import matplotlib.pyplot as plt

'''
DO NOT CHANGE!!
Adresses of adjustable properties of the camera.
'''
ExposureTimeAddress = c_int(0x1001)
ExposureAutoAddress = c_int(0x1003)
GainValueAddress = c_int(0x1023)
GainAutoAddress = c_int(0x1024)
FilterGammaAddress = c_int(0x3100)
FilterLuminanceAddress = c_int(0x3101)
FilterContrastAddress = c_int(0x3102)
FilterBlacklevelAddress = c_int(0x3103)
SensorRoiAddress = c_int(0x3010)
PixelClockAddress = c_int(0x2100)
HBlankDurationAddress = c_int(0x1010)
VBlankDurationAddress = c_int(0x1011)
VRefAddress = c_int(0x1070)
BlacklevelAutoAddress = c_int(0x1071)
BlacklevelAdjustAddress = c_int(0x1072)
FlipHorizontalAddress = c_int(0x1046)
FlipVerticalAddress = c_int(0x1047)
SourceFormatAddress = c_int(0x3000)
StatusLEDAddress = c_int(0x2008)

class CameraKey(Structure):
    '''Struct that holds the key of a camera'''

    _fields_ = [
    ('m_serial',c_uint),
    ('mp_manufacturer_str',POINTER(c_char)),
    ('mp_product_str',POINTER(c_char)),
    ('m_busy',c_uint),
    ('mp_private',POINTER(c_void_p))
    ]

    def __init__(self):
        pass

class ImageFormat(Structure):
    '''Struct that holds the image format'''

    _fields_ = [
    ('m_width',c_uint),
    ('m_height',c_uint),
    ('m_color_format',c_int),
    ('m_image_modifier',c_int)
    ]

    def __init__(self):
        pass

class Image(Structure):
    '''Struct that holds the image'''

    _fields_ = [
    ('m_image_format',ImageFormat),
    ('mp_buffer',POINTER(c_char)),
    ('m_pitch',c_uint),
    ('m_time_stamp',c_double),
    ('mp_private',POINTER(c_void_p))
    ]

    def __init__(self):
        pass

# class Rect(Structure):
#     '''Struct that holds the data for a roi of the image'''

#     _fields_ = [
#     ('m_left',c_int),
#     ('m_top',c_int),
#     ('m_width',c_int),
#     ('m_height',c_int)
#     ]

#     def __init__(self):
#         pass

class ExpoTimeProps(Structure):
    '''Struct that holds the data of the properties of the exposure time'''

    _fields_ = [
    ('m_default',c_float),
    ('m_min',c_float),
    ('m_max',c_float),
    ('m_step',c_float)
    ]

    def __init__(self):
        pass

class GainProps(Structure):
    '''Struct that holds the data of the properties of the gain value'''

    _fields_ = [
    ('m_default',c_int),
    ('m_min',c_int),
    ('m_max',c_int),
    ('m_step',c_int)
    ]

    def __init__(self):
        pass




class VRmagicUSBCam_API(Camera_API):
    '''Functions for the VR Magic USB Camera.'''


    def __init__(self, dllPath='vrmusbcam2.dll'):

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

        # Own variables
        self.key = None
        self.keytest = 0
        self.CamIndex = None
        self.format = ImageFormat()








    def ShowErrorInformation(self):
        '''In case an error occurs, the method shows the according error message in the console'''

        inf = POINTER(c_char)
        addr = self.dll.VRmUsbCamGetLastError()
        # addr = c_int(addr)

        message = cast(addr, inf)

        Message = []
        i = 0
        while message[i] != '\0':
            Message.append(message[i])
            i += 1
        Message = ''.join(Message)
        print '!ERROR!: ', Message


    def GetDeviceKeyList(self):
        '''The method gets the device key list'''

        Error = self.dll.VRmUsbCamUpdateDeviceKeyList()

        if Error==0:
            self.ShowErrorInformation()

        print 'KeyList'

    def GetDeviceKeyListSize(self):
        '''
        The method gets the size of the device key list.
        The size gives the number of connected cameras.
        '''

        No=c_uint(0)
        Error = self.dll.VRmUsbCamGetDeviceKeyListSize(byref(No))

        print 'Number of cameras', No.value
        if Error==1:
            return No.value
        else:
            self.ShowErrorInformation()
            return 0

        


    def GetDeviceKeyListEntry(self,camindex=0):
        '''The method gets the key that belongs to a camera with a certain index.'''

        self.CamIndex = camindex
        self.CamIndex = c_uint(self.CamIndex)

        # Key_p = POINTER(CameraKey)
        self.dll.VRmUsbCamGetDeviceKeyListEntry.argtypes = [c_uint,POINTER(POINTER(CameraKey))]
        
        self.key = POINTER(CameraKey)()
        
        Key = self.dll.VRmUsbCamGetDeviceKeyListEntry(self.CamIndex,byref(self.key))

        if Key==0:
            self.ShowErrorInformation()
            self.keytest = 0
        else:
            self.keytest = 1
        

    def GetDeviceInformation(self):
        '''The method gets information about a camera (product ID and serial string).'''

        if self.keytest==0:
            print 'No valid key available!'
            return None
        else:
            ID = c_uint(0)

            ErrID = self.dll.VRmUsbCamGetProductId(self.key,byref(ID))

            inf = POINTER(c_char)()

            Errinf = self.dll.VRmUsbCamGetSerialString(self.key,byref(inf))

            print 'Key', self.key
            print ErrID, 'ID', ID.value

            serial = []
            i = 0
                
            while inf[i] != '\0':
                serial.append(inf[i])
                i += 1
            serial = ''.join(serial)
            print 'Serial String: ', serial
            print 'Busy: ', self.key.contents.m_busy

            return serial


    '''
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    Functions to handle important properties
    The 'Get...' Function gets the actual value;
    The 'Set...' Function sets the value to the committed value
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    '''



    '''Switch on/off status LED'''
    def GetStatusLED(self):

        StatusLED = c_bool(0)
        Error = self.dll.VRmUsbCamGetPropertyValueB(self.CamIndex, StatusLEDAddress, byref(StatusLED))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Status LED on: ', StatusLED.value

    def SetStatusLED(self,statusled=False):

        StatusLED = c_bool(statusled)
        Error = self.dll.VRmUsbCamSetPropertyValueB(self.CamIndex, StatusLEDAddress, byref(StatusLED))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Status LED set to: ', StatusLED.value


    '''
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    Functions to handle images 
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    '''


    def UseSourceFormat(self):
        '''Get the source format and safe it as 'self.format'.'''
        Error = self.dll.VRmUsbCamGetSourceFormatEx(self.CamIndex,c_uint(1),byref(self.format))
        if Error==0:
            self.ShowErrorInformation()


    def GetSourceFormatInformation(self):
        '''Get information about the source format and print it in the console.'''
        inf = POINTER(c_char)()

        Error = self.dll.VRmUsbCamGetSourceFormatDescription(self.CamIndex,c_uint(1),byref(inf))
        if Error==0:
            self.ShowErrorInformation()

        sourceformat = []
        i = 0
                
        while inf[i] != '\0':
            sourceformat.append(inf[i])
            i += 1
        sourceformat = ''.join(sourceformat)
        print 'Source format: ', sourceformat





    # def GrabNextImage(self):
    #     '''
    #     The next image is grabbed and stored as a 'numpy array'.
    #     This array can then be used by external programs to display the image or a live view.
    #     '''

    #     self.dll.VRmUsbCamLockNextImageEx2.argtypes = [c_uint,c_uint,POINTER(POINTER(Image)),POINTER(c_uint),c_int]
                
    #     source_image_p = POINTER(Image)()

    #     framesdropped = c_uint(0)

    #     timeout = 5000

    #     Error = self.dll.VRmUsbCamLockNextImageEx2(self.CamIndex,c_uint(1),byref(source_image_p),byref(framesdropped),c_int(timeout))
                
    #     if Error==0:
    #         self.ShowErrorInformation()
    #     if Error==1:
    #         # print'Image taken!'

    #         ImageList = list(source_image_p.contents.mp_buffer[0:(self.format.m_height)*int(source_image_p.contents.m_pitch)])
    #         ImageList = [ord(i) for i in ImageList]
    #         # print len(ImageList)

    #         self.ImageArray = np.array(ImageList)
    #         self.ImageArray = np.reshape(self.ImageArray,(self.format.m_height,int(source_image_p.contents.m_pitch)))
    #         self.ImageArray = self.ImageArray[:,:self.format.m_width]


    #     Error = self.dll.VRmUsbCamUnlockNextImage(self.CamIndex,byref(source_image_p))
    #     # print 'Unlock Image'
    #     if Error==0:
    #         self.ShowErrorInformation()




    # def InitializeCam(self):
    #     '''The available cameras are intitialized.'''

    #     self.GetDeviceKeyList()
    #     self.GetDeviceKeyListEntry()




    # def StartCam(self):
    #     '''One camera is started.'''

    #     if self.keytest==0:
    #         print 'No valid key available!'
    #     elif self.key.contents.m_busy!=0:
    #         print 'Camera is busy!'
    #     else:
    #         Error = self.dll.VRmUsbCamOpenDevice(self.key,byref(self.CamIndex))
    #         if Error==0:
    #             self.ShowErrorInformation()
    #         else:
    #             print 'Device opened successfully'

    #             self.format = ImageFormat()
    #             self.GetSourceFormatInformation()
    #             self.UseSourceFormat()


    #             Error = self.dll.VRmUsbCamStart(self.CamIndex)
    #             print 'Started Cam'

    # def StopCam(self):
    #     '''One camera is stopped.'''

    #     Error = self.dll.VRmUsbCamStop(self.CamIndex)
    #     if Error==0:
    #         self.ShowErrorInformation()




    #     Error = self.dll.VRmUsbCamFreeDeviceKey(byref(self.key))
    #     if Error==0:
    #         self.ShowErrorInformation()

    #     Error = self.dll.VRmUsbCamCloseDevice(self.CamIndex)
    #     if Error==0:
    #         self.ShowErrorInformation()
    #     print 'Cam stopped'


    '''
    -----------------------------------------------------------------------------------------------
    New methods
    -----------------------------------------------------------------------------------------------
    '''

    def StartCamera(self,camindex=0):
        '''
        This method starts the camera.
        '''

        self.CamIndex = camindex
        self.GetDeviceKeyListEntry(camindex=camindex)


        if self.keytest==0:
            print 'No valid key available!'
        elif self.key.contents.m_busy!=0:
            print 'Camera is busy!'
        else:
            Error = self.dll.VRmUsbCamOpenDevice(self.key,byref(self.CamIndex))
            if Error==0:
                self.ShowErrorInformation()
            else:
                print 'Device opened successfully'

                # self.GetDeviceInformation()

                self.GetSourceFormatInformation()
                self.UseSourceFormat()

                Error = self.dll.VRmUsbCamStart(self.CamIndex)
                if Error==0:
                    self.ShowErrorInformation()
                else:
                    print 'Started Cam'


    def StopCamera(self):
        '''
        This method stops the camera, that is in use at the moment.
        '''

        Error = self.dll.VRmUsbCamStop(self.CamIndex)
        if Error==0:
            self.ShowErrorInformation()

        Error = self.dll.VRmUsbCamFreeDeviceKey(byref(self.key))
        if Error==0:
            self.ShowErrorInformation()

        Error = self.dll.VRmUsbCamCloseDevice(self.CamIndex)
        if Error==0:
            self.ShowErrorInformation()

        print 'Cam stopped'



    def CreateCameraList(self):

        '''
        This method creates a camera list. All available cameras of one type are listed in an array of
        strings (their serial number).
        '''

        self.GetDeviceKeyList()
        NumberCams = self.GetDeviceKeyListSize()
        cameralist = []
        if NumberCams != 0:
            for i in range(NumberCams):
                self.CamIndex = i
                self.GetDeviceKeyListEntry(camindex=i)
                serial = self.GetDeviceInformation()
                
                addlist = [serial]
                cameralist = cameralist + addlist
                # print cameralist, "cameralist"
                
                i += 1
            
        else:
            print 'ERROR -- No cameras found!!'


        self.cameraList = cameralist
        return cameralist


    def GetNextImage(self):
        '''
        This method gets the next image and stores it in self.imageArray.
        
        The next image is grabbed and stored as a 'numpy array'.
        This array can then be used by external programs to display the image or a live view.
        '''

        self.dll.VRmUsbCamLockNextImageEx2.argtypes = [c_uint,c_uint,POINTER(POINTER(Image)),POINTER(c_uint),c_int]
        source_image_p = POINTER(Image)()
        framesdropped = c_uint(0)
        timeout = 5000
        Error = self.dll.VRmUsbCamLockNextImageEx2(self.CamIndex,c_uint(1),byref(source_image_p),byref(framesdropped),c_int(timeout))
                
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:

            ImageList = list(source_image_p.contents.mp_buffer[0:(self.format.m_height)*int(source_image_p.contents.m_pitch)])
            ImageList = [ord(i) for i in ImageList]

            imagearray = np.array(ImageList)
            imagearray = np.reshape(imagearray,(self.format.m_height,int(source_image_p.contents.m_pitch)))
            imagearray = imagearray[:,:self.format.m_width]
            self.imageArray = imagearray

        Error = self.dll.VRmUsbCamUnlockNextImage(self.CamIndex,byref(source_image_p))
        if Error==0:
            self.ShowErrorInformation()


    def GetImageSize(self):
        '''
        This method reads out the actual image size and stores it in self.imageSize and returns the values
        as tuple (width,height).
        '''

        imagesize = (int(self.format.m_width),int(self.format.m_height))
        self.imageSize = imagesize

        return imagesize


    def GetSaturationValue(self):
        '''
        This method reads out the actual saturation value of the camera and stores it in self.saturationValue and returns the value.
        '''
        bytesperpxl = c_int(0)

        Error = self.dll.VRmUsbCamGetPixelDepthFromColorFormat(self.format.m_color_format,byref(bytesperpxl))

        if Error==0:
            self.ShowErrorInformation()
            return None

        else:
            satvalue = 2**(bytesperpxl.value*8) - 1
       
            # print 'Saturation value: ', satvalue

            self.saturationValue = satvalue
            return satvalue


    def GetExposureTime(self):
        '''
        This method returns the actual value of the exposure time and sets the global variable.
        '''

        ExpoTime = c_float(0.0)
        Error = self.dll.VRmUsbCamGetPropertyValueF(self.CamIndex, ExposureTimeAddress, byref(ExpoTime))
        if Error==0:
            self.ShowErrorInformation()
            return None
        else:    
            # print ExpoTime.value, "Expo time"
            self.exposureTime = ExpoTime.value
            return self.exposureTime


    def SetExposureTime(self,exposuretime=0):
        '''
        This method sets the exposure time to the input value, returns the value and sets the global variable.
        '''

        ExpoTime = c_float(exposuretime)
        Error = self.dll.VRmUsbCamSetPropertyValueF(self.CamIndex, ExposureTimeAddress, byref(ExpoTime))
        if Error==0:
            self.ShowErrorInformation()
            return None
        else:
            # if Error==1:
            #     print 'Exposure Time set to: ', ExpoTime.value, 'ms'
            self.exposureTime = ExpoTime.value
            return self.exposureTime


    def GetExposureTimeRange(self):
        '''
        Returns the adjustable range of the exposure time and sets the global variable.
        '''

        expotimeprops = ExpoTimeProps()
        Error = self.dll.VRmUsbCamGetPropertyAttribsF(self.CamIndex, ExposureTimeAddress, byref(expotimeprops))
        if Error==0:
            self.ShowErrorInformation()
            return None
        else:
            self.exposureRange = (expotimeprops.m_min,expotimeprops.m_max)
            # print self.exposureRange, "Expo Time Range"
            return self.exposureRange
        del expotimeprops


    def GetExposureTimeSteps(self):
        '''
        Returns the stepsize of the exposure time and sets the global variable.
        '''

        expotimeprops = ExpoTimeProps()
        Error = self.dll.VRmUsbCamGetPropertyAttribsF(self.CamIndex, ExposureTimeAddress, byref(expotimeprops))
        if Error==0:
            self.ShowErrorInformation()
            return None
        else:
            self.exposureSteps = expotimeprops.m_step
            # print self.exposureSteps, "Expo Time Steps"
            return self.exposureSteps
        del expotimeprops



    def GetGainValue(self):
        '''
        This method returns the actual value of the gain and sets the global variable.
        '''

        GainValue = c_int(0)
        Error = self.dll.VRmUsbCamGetPropertyValueI(self.CamIndex, GainValueAddress, byref(GainValue))
        if Error==0:
            self.ShowErrorInformation()
            return None
        else:
            # print 'Gain Value: ', GainValue.value
            self.gainValue = GainValue.value
            return self.gainValue


    def SetGainValue(self,gainvalue=0):
        '''
        This method sets the gain to the input value, returns the value and sets the global variable.
        '''

        gainvalue =int(round(gainvalue,0))
        GainValue = c_int(gainvalue)
        Error = self.dll.VRmUsbCamSetPropertyValueI(self.CamIndex, GainValueAddress, byref(GainValue))
        if Error==0:
            self.ShowErrorInformation()
            return None
        else:
            # print 'Gain Value set to: ', GainValue.value
            self.gainValue = GainValue.value
            return self.gainValue


    def GetGainRange(self):
        '''
        Returns the adjustable range of the gain and sets the global variable.
        '''

        gainprops = GainProps()
        Error = self.dll.VRmUsbCamGetPropertyAttribsI(self.CamIndex, GainValueAddress, byref(gainprops))
        if Error==0:
            self.ShowErrorInformation()
            return None
        else:
            self.gainRange = (gainprops.m_min,gainprops.m_max)
            # print self.gainRange, "Gain Range"
            return self.gainRange
        del gainprops


        
    def GetGainSteps(self):
        '''
        Returns the sepsize of the gain and sets the global variable.
        '''

        gainprops = GainProps()
        Error = self.dll.VRmUsbCamGetPropertyAttribsI(self.CamIndex, GainValueAddress, byref(gainprops))
        if Error==0:
            self.ShowErrorInformation()
            return None
        else:
            self.gainSteps = gainprops.m_step
            # print self.gainSteps, "Gain Steps"
            return self.gainSteps
        del gainprops

        




        






if __name__=="__main__":
    check = VRmagicUSBCam_API()
    check.CreateCameraList()
    check.StartCamera(camindex=0)

    size = check.GetImageSize()
    print size, "Image Size"

    # check.GetSaturationValue()

    check.GetNextImage()
    # check.GetExposureTime()
    check.SetExposureTime(30.)
    # check.GetGainValue()
    # check.SetGainValue(34)
    # check.GetExposureTimeRange()
    # check.GetExposureTimeSteps()
    # check.GetGainRange()
    # check.GetGainSteps()

    image = check.imageArray





    check.StopCamera()

    plt.figure()
    plt.imshow(image)

    # del image


    

    print check.cameraList, "Camera List"



    plt.show()







