from instrument_abstract import Instrument

'''
Desc: Stores configuration information / methods
Para: Instrument abstract class
Return None
'''

class DSA832(Instrument):

    # Initialise communication 
    # Read data from cmd's file
    def __init__(self):
        pass
    
    # Load commands from json file
    def loadcmd(self, filename):
        pass

    # prepares cmd ascii message to be sent to device
    def cmd(self, cmd, arg1 = None, arg2 = None):
        pass

    # Enables / Disables EMI filter on device
    def emifilter(on = True):
        pass

    # Set bandwidth resoltion on device
    def setrbw(self, rbw):
        pass

    # Set bandwidth video on device
    def setrbw(self, vbw):
        pass

    # Set span frequency
    def setspan(self, span):
        pass

    # Set centre frequency
    def setcenter(self, freq):
        pass

    # Define trace mode
    def settracemode(self, mode, tracenum=1):
        pass

    # Enable / Disable consinuous mode
    def setcontinuous(self,cont = True):
        pass

    # Establish comms connection
    def connect(self, ip = '192.168.1.70'):
        pass
        
    # Send command
    def send(self, cmd):
        pass        
    
    # Receive message from device
    def recv(self, handler=None):
        pass

    # Clear recieved data in buffer
    def cleardata(self):
        pass
        
    # Format trace data
    def processtrace(self, data):
        pass
    
    # ??????
    def multitrace(self, fstart, fstop, step):
        pass
        
    # Receive trace data and process as required
    def gettrace(self,tracenum=1):
        pass