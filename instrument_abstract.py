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

    @abstractmethod
    # prepares cmd ascii message to be sent to device
    def cmd(self, cmd, arg1 = None, arg2 = None):
        print("Error: ", inspect.stack()[0][3], " Un-implemented")        
        
    @abstractmethod   
    # Send command
    def send(self, cmd):
        print("Error: ", inspect.stack()[0][3], " Un-implemented")
                
    @abstractmethod
    # Receive message from device
    def recv(self, handler=None):
        print("Error: ", inspect.stack()[0][3], " Un-implemented")
        
    @abstractmethod
    # Format trace data
    def processtrace(self, data):
        print("Error: ", inspect.stack()[0][3], " Un-implemented")
  