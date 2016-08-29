# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 10:23:22 2016

@author: Konrad
"""

import MOTCamAPI as motcam
reload(motcam)


from Pyro.EventService.Clients import Subscriber
import Pyro.core
import socket
import os.path
import numpy as np

def getHostIP():
    """return the host ip of the computer"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        myip = s.getsockname()[0]
        s.close()
    except:
        myip = socket.gethostbyname(socket.gethostname())
        print "failed to get ip by connecting to external server. using %s"%myip
    return myip
    
# Set up ethernet connection between this script and the timing PC
Pyro.config.PYRO_HOST = getHostIP()
Pyro.config.PYRO_NS_HOSTNAME = '172.31.10.10'
Pyro.core.initClient()

class MotCamServer(Subscriber):
    def __init__(self):
        Subscriber.__init__(self)
        self.subscribe('MotCamReadOut')
        self.subscribe('MotCamSetUp')
        self.subscribe('fprefix')
        self.datapath = None
        motcam.SetUp()
        print('listening for events')

    def event(self, event):
            # ignore all timing events, they will just flood the queue
        if event.subject == 'Status' and event.msg[0][0] == 'Time':
            return
        #print(event.subject)
        #print(event.msg)

        if event.subject == 'fprefix':
            self.datapath = os.path.normpath(event.msg[0])
            print(self.datapath)

        elif event.subject == 'MotCamReadOut':
            print('read image and write it to hdf5')
            image = motcam.ReadOut()
            #motcam.QuitCamera()
            np.save(self.datapath + '.npy', image)

        elif event.subject == 'MotCamSetUp':
            motcam.Arm()
            #print('MotCam is set up')
        
        elif event.subject == 'iterationStatus':
            if event.msg[0]['status'] == 'started':
                self._folder = os.path.normpath(event.msg[0]['folder'])
            if event.msg[0]['status'] == 'stopped':
                self._iterationDone = True


if __name__ == '__main__':
    a = MotCamServer()
    a.listen()
