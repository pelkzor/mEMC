import numpy as np
from matplotlib import pyplot as plt
import time
from datetime import datetime
import json
import os
import glob


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

    def __init__ (self, dev, savefilepath = "", desc = ""):
        self.savefilepath = savefilepath
        self.session_desc = desc        # description of session to be added to file
        self.meas = Measurement(dev)    # Class object of measurement to be used
        self.fclist = loadcorrection('tbaf1m.csv')      # Load correction info
        self.count = 0                  # Tracks number of measurements taken 
        self.measure_dict = {}          # Current measurement dictionary

        # Parent dictionary. Contains filename, data of creation, description
        # and list of measurements
        self.parent_dict = {}

        # Append date and time to given folder and file name
        curr_time = datetime.now()
        start_time = curr_time.strftime("%H%M%S")
        date = curr_time.strftime("%Y%m%d")
                       
        # Append time and date to save file path
        # If no path given, save to default folder in current folder
        if self.savefilepath == "":

            # Create a default save folder
            save_folder = "Measurements"
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)
            
            savefilename = f'Record_{date}_{start_time}'
            # Append directory to file name
            self.savefilepath = f'{save_folder}/{savefilename}'

        #else:
            #self.savefilpath = f'{self.savefilepath}_{date}_{start_time}'

        self.parent_dict["Date Created"] = date
        self.parent_dict["File Name"] = os.path.basename(self.savefilepath)
        self.parent_dict["Description"] = self.session_desc


    # Iterate 1 measurement
    def measure(self):

        # Clear current measure dictionary
        self.measure_dict = {}

        curr_time = datetime.now()
        logtime = curr_time.strftime("%H%M%S")
        # Initalise dictionary for current measurement 
        
        self.measure_dict["TimeStamp"] = logtime
        self.measure_dict["Configuration"] = self.meas.cfg

        # Clear buffers
        data = []      
        datax = []
        '''
        # Read data
        data, datax = self.meas.measure()
        # Apply corrections
        data = applycorrection(data, datax, self.fclist)
        '''
    
        # TESTING. Loads data from a previous json recording. Simulating reading
        # Data from actual instrument as above
        diction = load_sessiondata("session_test.json")["measure0"]
        data = diction["Sig_Level"]
        datax = diction['Frequency']
        data = applycorrection(data, datax, self.fclist)
        
        # Save data to dictionary
        self.measure_dict["Sig_Level"] = data
        self.measure_dict["Frequency"] = datax

        # Generate plot
        #plot(measure_dict)
        return self.measure_dict


    # save dictionary to file
    def savemeasure(self, meas_name = '', note = ''):

        self.measure_dict["Name"] = meas_name
        self.measure_dict["Note"] = note
        
        # Assign new measurement to parent dictionary
        if self.measure_dict['Name'] == '':
            self.parent_dict["measure" + str(self.count)] = self.measure_dict
        else:
            self.parent_dict["measure" + str(self.count) + '_' + self.measure_dict['Name']] = self.measure_dict

        # Save updated parent dictionary to file
        # Note: Cant save specific measurement each time as the json dump cannot append to file,
        # instead it overwrites it. hence I append measurement to a dctionary containing all measurements
        # and then save
        file = f'{self.savefilepath}'
        with open(file, mode = "w") as f:
            json.dump(self.parent_dict, f, indent=4)

        # Update measurement counter
        self.count += 1


