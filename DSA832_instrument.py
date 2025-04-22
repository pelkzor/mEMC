import socket
import time
from io import BytesIO
from threading import Thread
import queue

# FOR DEBUGGING ONLY (Allows for breakpoints in the debugger)
#import pdb;
from message import *
from instrument_abstract import Instrument

'''
Desc: Stores configuration information / methods
Para: Instrument abstract class
Return None
'''
class DSA832(Instrument):

    params = {
        "fstart":{"type":"int", "min":0, "max":3200000000, "scpi":":SENSe:FREQuency:STARt"},
        "fstop":{"type":"int", "min":0, "max":3200000000, "scpi":":SENSe:FREQuency:STOP"},
        "fcenter":{"type":"int", "min":0, "max":3200000000, "scpi":":SENSe:FREQuency:CENTer"},
        "fspan":{"type":"int", "min":0, "max":3200000000, "scpi":":SENSe:FREQuency:SPAN"},
        "emifilter":{"type":"bool", "enum": ["OFF","ON"], "scpi":":SENSe:BANDwidth:EMIFilter:STATe"},
        "rbw":{"type":"int", "min":10, "max":1000000, "scpi":":SENSe:BANDwidth:RESolution"},
        "rbwauto":{"type":"bool", "enum": ["OFF","ON"], "scpi":":SENSe:BANDwidth:RESolution:AUTO"},
        "continuous":{"type":"bool", "enum": ["OFF","ON"], "scpi":":INITiate:CONTinuous"},
        "tracemode":{"type":"select", "option": ["WRIT","MAXH","MINH","VIEW","BLAN","VID","POW"], "displayoption": ["Write","Maxhold","Minhold","View","Blank","Videoavg","Poweravg"], "scpi":":TRACe1:MODE"},
        "initiate":{"type":"cmd", "readonly":1, "scpi":":INITiate:IMMediate"},
        "data":{"type":"data", "readonly":1, "scpi":":TRACe:DATA? TRACE1"},
        "sweepcount":{"type":"int", "min":1, "max":9999, "scpi":":SENSe:SWEep:COUNt"},
        "sweepcountcurrent":{"type":"int", "readonly":1, "scpi":":SENSe:SWEep:COUNt:CURRent"},
        "sweeppoints":{"type":"int", "min":101, "max":3001, "scpi":":SENSe:SWEep:POINts"},
        "sweeptime":{"type":"float", "min":0.00002, "max":3200, "scpi":":SENSe:SWEep:TIME"},
        "detector":{"type":"select", "option": ["NEG","NORM","POS","RMS","SAMP","VAV","QPEAK"], "displayoption": ["Negative","Normal","Positive","RMS","Sample","VAverage","QuasiPeak"], "scpi":":SENSe:DETector:FUNCtion"},
        "unit":{"type":"select", "option": ["DBM","DBMV","DBUV","V","W"], "displayoption": ["dBm","dBmV","dBuV","V","W"], "scpi":":UNIT:POWer"},
        "attenuation":{"type":"int", "min":0, "max":30, "scpi":":SENSe:POWer:RF:ATTenuation"},
        "autoattenuation":{"type":"bool", "enum": ["OFF","ON"], "scpi":":SENSe:POWer:RF:ATTenuation:AUTO"},
        "offset":{"type":"float", "min":-300, "max":300, "scpi":":DISPlay:WINdow:TRACe:Y:SCALe:RLEVel:OFFSet"},
        "preamplifier":{"type":"bool", "enum": ["OFF","ON"], "scpi":":SENSe:POWer:RF:GAIN:STATe"},
        "xscale":{"type":"select","option":["LIN","LOG"], "scpi":":DISPlay:WINdow:TRACe:X:SCALe:SPACing"}
    }

    defaultparams = {
        "fstart":None,
        "fstop":None,
        "fcenter":None,
        "fspan":None,
        "emifilter":1,
        "rbw":120000,
        "rbwauto":0,
        "continuous":0,
        "tracemode":"MAXH",                
        "sweepcount":20,        
        "sweeppoints":601,
        "sweeptime":0.2,
        "detector":"POS",
        "unit":"dBuV",
        "attenuation":0,
        "autoattenuation":0,
        "offset":0,
        "preamplifier":0,
        "xscale":"LIN"
    }

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        

    def get(self, name):
        return self.command(name)
            
    def set(self, name, value):
        self.command(name, value)

        readval = self.get(name)
        if readval == value:
            return True
        return False
        
    def connect(self, ip = '192.168.1.70', port=5555):               
        try:
            self.sock.settimeout(2)
            self.sock.connect((ip, port))
            #self.sock.setblocking(False)
            return True
        except OSError as e:
            return False
    
    def disconnect(self):
        self.sock.close()

    def command(self, name, value=None):
        if not name in self.params:
            print("No such command")
            return None
        read = False
        cmd = self.params[name]['scpi']
        t = self.params[name]['type']

        if t == 'cmd':
            pass                                        #cmd is done
        elif t == 'data':
            read = True
        elif value is None:                             #if no value given
            cmd = cmd + '?'                             #add ? for query
            read = True
        else:
            if t == 'select':                               #special processing for select type to support both instrument and display variants of strings
                if value in self.params[name]['option']:    #valid instrument string
                    cmd = cmd + ' ' + str(value)            #insert value
                elif 'displayoption' in self.params[name] and value in self.params[name]['displayoption']:  #valid display string
                    indx = self.params[name]['displayoption'].index(value)                                  #get index                    
                    cmd = cmd + ' ' + str(self.params[name]['option'][indx])                                 #use same index instrument string                    
            else:
                cmd = cmd + ' ' + str(value)

        self.send(cmd)

        if read:
            d = self.recv()
            match t:
                case 'data':
                    self.data = b''                
                    return self.processtrace(d)
                case 'int' | 'bool':
                    return int(d)
                case 'float':
                    return float(d)
                case 'str':
                    return d
                case 'select':
                    if 'displayoption' in self.params[name]:
                        indx = self.params[name]['option'].index(d)
                        d = self.params[name]['displayoption'][indx]
                    return d
                    
            
    # Send command
    def send(self, cmd):        
        self.sock.send((cmd+'\r\n').encode('utf-8'))        
    
    # Receive message from device
    def recv(self) -> bytes:        
        data = BytesIO()
        for _ in range(20):
            data.write(self.sock.recv(12000))
            if b'\n' in data.getvalue():
                return data.getvalue().decode('utf-8').strip()
            time.sleep(0.1)        
        
    # Format trace data from string to floats
    def processtrace(self, data) -> float:
        v = data.split(',')
        v[0] = v[0].split()[1]
        return [ round(float(n),1) for n in v]

