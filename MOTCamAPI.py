# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 12:41:29 2016

@author: Konrad
"""

from uEyeAPI import CameraTypeSpecific_API

cam = CameraTypeSpecific_API()

def SetUp():
    #cam.is_SetErrorReport(1)
    cam.CreateCameraList()
    cam.is_GetSensorInfo()
    cam.StartCamera()
    cam.is_SetExternalTrigger(0x0001)
    #print cam.imageArray
    cam.GetNextImage()

def ReadOut():
    #print cam.imageArray
    cam.StopCamera()
