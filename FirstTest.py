# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 10:18:13 2015

@author: Michael
"""


import GaussBeamSimulation as Sim
reload(Sim)
import MathematicalTools as MatTools
reload(MatTools)

from ctypes import *
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import pyqtgraph.ptime as ptime
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import sys

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

class Rect(Structure):
    '''Struct that holds the data for a roi of the image'''

    _fields_ = [
    ('m_left',c_int),
    ('m_top',c_int),
    ('m_width',c_int),
    ('m_height',c_int)
    ]

    def __init__(self):
        pass

        

class VRmagicUSBCam_API:
    '''Functions for the VR Magic USB Camera.'''

    def __init__(self, dllPath='vrmusbcam2.dll'):
        self.dll = cdll.LoadLibrary(dllPath)


    def ShowErrorInformation(self):

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

        Error = self.dll.VRmUsbCamUpdateDeviceKeyList()

        if Error==0:
            self.ShowErrorInformation()

        print 'KeyList'

    def GetDeviceKeyListSize(self):

        No=c_uint(0)
        Error = self.dll.VRmUsbCamGetDeviceKeyListSize(byref(No))

        print 'Number of cameras', No.value
        if Error==1:
            return No.value
        else:
            self.ShowErrorInformation()

        


    def GetDeviceKeyListEntry(self):

        self.CamIndex = 0
        self.CamIndex = c_uint(self.CamIndex)

        # Key_p = POINTER(CameraKey)
        self.dll.VRmUsbCamGetDeviceKeyListEntry.argtypes = [c_uint,POINTER(POINTER(CameraKey))]
        
        self.key = POINTER(CameraKey)()
        
        Key = self.dll.VRmUsbCamGetDeviceKeyListEntry(self.CamIndex,byref(self.key))

        if Key==0:
            self.ShowErrorInformation()
            return 0
        else:
            return 1
        

    def GetDeviceInformation(self,keytest=0):

        if keytest==0:
            print 'No valid key available!'
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


    '''
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    Functions to handle important properties
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    '''


    def GetExposureTime(self,device):

        ExpoTime = c_float(0.0)
        Error = self.dll.VRmUsbCamGetPropertyValueF(device, ExposureTimeAddress, byref(ExpoTime))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Exposure Time: ', ExpoTime.value, 'ms'

    def SetExposureTime(self,device,exposuretime):

        ExpoTime = c_float(exposuretime)
        Error = self.dll.VRmUsbCamSetPropertyValueF(device, ExposureTimeAddress, byref(ExpoTime))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Exposure Time set to: ', ExpoTime.value, 'ms'



    def GetExposureAuto(self,device):

        ExpoAuto = c_bool(False)
        Error = self.dll.VRmUsbCamGetPropertyValueB(device, ExposureAutoAddress, byref(ExpoAuto))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Exposure Auto: ', ExpoAuto.value

    def SetExposureAuto(self,device,exposureauto=False):

        ExpoAuto = c_bool(exposureauto)
        Error = self.dll.VRmUsbCamSetPropertyValueB(device, ExposureAutoAddress, byref(ExpoAuto))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Exposure Auto set to: ', ExpoAuto.value



    def GetGainValue(self,device):

        GainValue = c_int(0)
        Error = self.dll.VRmUsbCamGetPropertyValueI(device, GainValueAddress, byref(GainValue))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Gain Value: ', GainValue.value

    def SetGainValue(self,device,gainvalue=0):

        GainValue = c_int(gainvalue)
        Error = self.dll.VRmUsbCamSetPropertyValueI(device, GainValueAddress, byref(GainValue))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Gain Value set to: ', GainValue.value



    def GetGainAuto(self,device):

        GainAuto = c_bool(0)
        Error = self.dll.VRmUsbCamGetPropertyValueB(device, GainAutoAddress, byref(GainAuto))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Gain Auto: ', GainAuto.value

    def SetGainAuto(self,device,gainauto=False):

        GainAuto = c_bool(gainauto)
        Error = self.dll.VRmUsbCamSetPropertyValueB(device, GainAutoAddress, byref(GainAuto))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Gain Auto set to: ', GainAuto.value



    def GetFilterGamma(self,device):

        FilterGamma = c_float(0.)
        Error = self.dll.VRmUsbCamGetPropertyValueF(device, FilterGammaAddress, byref(FilterGamma))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Filter Gamma: ', FilterGamma.value

    def SetFilterGamma(self,device,filtergamma=1.0):

        FilterGamma = c_float(filtergamma)
        Error = self.dll.VRmUsbCamSetPropertyValueF(device, FilterGammaAddress, byref(FilterGamma))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Filter Gamma set to: ', FilterGamma.value



    def GetFilterContrast(self,device):

        FilterContrast = c_float(0.)
        Error = self.dll.VRmUsbCamGetPropertyValueF(device, FilterContrastAddress, byref(FilterContrast))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Filter Contrast: ', FilterContrast.value

    def SetFilterContrast(self,device,filtercontrast=1.0):

        FilterContrast = c_float(filtercontrast)
        Error = self.dll.VRmUsbCamSetPropertyValueF(device, FilterContrastAddress, byref(FilterContrast))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Filter Contrast set to: ', FilterContrast.value



    def GetFilterLuminance(self,device):

        FilterLuminance = c_int(0)
        Error = self.dll.VRmUsbCamGetPropertyValueI(device, FilterLuminanceAddress, byref(FilterLuminance))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Filter Luminance: ', FilterLuminance.value

    def SetFilterLuminance(self,device,filterluminance=0):

        FilterLuminance = c_int(filterluminance)
        Error = self.dll.VRmUsbCamSetPropertyValueI(device, FilterLuminanceAddress, byref(FilterLuminance))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Filter Luminance set to: ', FilterLuminance.value



    def GetFilterBlacklevel(self,device):

        FilterBlacklevel = c_int(0)
        Error = self.dll.VRmUsbCamGetPropertyValueI(device, FilterBlacklevelAddress, byref(FilterBlacklevel))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Filter Blacklevel: ', FilterBlacklevel.value

    def SetFilterBlacklevel(self,device,filterblacklevel=0):

        FilterBlacklevel = c_int(filterblacklevel)
        Error = self.dll.VRmUsbCamSetPropertyValueI(device, FilterBlacklevelAddress, byref(FilterBlacklevel))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Filter Blacklevel set to: ', FilterBlacklevel.value



    def GetSensorRoi(self,device):

        SensorRoi = Rect()
        Error = self.dll.VRmUsbCamGetPropertyValueRectI(device, SensorRoiAddress, byref(SensorRoi))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Sensor Roi: ', SensorRoi.m_left, ':', SensorRoi.m_width, 'X', SensorRoi.m_top, ':', SensorRoi.m_height

    def SetSensorRoi(self,device,sensorroi=(0,0,754,480)):
        '''"sensorroi" format: (left,top,width,height)'''

        SensorRoi = Rect()
        SensorRoi.m_left = sensorroi[0]
        SensorRoi.m_top = sensorroi[1]
        SensorRoi.m_width = sensorroi[2]
        SensorRoi.m_height = sensorroi[3]
        Error = self.dll.VRmUsbCamSetPropertyValueRectI(device, SensorRoiAddress, byref(SensorRoi))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Sensor Roi set to: ', SensorRoi.m_left, ':', SensorRoi.m_width, 'X', SensorRoi.m_top, ':', SensorRoi.m_height



    def GetPixelClock(self,device):

        PixelClock = c_float(0.)
        Error = self.dll.VRmUsbCamGetPropertyValueF(device, PixelClockAddress, byref(PixelClock))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Pixel Clock: ', PixelClock.value

    def SetPixelClock(self,device,pixelclock=13.0):

        PixelClock = c_float(pixelclock)
        Error = self.dll.VRmUsbCamSetPropertyValueF(device, PixelClockAddress, byref(PixelClock))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Pixel Clock set to: ', PixelClock.value



    def GetHBlankDuration(self,device):

        HBlankDuration = c_int(0)
        Error = self.dll.VRmUsbCamGetPropertyValueI(device, HBlankDurationAddress, byref(HBlankDuration))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'HBlank Duration: ', HBlankDuration.value

    def SetHBlankDuration(self,device,hblankduration=61):

        HBlankDuration = c_int(hblankduration)
        Error = self.dll.VRmUsbCamSetPropertyValueI(device, HBlankDurationAddress, byref(HBlankDuration))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'HBlank Duration set to: ', HBlankDuration.value



    def GetVBlankDuration(self,device):

        VBlankDuration = c_int(0)
        Error = self.dll.VRmUsbCamGetPropertyValueI(device, VBlankDurationAddress, byref(VBlankDuration))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'VBlank Duration: ', VBlankDuration.value

    def SetVBlankDuration(self,device,vblankduration=5):

        VBlankDuration = c_int(vblankduration)
        Error = self.dll.VRmUsbCamSetPropertyValueI(device, VBlankDurationAddress, byref(VBlankDuration))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'VBlank Duration set to: ', VBlankDuration.value



    def GetVRef(self,device):

        VRef = c_int(0)
        Error = self.dll.VRmUsbCamGetPropertyValueI(device, VRefAddress, byref(VRef))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'VRef: ', VRef.value

    def SetVRef(self,device,vref=0):

        VRef = c_int(vref)
        Error = self.dll.VRmUsbCamSetPropertyValueI(device, VRefAddress, byref(VRef))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'VRef set to: ', VRef.value



    def GetBlacklevelAuto(self,device):

        BlacklevelAuto = c_bool(0)
        Error = self.dll.VRmUsbCamGetPropertyValueB(device, BlacklevelAutoAddress, byref(BlacklevelAuto))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Blacklevel Auto: ', BlacklevelAuto.value

    def SetBlacklevelAuto(self,device,blacklevelauto=False):

        BlacklevelAuto = c_bool(blacklevelauto)
        Error = self.dll.VRmUsbCamSetPropertyValueB(device, BlacklevelAutoAddress, byref(BlacklevelAuto))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Blacklevel Auto set to: ', BlacklevelAuto.value



    def GetBlacklevelAdjust(self,device):

        BlacklevelAdjust = c_int(0)
        Error = self.dll.VRmUsbCamGetPropertyValueI(device, BlacklevelAdjustAddress, byref(BlacklevelAdjust))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Blacklevel Adjust: ', BlacklevelAdjust.value

    def SetBlacklevelAdjust(self,device,blackleveladjust=0):

        BlacklevelAdjust = c_int(blackleveladjust)
        Error = self.dll.VRmUsbCamSetPropertyValueI(device, BlacklevelAdjustAddress, byref(BlacklevelAdjust))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Blacklevel Adjust set to: ', BlacklevelAdjust.value



    def GetFlipHorizontal(self,device):

        FlipHorizontal = c_bool(0)
        Error = self.dll.VRmUsbCamGetPropertyValueB(device, FlipHorizontalAddress, byref(FlipHorizontal))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Flip Horizontal: ', FlipHorizontal.value

    def SetFlipHorizontal(self,device,fliphorizontal=False):

        FlipHorizontal = c_bool(fliphorizontal)
        Error = self.dll.VRmUsbCamSetPropertyValueB(device, FlipHorizontalAddress, byref(FlipHorizontal))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Flip Horizontal set to: ', FlipHorizontal.value



    def GetFlipVertical(self,device):

        FlipVertical = c_bool(0)
        Error = self.dll.VRmUsbCamGetPropertyValueB(device, FlipVerticalAddress, byref(FlipVertical))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Flip Vertical: ', FlipVertical.value

    def SetFlipVertical(self,device,flipvertical=False):

        FlipVertical = c_bool(flipvertical)
        Error = self.dll.VRmUsbCamSetPropertyValueB(device, FlipVerticalAddress, byref(FlipVertical))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Flip Vertical set to: ', FlipVertical.value


    '''------------------------------------------------------------------------'''

    def GetSourceFormat(self,device):

        '''Working, but not understood!'''

        SourceFormat = c_int(0)
        Error = self.dll.VRmUsbCamGetPropertyAttribsE(device, SourceFormatAddress, byref(SourceFormat))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Source Format: ', SourceFormat

    def SetSourceFormat(self,device,sourceformat):

        '''Working, but not understood!'''

        SourceFormat = c_int(sourceformat)
        Error = self.dll.VRmUsbCamSetPropertyAttribsE(device, SourceFormatAddress, byref(SourceFormat))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Source Format set to: ', SourceFormat

    '''------------------------------------------------------------------------'''


    '''
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    Functions to handle images 
    ---------------------------------------------------------------------------
    ---------------------------------------------------------------------------
    '''



    def TakePicture(self,keytest=0):

        '''
        Not updated; does not work!!
        '''

        if keytest==0:
            print 'No valid key available!'
        elif self.key.contents.m_busy!=0:
            print 'Camera is busy!'
        else:
            Error = self.dll.VRmUsbCamOpenDevice(self.key,byref(self.CamIndex))
            if Error==0:
                self.ShowErrorInformation()
            else:
                print 'Device opend successfully'

                self.GetExposureTime(self.CamIndex)

                format = ImageFormat()
                format.m_width = 754
                format.m_height = 482
                format.m_color_format = 4
                format.m_image_modifier = 0

                inf = POINTER(c_char)()

                Error = self.dll.VRmUsbCamGetStringFromColorFormat(format.m_color_format,byref(inf))

                color = []
                i = 0
                
                while inf[i] != '\0':
                    color.append(inf[i])
                    i += 1
                color = ''.join(color)
                print 'Color format: ', color

                pixeldepth = c_uint(0)


                Error = self.dll.VRmUsbCamGetPixelDepthFromColorFormat(format.m_color_format,byref(pixeldepth))

                print 'Pixel Depth: ', pixeldepth.value

                self.dll.VRmUsbCamNewImage.argtypes = [POINTER(POINTER(Image)),ImageFormat]
        
                self.image_p = POINTER(Image)()

                Error = self.dll.VRmUsbCamStart(self.CamIndex)

                Error = self.dll.VRmUsbCamNewImage(byref(self.image_p),format)

                Error = self.dll.VRmUsbCamStop(self.CamIndex)

                print 'Pitch: ', self.image_p.contents.m_pitch

                if Error==0:
                    self.ShowErrorInformation()

                


                if Error==1:
                    print'Image taken!'

                    ImageList = list(self.image_p.contents.mp_buffer[0:(format.m_height)*int(self.image_p.contents.m_pitch)])
                    # print ImageList[0:10]
                    # print len(ImageList)
                    ImageList = [ord(i) for i in ImageList]
                    print len(ImageList)

                    self.ImageArray = np.array(ImageList)
                    self.ImageArray = np.reshape(self.ImageArray,(format.m_height,int(self.image_p.contents.m_pitch)))
                    self.ImageArray = self.ImageArray[:,:format.m_width]


                    # for j in range(format.m_height):
                    #   for i in range(format.m_width):
                    #       self.ImageArray[j,i] = ord(self.image_p.contents.mp_buffer[j*int(pixeldepth.value)+i*int(self.image_p.contents.m_pitch)])

                            # print ord(ImageList[i*int(pixeldepth.value)+j*int(self.image_p.contents.m_pitch)])

                    plt.figure()
                    plt.imshow(self.ImageArray, cmap = cm.Greys_r)




                    name_p = c_char_p('Test.png')
                    Error = self.dll.VRmUsbCamSavePNG(name_p,self.image_p,c_int(0))
                    if Error==0:
                        self.ShowErrorInformation()
                    if Error==1:
                        print'Image saved!'

                Error = self.dll.VRmUsbCamFreeImage(byref(self.image_p))

                if Error==0:
                    self.ShowErrorInformation()



                




        Error = self.dll.VRmUsbCamFreeDeviceKey(byref(self.key))
        if Error==0:
            self.ShowErrorInformation()

        Error = self.dll.VRmUsbCamCloseDevice(self.CamIndex)
        if Error==0:
            self.ShowErrorInformation()



    def UseSourceFormat(self):
        Error = self.dll.VRmUsbCamGetSourceFormatEx(self.CamIndex,c_uint(1),byref(self.format))
        if Error==0:
            self.ShowErrorInformation()


    def GetSourceFormatInformation(self):
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





    def GrabNextImage(self):

        self.dll.VRmUsbCamLockNextImageEx2.argtypes = [c_uint,c_uint,POINTER(POINTER(Image)),POINTER(c_uint),c_int]
                
        source_image_p = POINTER(Image)()

        framesdropped = c_uint(0)

        timeout = 5000

        Error = self.dll.VRmUsbCamLockNextImageEx2(self.CamIndex,c_uint(1),byref(source_image_p),byref(framesdropped),c_int(timeout))
                
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            # print'Image taken!'

            ImageList = list(source_image_p.contents.mp_buffer[0:(self.format.m_height)*int(source_image_p.contents.m_pitch)])
            ImageList = [ord(i) for i in ImageList]
            # print len(ImageList)

            self.ImageArray = np.array(ImageList)
            self.ImageArray = np.reshape(self.ImageArray,(self.format.m_height,int(source_image_p.contents.m_pitch)))
            self.ImageArray = self.ImageArray[:,:self.format.m_width]


        Error = self.dll.VRmUsbCamUnlockNextImage(self.CamIndex,byref(source_image_p))
        # print 'Unlock Image'
        if Error==0:
            self.ShowErrorInformation()





    def TakePictureGrabbing(self,keytest=0):
        if keytest==0:
            print 'No valid key available!'
        elif self.key.contents.m_busy!=0:
            print 'Camera is busy!'
        else:
            Error = self.dll.VRmUsbCamOpenDevice(self.key,byref(self.CamIndex))
            if Error==0:
                self.ShowErrorInformation()
            else:
                print 'Device opened successfully'

                self.format = ImageFormat()
                self.format.m_width = 754
                self.format.m_height = 480
                self.format.m_color_format = 4
                self.format.m_image_modifier = 0

                inf = POINTER(c_char)()

                Error = self.dll.VRmUsbCamGetStringFromColorFormat(self.format.m_color_format,byref(inf))

                color = []
                i = 0
                
                while inf[i] != '\0':
                    color.append(inf[i])
                    i += 1
                color = ''.join(color)
                print 'Color format: ', color

                pixeldepth = c_uint(0)


                self.GetExposureTime(self.CamIndex)
                self.SetExposureTime(self.CamIndex,0.75)
                self.GetExposureTime(self.CamIndex)

                self.GetExposureAuto(self.CamIndex)
                self.SetExposureAuto(self.CamIndex,False)
                self.GetExposureAuto(self.CamIndex)

                self.GetGainValue(self.CamIndex)
                self.SetGainValue(self.CamIndex,16)

                self.GetGainAuto(self.CamIndex)
                self.SetGainAuto(self.CamIndex,False)

                self.GetFilterGamma(self.CamIndex)
                self.SetFilterGamma(self.CamIndex)

                self.GetFilterContrast(self.CamIndex)
                self.SetFilterContrast(self.CamIndex)

                self.GetFilterLuminance(self.CamIndex)
                self.SetFilterLuminance(self.CamIndex)

                self.GetFilterBlacklevel(self.CamIndex)
                self.SetFilterBlacklevel(self.CamIndex)

                self.GetSensorRoi(self.CamIndex)
                self.SetSensorRoi(self.CamIndex)

                self.GetFlipVertical(self.CamIndex)
                self.SetFlipVertical(self.CamIndex)

                # self.GetGainDoubling(self.CamIndex)


                Error = self.dll.VRmUsbCamGetPixelDepthFromColorFormat(self.format.m_color_format,byref(pixeldepth))

                print 'Pixel Depth: ', pixeldepth.value

                self.GetSourceFormatInformation()
                self.UseSourceFormat()


                Error = self.dll.VRmUsbCamStart(self.CamIndex)
                print 'Start Cam'

                self.GrabNextImage()


                Error = self.dll.VRmUsbCamStop(self.CamIndex)
                if Error==0:
                    self.ShowErrorInformation()


                plt.figure()
                plt.imshow(self.ImageArray, cmap = cm.Greys_r)
                plt.colorbar()

                    # name_p = c_char_p('Test.png')
                    # Error = self.dll.VRmUsbCamSavePNG(name_p,source_image_p,c_int(0))
                    # if Error==0:
                    #   self.ShowErrorInformation()
                    # if Error==1:
                    #   print'Image saved!'

                
                if Error==0:
                    self.ShowErrorInformation()

        Error = self.dll.VRmUsbCamFreeDeviceKey(byref(self.key))
        if Error==0:
            self.ShowErrorInformation()

        Error = self.dll.VRmUsbCamCloseDevice(self.CamIndex)
        if Error==0:
            self.ShowErrorInformation()



    def RealTimeView(self,keytest=0):

        if keytest==0:
            print 'No valid key available!'
        elif self.key.contents.m_busy!=0:
            print 'Camera is busy!'
        else:
            Error = self.dll.VRmUsbCamOpenDevice(self.key,byref(self.CamIndex))
            if Error==0:
                self.ShowErrorInformation()
            else:
                print 'Device opened successfully'

                self.GetExposureTime(self.CamIndex)
                self.SetExposureTime(self.CamIndex,0.75)
                self.GetExposureTime(self.CamIndex)

                self.GetExposureAuto(self.CamIndex)
                self.SetExposureAuto(self.CamIndex,False)
                self.GetExposureAuto(self.CamIndex)

                self.format = ImageFormat()
                self.GetSourceFormatInformation()
                self.UseSourceFormat()


                Error = self.dll.VRmUsbCamStart(self.CamIndex)
                print 'Started Cam'


                app = QtGui.QApplication([])

                # ## Create window with GraphicsView widget
                # win = pg.GraphicsLayoutWidget()
                # win.show()  ## show widget alone in its own window
                # win.setWindowTitle('pyqtgraph example: ImageItem')
                # view = win.addViewBox()

                # ## lock the aspect ratio so pixels are always square
                # view.setAspectLocked(True)

                # ## Create image item
                # img = pg.ImageItem(border='w')
                # view.addItem(img)

                # ## Set initial view bounds
                # view.setRange(QtCore.QRectF(0, 0, 754, 480))



                # self.GrabNextImage()
                
                # self.ImageArray = self.ImageArray.flatten
                # i = 0

                # updateTime = ptime.time()
                # fps = 0

                # def updateData():
                #   global img, i, updateTime, fps

                #   ## Display the data
                #   img.setImage(self.ImageArray[i])
                #   i = (i+1) % self.ImageArray.shape[0]

                #   QtCore.QTimer.singleShot(1, updateData)
                #   now = ptime.time()
                #   fps2 = 1.0 / (now-updateTime)
                #   updateTime = now
                #   fps = fps * 0.9 + fps2 * 0.1
    
                #   #print "%0.1f fps" % fps
    

                # updateData()

    #           if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
                #   # QtGui.QApplication.instance().exec_()
                #   pg.exit()
                #   Error = self.dll.VRmUsbCamStop(self.CamIndex)
                #   if Error==0:
                #       self.ShowErrorInformation()


                
                win = QtGui.QWidget()


                


                # Image widget
                imagewidget = pg.GraphicsLayoutWidget()
                view = imagewidget.addViewBox()
                view.setAspectLocked(True)
                self.img = pg.ImageItem(border='k')
                view.addItem(self.img)
                view.setRange(QtCore.QRectF(0, 0, 754, 480))

                # Custom ROI for selecting an image region
                roi = pg.ROI([0, 200], [100, 200],pen=(0,9))
                roi.addScaleHandle([0.5, 1], [0.5, 0.5])
                roi.addScaleHandle([0, 0.5], [0.5, 0.5])
                view.addItem(roi)
                roi.setZValue(10)  # make sure ROI is drawn above

                p3 = imagewidget.addPlot(colspan=1)
                # p3.rotate(90)
                p3.setMaximumWidth(200)

                # Another plot area for displaying ROI data
                imagewidget.nextRow()
                p2 = imagewidget.addPlot(colspan=1)
                p2.setMaximumHeight(200)
                
                # win.show()


                layout = QtGui.QGridLayout()
                win.setLayout(layout)
                win.setWindowTitle('VRmagic USB Cam Live View')
                layout.addWidget(imagewidget, 1, 2, 3, 1)
                win.resize(1100, 870)
                win.show()


                
                def updateview():
                    
                    self.GrabNextImage()
                    self.img.setImage(self.ImageArray.T)

                    updateRoi()

                def updateRoi():

                    selected = roi.getArrayRegion(self.ImageArray.T, self.img)
                    p2.plot(selected.sum(axis=1), clear=True)
                    p3.plot(selected.sum(axis=0), clear=True).rotate(-90)


                roi.sigRegionChanged.connect(updateRoi)

                viewtimer = QtCore.QTimer()
                viewtimer.timeout.connect(updateview)
                viewtimer.start(0)

                app.exec_()
                viewtimer.stop()
                Error = self.dll.VRmUsbCamStop(self.CamIndex)
                if Error==0:
                    self.ShowErrorInformation()




        Error = self.dll.VRmUsbCamFreeDeviceKey(byref(self.key))
        if Error==0:
            self.ShowErrorInformation()

        Error = self.dll.VRmUsbCamCloseDevice(self.CamIndex)
        if Error==0:
            self.ShowErrorInformation()



    def RealTimeViewTest(self):

        simulation = Sim.GaussBeamSimulation()
        simulation.CreateImages()

        app = QtGui.QApplication([])

        win = QtGui.QWidget()

        # Image widget
        imagewidget = pg.GraphicsLayoutWidget()
        view = imagewidget.addViewBox()
        view.setAspectLocked(True)
        self.img = pg.ImageItem(border='k')
        view.addItem(self.img)
        view.setRange(QtCore.QRectF(0, 0, 754, 480))

        # Custom ROI for selecting an image region
        roi = pg.ROI([310, 210], [200, 200],pen=(0,9))
        roi.addScaleHandle([0.5, 1], [0.5, 0.5])
        roi.addScaleHandle([0, 0.5], [0.5, 0.5])
        view.addItem(roi)
        roi.setZValue(10)  # make sure ROI is drawn above


        peak = pg.GraphItem()
        symbol = ['x']
        view.addItem(peak)
        roi.setZValue(20)

        p3 = imagewidget.addPlot(colspan=1)
        # p3.rotate(90)
        p3.setMaximumWidth(200)

        # Another plot area for displaying ROI data
        imagewidget.nextRow()
        p2 = imagewidget.addPlot(colspan=1)
        p2.setMaximumHeight(200)

        #cross hair
        vLine = pg.InfiniteLine(angle=90, movable=False)
        hLine = pg.InfiniteLine(angle=0, movable=False)
        view.addItem(vLine, ignoreBounds=True)
        view.addItem(hLine, ignoreBounds=True)

                
        # win.show()


        layout = QtGui.QGridLayout()
        win.setLayout(layout)
        win.setWindowTitle('VRmagic USB Cam Live View')
        layout.addWidget(imagewidget, 1, 2, 3, 1)
        win.resize(1100, 870)
        win.show()


                
        def updateview():
            # simulation.NewImage()
            # simulation.AddWhiteNoise()
            # simulation.AddRandomGauss()
            # simulation.SimulateTotalImage()
            simulation.ChooseImage()

            self.ImageArray = simulation.image
            self.img.setImage(self.ImageArray.T)

            updateRoi()

        def updateRoi():

            selected = roi.getArrayRegion(self.ImageArray.T, self.img)
            p2.plot(selected.sum(axis=1), clear=True)

            datahor = selected.sum(axis=1)
            FittedParamsHor = MatTools.FitGaussian(datahor)[0]
            xhor = np.arange(datahor.size)
            p2.plot(MatTools.gaussian(xhor,*FittedParamsHor), pen=(0,255,0))


            p3.plot(selected.sum(axis=0), clear=True).rotate(-90)

            datavert = selected.sum(axis=0)
            FittedParamsVert = MatTools.FitGaussian(datavert)[0]
            xvert = np.arange(datavert.size)
            p3.plot(MatTools.gaussian(xvert,*FittedParamsVert), pen=(0,255,0)).rotate(-90)

            hLine.setPos(FittedParamsVert[2]+roi.pos()[1])
            vLine.setPos(FittedParamsHor[2]+roi.pos()[0])


            
            pos = np.array([[(FittedParamsHor[2]+roi.pos()[0]),(FittedParamsVert[2]+roi.pos()[1])]])
            peak.setData(pos=pos,symbol=symbol,size=25, symbolPen='g', symbolBrush='g')
            
            # print roi.pos, 'ROI Position'



            # print 'ROI Sum: ', selected.sum(axis=1)


        roi.sigRegionChanged.connect(updateRoi)

        viewtimer = QtCore.QTimer()
        viewtimer.timeout.connect(updateview)
        viewtimer.start(0)

        app.exec_()
        viewtimer.stop()
                



        

if __name__=="__main__":
    check = VRmagicUSBCam_API()
    check.GetDeviceKeyList()
    check.GetDeviceKeyListSize()
    keycheck = check.GetDeviceKeyListEntry()
    check.GetDeviceInformation(keycheck)
    # check.TakePictureGrabbing(keycheck)
    # check.RealTimeView(keycheck)
    check.RealTimeViewTest()
    plt.show()