class Measurement():

    configtemplate = {
        "fstart": {"type":"int", "value": 30_000_000, "displayname":"Start Frequency","unit":"Hz","minval":9_000,"maxval":3_200_000_000,"tip":"Start frequency of scan"},
        "fstop": {"type":"int", "value": 1_000_000_000, "displayname":"Stop Frequency","unit":"Hz","minval":9_000,"maxval":3_200_000_000,"tip":"Stop frequency of scan"},
        "fcenter": {"type":"int", "value": None, "displayname":"Center Frequency","unit":"Hz","minval":9_000,"maxval":3_200_000_000,"tip":"Stop frequency of scan"},
        "fspan": {"type":"int", "value": None, "displayname":"Frequency Span","unit":"Hz","minval":9_000,"maxval":3_200_000_000,"tip":"Stop frequency of scan"},
        "sweeptime": {"type":"float","value":0.2,"displayname":"Sweep Time","unit":"s"},        
        "rbw": {"type":"int","value": 120_000,"displayname":"Resolution Bandwidth","minval":10,"maxval":1_000_000},
        "preamplifier": {"type":"bool","value": 0,"displayname":"Preamplifier", "enum" : ["ON","OFF"]},
        "attenuation": {"type":"int","value":0,"displayname":"Attenuation","unit":"dB","minval":0,"maxval":60},
        "detector": {"type":"select","value":"Positive","displayname":"Detector","option":["Positive","Negative","Normal","RMS","Sample","VAverage","QPeak"]},
        "emifilter": {"type":"int","value": 1,"displayname":"EMI filter","minval":0,"maxval":1},
        "sweepcount": {"type":"int","value":20,"displayname":"Sweep count","unit":"","minval":1,"maxval":1000},        
        "offset":{"type":"float", "value": 0.0, "displayname":"Signal level offset", "min":-300, "max":300, },
        "tracemode": {"type":"select","value":"Maxhold","displayname":"Trace mode","option":["Maxhold","Write","Minhold","Videoavg","Poweravg"]}
    }

    def __init__(self, instrument : Instrument = None):
        self.meascfg = None
        self.instrument = instrument

    @classmethod
    def modifytemplate(cls, inputtemplate: dict | None = None ) -> dict:

        template = cls.configtemplate.copy()
        if inputtemplate is None:
            return template
        for k,v in inputtemplate.items():
            if k in template:
                if type(v) == dict:
                    template[k]['value'] = v['value']
                else:
                    template[k]['value'] = v
        return template

    def wait(self, timesec):
        tstart = time.time()
        while tstart + timesec > time.time():
            time.sleep(0.1)
            if not self.runthread:
                break

    def setinstrument(self, instrument : Instrument):
        self.instrument = instrument

    def setconfig(self, config : dict):
        self.meascfg = { k:v for (k,v) in config.items() if v is not None}

    def measure_thread(self, msgqueue : queue.SimpleQueue):
        self.runthread = True  
        self.data = []
        self.meascfg = self.instrument.defaultparams | self.meascfg
        self.createsubmeasurements()

        for k,v in self.meascfg.items():
            if v != None:
                #print('setting', k, v)
                self.instrument.set(k,v)
        
        for m in self.submeaslist:
            msgqueue.put(('msg','Segment...'))
            self.instrument.set('fstart',m[0])
            self.instrument.set('fstop',m[1])
            self.instrument.set('tracemode', self.meascfg['tracemode'])          
            sweeptime = self.instrument.get('sweeptime')
            self.instrument.set('initiate',1)
            #print('st = ', sweeptime)
            #print ('waiting ', sweeptime * self.meascfg['sweepcount'] + 1, 's')
            time.sleep(sweeptime * self.meascfg['sweepcount'] + 1)
            while(self.instrument.get('sweepcountcurrent') != self.meascfg['sweepcount']):
                self.wait(sweeptime * self.meascfg['sweepcount'] + 1)
            self.data.extend(self.instrument.get('data'))
            self.createfrequencylist(m[1])
            msgqueue.put((MSG.THREAD,THREADMSG.DATA,None))
        self.runthread = False
        msgqueue.put((MSG.THREAD,THREADMSG.DONE, None))


    def stopmeasurement(self):
        self.runthread = False

    def startmeasurement(self, msgqueue):
        measthread = Thread(target=self.measure_thread, args=(msgqueue,))
        measthread.daemon = True
        measthread.start()        

    def createsubmeasurements(self):
        self.span = self.meascfg['fstop']-self.meascfg['fstart']
        self.totpoints = self.span / self.meascfg['rbw']
        self.nmeas = int(self.totpoints / self.meascfg['sweeppoints'] + 0.999)
        self.subspan = int(self.span / self.nmeas)
        
        self.submeaslist = []
        fs = self.meascfg['fstart']
        fe = fs + self.subspan
        while(fs + 1000 < self.meascfg['fstop']):
            self.submeaslist.append((fs,fe))
            fs = fs + self.subspan
            fe = fe + self.subspan
        return self.submeaslist
    
    def createfrequencylist(self, fstop = None):
        if fstop is None:
            fstop = self.meascfg['fstop']
        step = (fstop - self.meascfg['fstart']) / len(self.data)
        self.datax = [ self.meascfg['fstart'] + step//2 + n * step for n in range(len(self.data))]

    #adjusts data in self.data according to self.corr
    def applycorrection(self):       
        for i in range(len(self.data)):
            self.data[i] = self.data[i] + self.getfc(self.datax[i])
        
    #get correction for specific frequency
    def getfc(self, freq):
        f1 = int(self.fclist[0][0])
        c1 = float(self.fclist[0][1])
        
        for i in range(1,len(self.fclist)):
            if freq >= f1 and freq <= int(self.fclist[i][0]):
                fdiff = int(self.fclist[i][0]) - f1
                cdiff = float(self.fclist[i][1]) - c1
                m = (freq - f1) / fdiff
                return c1+m*cdiff
                
            f1 = int(self.fclist[i][0])
            c1 = float(self.fclist[i][1])
                
        return 0

    def loadcorrection(self, file):
        with open(file, 'r') as f:
            self.fclist = [tuple(x.split(',')) for x in f.read().split('\n')] 

class EUTSetup:
    def __init__(self):
        pass
    
class MeasurementResult:
    def __init__(self):        
        self.measurementconfig = None
        self.xdata = []
        self.ydata = []


