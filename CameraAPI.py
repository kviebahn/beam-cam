# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 15:48:13 2016

This script implements the base class to handle the camera. The methods defined here have to be implemented by every specific camera API.

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


import numpy as numpy


class Camera_API(object):
    '''Functions for the Camera'''


    def __init__(self):
        '''
        To be implemented!!!
        '''

        self.imageArray = None

        self.cameraList = None

        self.imageSize = None
        self.saturationValue = None
        self.exposureTime = None
        self.exposureRange = None
        self.gainValue = None
        self.gainRange = None




    def StartCamera(self):
        '''
        This method starts the camera.
        '''

        print "This method is not implemented here!"



    def StopCamera(self):
        '''
        This method stops the camera.
        '''

        print "This method is not implemented here!"


    def CreateCameraList(self):
        '''
        This method creates a camera list. All available cameras of one type are listed in an array of
        strings (their serial number).
        '''

        print "This method is not implemented here!"


    def GetNextImage(self):
        '''
        This method gets the next image and stores it in self.imageArray.
        '''

        print "This method is not implemented here!"


    def GetImageSize(self):
        '''
        This method reads out the actual image size and stores it in self.imageSize and returns the values
        as tuple (width,height).
        '''

        print "This method is not implemented here!"

        return None


    def GetSaturationValue(self):
        '''
        This method reads out the actual saturation value of the camera and stores it in self.saturationValue and returns the value.
        '''

        print "This method is not implemented here!"

        return None


    def GetExposureTime(self):
        '''
        This method returns the actual value of the exposure time and sets the global variable.
        '''

        print "This method is not implemented here!"

        return None


    def SetExposureTime(self):
        '''
        This method sets the exposure time to the input value, returns the value and sets the global variable.
        '''

        print "This method is not implemented here!"

        return None


    def GetExposureTimeRange(self):
        '''
        Returns the adjustable range of the exposure time and sets the global variable.
        '''

        print "This method is not implemented here!"

        return None


    def GetGainValue(self):
        '''
        This method returns the actual value of the gain and sets the global variable.
        '''

        print "This method is not implemented here!"

        return None


    def SetGainValue(self):
        '''
        This method sets the gain to the input value, returns the value and sets the global variable.
        '''

        print "This method is not implemented here!"

        return None


    def GetGainRange(self):
        '''
        Returns the adjustable range of the gain and sets the global variable.
        '''

        print "This method is not implemented here!"

        return None


    def InitializeCamera(self):
        '''
        This method initializes a camera using methods implemented above.
        '''

        self.StartCamera()
        imagesize = self.GetImageSize()
        saturationvalue = self.GetSaturationValue()
        exposuretime = self.GetExposureTime()
        exposuretimerange = self.GetExposureTimeRange()
        gainvalue = self.GetGainValue()
        gainrange = self.GetGainRange()

        return imagesize,saturationvalue,exposuretime,exposuretimerange,gainvalue,gainrange



    def GiveCameraList(self):
        '''
        Returns camera list.
        '''

        return self.cameraList



    def GiveImage(self):
        '''
        Returns image array.
        '''

        return self.imageArray

