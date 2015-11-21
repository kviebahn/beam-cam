# -*- coding: utf-8 -*-
"""
Created on Mon Aug 04 15:59:45 2015

@author: Michael

This Script provides a Python interface to VR Magic USB Cameras. It only contains the most relevant methods.
If necessary, other methods can be implemented by using the the header file "vrmusbcam2.h".
"""

from ctypes import *
import numpy as np
import sys

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
        self.keytest = 0
        # self.CamIndex = c_uint(0)


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



    '''Exposure time'''
    def GetExposureTime(self,device):

        ExpoTime = c_float(0.0)
        Error = self.dll.VRmUsbCamGetPropertyValueF(device, ExposureTimeAddress, byref(ExpoTime))
        if Error==0:
            self.ShowErrorInformation()
        # if Error==1:
        #     print 'Exposure Time: ', ExpoTime.value, 'ms'
        return ExpoTime.value

    def SetExposureTime(self,device,exposuretime):

        ExpoTime = c_float(exposuretime)
        Error = self.dll.VRmUsbCamSetPropertyValueF(device, ExposureTimeAddress, byref(ExpoTime))
        if Error==0:
            self.ShowErrorInformation()
        # if Error==1:
        #     print 'Exposure Time set to: ', ExpoTime.value, 'ms'


    '''Automatic adjustment of exposure time'''
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


    '''Gain'''
    def GetGainValue(self,device):

        GainValue = c_int(0)
        Error = self.dll.VRmUsbCamGetPropertyValueI(device, GainValueAddress, byref(GainValue))
        if Error==0:
            self.ShowErrorInformation()
        # if Error==1:
        #     print 'Gain Value: ', GainValue.value
        return GainValue.value

    def SetGainValue(self,device,gainvalue=0):

        GainValue = c_int(gainvalue)
        Error = self.dll.VRmUsbCamSetPropertyValueI(device, GainValueAddress, byref(GainValue))
        if Error==0:
            self.ShowErrorInformation()
        # if Error==1:
        #     print 'Gain Value set to: ', GainValue.value



    '''Automatic adjustment of gain'''
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


    '''Gamma filter'''
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


    '''Filter contrast'''
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


    '''Filter luminance'''
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


    '''Filter blacklevel'''
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


    '''Sensor ROI'''
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


    '''Pixel clock'''
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


    '''HBlank duration'''
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


    '''VBlank duration'''
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


    '''VRef'''
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


    '''Automatic adjustment of blacklevel'''
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


    '''Blacklevel adjust'''
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


    '''Flip horizontal'''
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


    '''Flip vertical'''
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


    '''Switch on/off status LED'''
    def GetStatusLED(self,device):

        StatusLED = c_bool(0)
        Error = self.dll.VRmUsbCamGetPropertyValueB(device, StatusLEDAddress, byref(StatusLED))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Status LED on: ', StatusLED.value

    def SetStatusLED(self,device,statusled=False):

        StatusLED = c_bool(statusled)
        Error = self.dll.VRmUsbCamSetPropertyValueB(device, StatusLEDAddress, byref(StatusLED))
        if Error==0:
            self.ShowErrorInformation()
        if Error==1:
            print 'Status LED set to: ', StatusLED.value


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





    def GrabNextImage(self):
        '''
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




    def InitializeCam(self):
        '''The available cameras are intitialized.'''

        self.GetDeviceKeyList()
        self.GetDeviceKeyListEntry()




    def StartCam(self):
        '''One camera is started.'''

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

                self.format = ImageFormat()
                self.GetSourceFormatInformation()
                self.UseSourceFormat()


                Error = self.dll.VRmUsbCamStart(self.CamIndex)
                print 'Started Cam'

    def StopCam(self):
        '''One camera is stopped.'''

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


if __name__=="__main__":
    check = VRmagicUSBCam_API()
    check.InitializeCam()
    check.GetDeviceInformation()
    check.StartCam()
    check.StopCam()

