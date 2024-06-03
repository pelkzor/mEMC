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

'''
Author: Shawn Nagar
Date: 03/06/2024
'''

'''
Open items: 
1. Where to fit the logger?
2. What is the nature of configuration? include IP addresses???
'''


''' 
Desc:   Class works independent of device being used. Methods request data from instrument. 
        Data storage, manipulation and graphing implemented here.
Para:   Instrument Object
Return: NA
'''
class Measurement:

    def __init__(self):
        pass
        return

''' 
Desc:   Class that holds device specific information / methods.
Para:   configuration dictionary??????
Return: --------------?????
'''
class Instrument:

    def __init__(self):
        pass
        return
    




