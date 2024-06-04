from abc import abstractmethod
import inspect

'''
Desc: Abstract class used to ensure any instrument classes being
used stick to a specific format used by the measurement class
'''

class Instrument():

    # Initialise communication 
    # Read data from cmd's file
    def __init__(self):
        pass
    
    @abstractmethod
    # Load commands from json file
    def loadcmd(self, filename):
        print("Error: ", inspect.stack()[0][3], " Un-implemented")
        pass

    @abstractmethod
    # prepares cmd ascii message to be sent to device
    def cmd(self, cmd, arg1 = None, arg2 = None):
        pass

    @abstractmethod
    # Enables / Disables EMI filter on device
    def emifilter(on = True):
        pass

    @abstractmethod
    # Set bandwidth resoltion on device
    def setrbw(self, rbw):
        pass

    @abstractmethod
    # Set bandwidth video on device
    def setrbw(self, vbw):
        pass

    @abstractmethod
    # Set span frequency
    def setspan(self, span):
        pass

    @abstractmethod
    # Set centre frequency
    def setcenter(self, freq):
        pass

    @abstractmethod
    # Define trace mode
    def settracemode(self, mode, tracenum=1):
        pass

    @abstractmethod
    # Enable / Disable consinuous mode
    def setcontinuous(self,cont = True):
        pass

    @abstractmethod
    # Establish comms connection
    def connect(self, ip = '192.168.1.70'):
        pass
        
    @abstractmethod   
    # Send command
    def send(self, cmd):
        pass        
    
    @abstractmethod
    # Receive message from device
    def recv(self, handler=None):
        pass

    @abstractmethod
    # Clear recieved data in buffer
    def cleardata(self):
        pass
        
    @abstractmethod
    # Format trace data
    def processtrace(self, data):
        pass
    
    @abstractmethod
    # ??????
    def multitrace(self, fstart, fstop, step):
        pass

    @abstractmethod 
    # Receive trace data and process as required
    def gettrace(self,tracenum=1):
        pass