'''
Desc:   Class contains different configurations for reading data from device
'''
class Config:
    # Class variable with the number of default configurations
    CONFIGS_AVAIL = 7

    def __init__(self):
        pass

    @classmethod
    # return correct configuration based on number provided
    def get_config(cls, opt: int):
        # Dictionary associating options provided with configuration methods
        configs = {0: Config.cfg_default,
                1: Config.cfg_condqp,
                2: Config.cfg_cond1,
                3: Config.cfg_cond2,
                4: Config.cfg_rad1,
                5: Config.cfg_radcoarse,
                6: Config.cfg_mt100}
        
        # Use default config if an invalid option was provided
        if opt < 0 or opt >= len(configs):
            print("Invalid Option: Default config applied")
            opt = 1

        # return correct method
        config_func = configs.get(opt)

        # Return configuration dictionary
        return config_func()


    @classmethod
    def cfg_default(cls):
        return {'Name': 'cfg_default', 'continuous':0, 'fstart':30000000, 
                'fstop':1000000000, 'rbw':120000, 'vbw':1000000, 
                'amp':1, 'atten':0, 'detector':'POSitive', 'xscale':'LIN',
                'emifilter':1, 'sweeppoints':601, 'sweepcount':20, 
                'tracemode':'MAXHold', 'unit':'dBuV', 'offset':0}

    @classmethod
    def cfg_condqp(cls):   # conducted emf by cable - quasi filter
        return {'Name': 'cfg_condqp', 'continuous':0, 'xscale':'LIN', 'fstart':150000, 
                'fstop':30000000, 'sweeptime': 15, 'rbw':9000, 'vbw':9000, 
                'amp':0, 'atten':0, 'detector':'QPEak', 'emifilter':1, 
                'sweeppoints':601, 'sweepcount':1, 'tracemode':'MAXHold', 
                'unit':'dBuV', 'offset':10}

    @classmethod
    def cfg_cond2(cls):    # generic conducted emf
        return {'Name': 'cfg_cond2', 'continuous':0, 'xscale':'LIN', 'fstart':150000, 
                'sweeptime': 0.2, 'fstop':30000000, 'rbw':9000, 
                'vbw':9000, 'amp':0, 'atten':0, 'detector':'POSitive', 
                'emifilter':1, 'sweeppoints':601, 'sweepcount':1, 
                'tracemode':'MAXHold', 'unit':'dBuV', 'offset':10}        
        
    @classmethod
    def cfg_cond1(cls):    # generic conducted emf
        return {'Name': 'cfg_cond1', 'continuous':0, 'xscale':'LIN', 'fstart':150000, 
                'sweeptime': 0.2, 'fstop':30000000, 'rbw':9000, 
                'vbw':9000, 'amp':0, 'atten':0, 'detector':'POSitive', 
                'emifilter':1, 'sweeppoints':601, 'sweepcount':20, 
                'tracemode':'MAXHold', 'unit':'dBuV', 'offset':10}

    @classmethod
    def cfg_rad1(cls):     # radiation emmission
        return {'Name': 'cfg_rad1', 'continuous':0, 'xscale':'LIN', 'offset': 0, 'fstart':30000000, 
                'fstop':1000000000, 'sweeptime': 0.2, 'rbw':120000, 'vbw':120000, 
                'amp':1, 'atten':0, 'detector':'POSitive', 'emifilter':1, 
                'sweeppoints':601, 'sweepcount':20, 'tracemode':'MAXHold', 
                'unit':'dBuV', 'offset':0}

    @classmethod
    def cfg_radcoarse(cls):    # radiation emmission Less resolution
        return {'Name': 'cfg_radcoarse', 'continuous':0, 'xscale':'LIN', 'offset': 0, 'fstart':30000000, 
                'fstop':1000000000, 'sweeptime': 0.2, 'rbw':1000000, 'vbw':1000000, 
                'amp':1, 'atten':0, 'detector':'POSitive', 'emifilter':1, 
                'sweeppoints':601, 'sweepcount':20, 'tracemode':'MAXHold', 
                'unit':'dBuV', 'offset':0}

    @classmethod
    def cfg_mt100(cls):        # Specifc to measurement transformer
        return {'Name': 'cfg_mt100', 'continuous':0, 'xscale':'LIN', 'offset': 0, 
                'fstart':150000, 'fstop':100000000, 'sweeptime': 0.2, 
                'rbw':9000, 'vbw':9000, 'amp':1, 'atten':0, 'detector':'POSitive', 
                'emifilter':1, 'sweeppoints':601, 'sweepcount':20, 'tracemode':'MAXHold', 
                'unit':'dBuV', 'offset':0}


