import socket
import time
from io import BytesIO
from threading import Thread
import queue

# FOR DEBUGGING ONLY (Allows for breakpoints in the debugger)
#import pdb;
from message import *
from instrument_abstract import InstrumentBase

'''
Desc: Stores configuration information / methods
Para: Instrument abstract class
Return None
'''
class Instrument(InstrumentBase):

    name = 'Simulator'  

    def __init__(self):
        self.instparams = {}

    def default(self):
        return True

    def get(self, name):
        if name == 'data':
            return [(i % 600)/15 + 10 for i in range(self.instparams['sweeppoints'])]
        if name == 'sweepcountcurrent':
            return self.instparams['sweepcount']
        
        return self.instparams[name]
            
    def set(self, name, value):
        self.instparams[name] = value
        return True
                
    def connect(self, *args, **kwargs):               
        return True
    
    def disconnect(self):
        return True                          
            



