from abc import abstractmethod
import inspect

'''
Desc: Abstract class used to ensure any instrument classes being
used stick to a specific format used by the measurement class
'''
class InstrumentBase():

    # Initialise communication 
    # Read data from cmd's file
    def __init__(self):
        pass    

    @abstractmethod
    # initialize instrument with default parameters
    def default(self):
        print("Error: ", inspect.stack()[0][3], " Un-implemented")

    @abstractmethod
    # set variable value in instrument
    def set(self, name, value):
        print("Error: ", inspect.stack()[0][3], " Un-implemented")

    @abstractmethod
    # get value from instrument
    def get(self, name):
        print("Error: ", inspect.stack()[0][3], " Un-implemented")

    @abstractmethod
    # return dict with instrument variables
    def getproperties(self):
        print("Error: ", inspect.stack()[0][3], " Un-implemented")                

    @abstractmethod
    # connect instrument
    def connect(self, address, port):
        print("Error: ", inspect.stack()[0][3], " Un-implemented")

    @abstractmethod
    # disconnect instrument
    def disconnect(self):
        print("Error: ", inspect.stack()[0][3], " Un-implemented")
