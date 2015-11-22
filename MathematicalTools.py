# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 12:41:23 2015

@author: Michael

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

import numpy as np
import random
from matplotlib import pylab as plt
import scipy as sp
from scipy.optimize import leastsq

def gaussian(x, *p):
    '''returns gaussfunction'''
    A,sigx,x0,off = p
    A = A*(sigx*np.sqrt(np.pi/2.))
    g = (A/(sigx*np.sqrt(np.pi/2.)))*np.exp(-2.*((x-x0)/sigx)**2)+off

    return g

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






def rotmatrix(alpha):
    '''returns a 2d rotation matrix'''
    return np.array([[np.cos(alpha), -np.sin(alpha)], [np.sin(alpha),  np.cos(alpha)]])


def gaussian2(xy, *p):
    '''returns gaussfunction for arbitrarily positioned and rotated 2d gauss'''
    A, sx, x0, y0, sy,alpha,off = p
    # M = np.array([[Bx,Bxy],[Bxy,By]])
    R = rotmatrix(alpha)
    M = np.dot(R,np.dot(np.array([[1./sx**2,0],[0,1./sy**2]]),R.T))
    r = np.array([xy[:,0]-x0,xy[:,1]-y0])
    g = A*np.exp(-0.5*np.sum(np.dot(M,r)*r,axis=0)) + off
    # print g
    return g



def FitGaussian(data):
    '''fits gaussian to data'''

    def split(arr, size):
        '''
        EXPERIMENTAL!
        reduce size of fit array by taking mean over a certain number of cells
        '''
        length = arr.size
        cutoff = length % size
        arrs = arr[cutoff:]
        arrs = arrs.reshape((int((length-cutoff)/size),size))
        arrs = np.mean(arrs, axis=1)
        return arrs, cutoff

    # x = np.arange(data.size)
    usepervimpro = True # Should the 'split' method be used to improve performance?
    meansize = 5 # if usepervimpro = True: how many values are taken together to calculate the mean.
    critvalue = 200 # value from which on the 'split' method is used.

    if usepervimpro:
        if data.size > critvalue:
            data, cutoff = split(data,meansize)
            corr = (meansize-1)/2.
            x = np.arange(data.size)*meansize + corr + cutoff
        else:
            x = np.arange(data.size)
    else:
        x = np.arange(data.size)

    # print data

    def errf(params):
        '''
        The errorfunction to be minimized
        '''
        # x = np.arange(data.size)
        return (data-gaussian(x,*params)) #take only every 10th value

    x0iniarg = np.argmax(data)
    Aini = data[x0iniarg]
    x0ini = x[x0iniarg]
    sigxini = 10.
    offini = 1000.

    p0 = [Aini,sigxini,x0ini,offini]
    # args = [A,sigx,x0,off]

    fitres = leastsq(errf,p0)

    # print fitres, 'FitRes'

    return fitres

    