''' 
Desc:   Class works independent of device being used. Methods request data from instrument. 
        Data storage, manipulation and graphing implemented here.
Para:   Instrument Object
Return: NA
'''
class Measurement:

    # Initialise instrument object here
    def __init__(self, dev):
        self.data = []      # Stores raw measured data (Y-axis)
        self.datax = []     # Stores raw measured data (X-axis)
        self.device = dev   # Class object instrument used to read sensors
        self.mlist = []     # List of spectrum windows to be read
        # Assign default configuration
        self.cfg = Config.cfg_default() #Tracks configuration used for current measurement
    
    # Create list of spectrum windows to be read
    # Note: Resolution is poort if we read the entire spectrum at once. 
    # Solution: Break the entire spectrum into smaller windows
    def create(self):
        
        span = self.cfg['fstop']-self.cfg['fstart']
        totpoints = span / self.cfg['rbw']
        nmeas = int(totpoints / self.cfg['sweeppoints'] + 0.999)
        subspan = int(span / nmeas)
        
        # Clear list of windows
        self.mlist = [] 
        
        fs = self.cfg['fstart']
        fe = fs + subspan
        # Create windows based on start / stop frequencies
        while(fs + 1000 < self.cfg['fstop']):       #Remainder bandwidth less than 1000 hz
            self.mlist.append((fs,fe))
            fs = fs + subspan                
            fe = fe + subspan

    # generate a list of X-axis values based on readings + configuration
    def setdatafreq(self):
        step = (self.cfg['fstop'] - self.cfg['fstart']) / len(self.data)
        self.datax = [ self.cfg['fstart'] + step//2 + n * step for n in range(len(self.data))]

    # Measure all spectrum windows and return data
    def measure(self):
        # Clear data buffer
        self.data = []
        self.create()

        for m in self.mlist:
            # Commented out setter function in DSA832 implementation. Kept in case required for future
            '''
            # Send configuration commands to device
            self.device['fstart'] = m[0]       # Start recording from current window start frequency
            self.device['fstop'] = m[1]    # End recording at next window start frequency
            self.device['tracemode'] = self.cfg['tracemode']            
            # Request sweep time
            sweeptime = self.device.cmd('sweeptime','?')            
            # initiate request of data
            self.device['initiate'] = 1
            '''

            # Send configuration commands to device
            self.device.cmd('fstart',m[0])
            self.device.cmd('fstop', m[1])
            self.device.cmd('tracemode', self.cfg['tracemode'])
            # Request sweep time
            sweeptime = self.device.cmd('sweeptime','?')
            # calculate time delay
            wait_time = sweeptime * self.cfg['sweepcount'] + 1     
            # Initiate read of data
            self.device.cmd('initiate', 1)       

            print('st = ', sweeptime)
            print ('sleeping ', wait_time, 's')
            
            while(1):
                time.sleep(wait_time)
                # Device should now be sweeping through windows
                # Keep checking till the current sweep count is the max sweep count requested
                if(self.device.cmd('sweepcountcurrent','?') == self.cfg['sweepcount']):
                    break
            
            # Trace should be completed by now. Request entire trace
            self.data.extend(self.device.cmd('tracedata',1))
        
        self.setdatafreq()

        return self.data, self.datax

    # Update configuration of the measure class
    def update_config(self, opt: int):
        self.cfg = Config.get_config(opt)


# Loads readings from previous session. To be used for plotting / data manipulation
def load_sessiondata(fname):
    # Read the JSON file and load its contents into a dictionary
    with open(fname, 'r') as file:
        dict = json.load(file)
    
    return dict

# Load correction data from csv
def loadcorrection(fname):
    with open(fname, 'r') as f:
        # frequency/correction list
        fclist = [tuple(x.split(',')) for x in f.read().split('\n')]         
        return fclist

# Adjusts read data according to corrections
def applycorrection(data, datax, fclist):
    data0 = []
    for i in range(len(data)):
        data0.append(data[i] + getfc(datax[i], fclist))
    return data0

# Define correction for specific freq
def getfc(freq, fclist):
    f1 = int(fclist[0][0])
    c1 = float(fclist[0][1])
        
    for i in range(1,len(fclist)):
        if freq >= f1 and freq <= int(fclist[i][0]):
            fdiff = int(fclist[i][0]) - f1
            cdiff = float(fclist[i][1]) - c1
            m = (freq - f1) / fdiff
            return c1+m*cdiff
            
        f1 = int(fclist[i][0])
        c1 = float(fclist[i][1])
            
    return 0  

# Get peak of read data
def getpeaks(lag, threshold, influence, data, datax):
    signals = np.zeros(len(data))
    filteredY = np.array(data)
    avgFilter = [0]*len(data)
    stdFilter = [0]*len(data)
    avgFilter[lag - 1] = np.mean(data[0:lag])
    stdFilter[lag - 1] = np.std(data[0:lag])
    for i in range(lag, len(data)):
        if abs(data[i] - avgFilter[i-1]) > threshold * stdFilter [i-1]:
            if data[i] > avgFilter[i-1]:
                signals[i] = 1
            else:
                signals[i] = -1

            filteredY[i] = influence * data[i] + (1 - influence) * filteredY[i-1]
            avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
            stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])
        else:
            signals[i] = 0
            filteredY[i] = data[i]
            avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
            stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])

    d = dict(signals = np.asarray(signals),avgFilter = np.asarray(avgFilter),
             stdFilter = np.asarray(stdFilter))
    #return tuple with lists for datax and data 
    pf = [datax[i] for i in range(len(d['signals'])) if d['signals'][i] > 0]
    pv = [data[i] for i in range(len(d['signals'])) if d['signals'][i] > 0]
    return pf,pv

