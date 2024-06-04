'''
Intrument class to be implemented.  To be called by measurement class. Similar to  DSA832.
Note: currently DSA832 (Instrument) class has measure method which takes a instance of  Measurement class as argument, 
this should be modified so that Measurement class has a measure method and a instrument as instance variable, the instrument instance should be defined by __init__.
Measurement class, should save data as json. Should include measurement configuration, description, date and time.
Define a ‘session’ object/class.
Session is a set of measurements and notes.
Measurement entries contain filename of measurement.
Note entries contain date/time and note text
'''

from DSA832_instrument import DSA832

'''
Author: Shawn Nagar
Date: 03/06/2024
'''


'''
Desc: Highest abstraction. Calls measurement class. Handles data storage along with notes by user
Para: save file name, object of instrument being used
return: NA
'''
class Session:

    def __init__ (self, savefile, dev):
        pass
    
    # Creates json file to store data in
    # Stores device configuration / settings
    # Loads correction data
    def begin (filename):
        pass

    # Called when signal to script is caught (currently ctrl + n)
    # Pauses script, user can write to json file
    def notes ():
        pass

    # Called when signal to script is caught (currently ctrl + e)
    # Terminates session
    # Clean up
    def end ():
        pass

    # Save data from previous measurement to file as json
    def savedata(self, fname):
        pass
        
    

''' 
Desc:   Class works independent of device being used. Methods request data from instrument. 
        Data storage, manipulation and graphing implemented here.
Para:   Instrument Object
Return: NA
'''
class Measurement:

    # Initialise instrument object here
    def __init__(self, filename=None, descr=''):
        pass
    
    # Create list of spectrum windows to be read
    def create(self):
        pass

    # ?????????????????????????????????????????????
    def setdatafreq(self):
        pass

    # Measure specific spectrum window
    def measuresingle(self):
        pass

    # Measure all spectrum windows
    def measureall(self):
        pass


# Loads readings from previous session. To be used for plotting / data manipulation
def load_sessiondata(filename):
    pass

# Load correction data from csv
def loadcorrection(filename):
    pass

# Adjusts read data according to corrections
def applycorrection():
    pass

# Define correction for specific freq
def getfc(freq):
    pass

# Get peak of read data
def getpeaks(self, c=10, a=0.9, nd = 0.5, ndstep = 1, th = 20):
    pass

# Plot waveform
def plot(self, ref=None, peaklist = None): 
    pass