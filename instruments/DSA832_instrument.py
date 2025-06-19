import socket
import time
from io import BytesIO

# FOR DEBUGGING ONLY (Allows for breakpoints in the debugger)
#import pdb;

from utils import message
from utils.message import *
from instruments.instrument_abstract import InstrumentBase
from config import LOCAL_IP


'''
Desc: Stores configuration information / methods
Para: Instrument abstract class
Return None
'''
class Instrument(InstrumentBase):

    name = 'DSA832'

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
        
    def connect(self, ip = LOCAL_IP, port=5555):               
        try:
            self.sock.settimeout(5)
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
        try:
            data = BytesIO()
            for _ in range(20):
                data.write(self.sock.recv(12000))
                if b'\n' in data.getvalue():
                    return data.getvalue().decode('utf-8').strip()
                time.sleep(0.1)
        except TimeoutError:
            print('TimeoutError: No data received') #!!! Todo: handle as error        
        
    # Format trace data from string to floats
    def processtrace(self, data) -> float:
        v = data.split(',')
        v[0] = v[0].split()[1]
        return [ round(float(n),1) for n in v]