def plotSingleCanvas(meas, canvas, axis, ref=None, peaklist = None, xlabel = "Frequency", 
            ylabel = "dBuV", label = None, title = None): 
        
    # Clear previous plots
    plt.cla()
    plt.close()

    fclist = loadcorrection('tbaf1m.csv')
    datax = meas["Frequency"]
    data = applycorrection(meas["Sig_Level"], datax, fclist)

    # Clear the canvas before drawing the plot
    axis.clear()
    axis.plot(datax, data, linewidth = 0.5, label = label)

    if ref:
        axis.plot(ref.datax, ref.data, linewidth = 0.5, ls=':')
        
    if peaklist:            
        axis.scatter(peaklist[0] , peaklist[1])

    axis.set_title(title)
    axis.set_xlabel(xlabel)
    axis.set_ylabel(ylabel)
    axis.grid(True)

    canvas.draw()

    return axis


# Plot waveform         # fig = plt
def plotall(measurements, ref=None, peaklist = None, xlabel = "frequency", 
            ylabel = "dBuV", title = "Measurement Plot", label = ""): 
    
    # Clear previous plots
    plt.cla()
    plt.close()

    fig, ax = plt.subplots()  # Create a new figure and axes
    fclist = loadcorrection('tbaf1m.csv')
    plt.cla()
    for meas in measurements:
        datax = meas["Frequency"]
        data = applycorrection(meas["Sig_Level"], datax, fclist)

        #limit = [ 50 if x < 230000000 else 58 for x in datax]
        #plt.plot(datax, data, datax, limit, linewidth = 0.5, label = f'{meas["JSON_Name"]}/{meas["Name"]}')
        ax.plot(datax, data, linewidth = 0.5, label = f'{meas["JSON_Name"]}/{meas["Name"]}')
        if ref:
            ax.plot(ref.datax, ref.data, linewidth = 0.5, ls=':')
            
        if peaklist:            
            ax.scatter(peaklist[0] , peaklist[1])

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid()

    plt.show()
    plt.close(fig)


def list_json_files(directory = ''):

    json_files = []              # list of valid json dictionaries
    if directory == '':
        # Use glob to find all JSON files in the current folder
        # If no directory is provided
        json_file_paths = glob.glob(os.path.join('.','**/*.json'), recursive=True)
    else:
        # Else find files in given directory / sub directory
        json_file_paths = glob.glob(os.path.join(directory,'**/*.json'),  recursive=True)

    # Filter out invalid json files
    for file in json_file_paths:
        # load data from json file
        file_dict = load_sessiondata(file)
        # Search for at least one valid measurement in each json file
        for key in file_dict.keys():
            if key.startswith("measure0"):
                # Append to list of valid json files
                json_files.append({"filename":os.path.basename(file), "filepath": file})

    # Print the list of valid JSON files found
    if json_files != None:
        #print("Found JSON files:")
        #count = 0
        #for valid_json_file in json_files:
        #    print(f'{count}. {valid_json_file.get("filename")}')
        #    count += 1
        return json_files

    else:
        #print("No JSON files found in the folder.")
        return


# API's
#def meas_instr():
    #dev = DSA832()      # Create device object
    #Session(dev, input("Savefile Name: "), input("Test Description:")).begin()

#def meas_plot():
#    files = list_json_files()
#    selection = int(input("Select file to plot: "))
#    plotall_measured(meas[selection])

#meas_plot()
#meas_instr()