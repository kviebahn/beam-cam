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
		self.imageSize = None



	def StartCamera(self):

		print "This method is not implemented here!"



	def StopCamera(self):

		print "This method is not implemented here!"

