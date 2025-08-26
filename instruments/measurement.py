from threading import Thread
import json
import queue
import time

from instruments.DSA832_instrument import InstrumentBase
from utils.message import MSG, THREADMSG 


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

    correctiontemplate = {
    "distance": {
        "type": "int",
        "value": 1,
        "displayname": "Distance",
        "unit": "m",
        "tip": "Distance from antenna"
        },
        "frequency": {
            "type": "list",
            "value": [
                20000000, 25000000, 27000000, 30000000, 35000000, 40000000, 50000000, 60000000, 70000000, 80000000,
                90000000, 100000000, 110000000, 120000000, 125000000, 130000000, 140000000, 150000000, 160000000,
                170000000, 175000000, 180000000, 190000000, 200000000, 225000000, 250000000, 275000000, 300000000,
                325000000, 350000000, 400000000, 425000000, 450000000, 475000000, 500000000, 525000000, 550000000,
                575000000, 600000000, 625000000, 650000000, 675000000, 700000000, 750000000, 800000000, 850000000,
                900000000, 950000000, 1000000000
            ],
            "displayname": "Frequency",
            "unit": "Hz",
            "tip": "Frequency points for correction"
        },
        "level": {
            "type": "list",
            "value": [
                29.10, 28.95, 28.89, 28.80, 28.65, 28.51, 28.19, 27.72, 26.73, 25.56, 24.76, 24.06, 23.07, 22.11,
                21.77, 21.54, 21.54, 21.79, 21.23, 19.58, 18.56, 17.66, 16.43, 16.18, 17.24, 17.70, 17.42, 17.85,
                19.85, 19.73, 21.10, 21.44, 21.61, 22.65, 22.94, 22.94, 23.87, 24.20, 24.23, 25.19, 25.57, 25.53,
                26.40, 26.81, 28.01, 28.57, 28.89, 30.03, 30.71
            ],
            "displayname": "Correction Level",
            "unit": "dB",
            "tip": "Correction values corresponding to each frequency"
        }
    }

    cispr32classa_template = {
        "name": {
            "type": "str",
            "value": "CISPR32 Class A",
            "displayname": "Standard Name",
            "tip": "Name of the standard"
        },
        "description": {
            "type": "str",
            "value": "standard for 1m",
            "displayname": "Description",
            "tip": "Description of the standard"
        },
        "limits": {
            "type": "list",
            "value": [
                {
                    "min_freq": 0,
                    "max_freq": 230,
                    "limit": 60
                },
                {
                    "min_freq": 230,
                    "max_freq": None,
                    "limit": 67
                }
            ],
            "displayname": "Limits",
            "tip": "Frequency ranges and their limits"
        }
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

    def __init__(self, instrument : InstrumentBase = None):
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
    
    @classmethod
    def modifycorrectiontemplate(cls, inputtemplate: dict | None = None ) -> dict:

        template = cls.correctiontemplate.copy()
        if inputtemplate is None:
            return template
        for k,v in inputtemplate.items():
            if k in template:
                if type(v) == dict:
                    template[k]['value'] = v['value']
                else:
                    template[k]['value'] = v
        return template
    
    @classmethod
    def modifystandardtemplate(cls, inputtemplate: dict | None = None ) -> dict:
        template = cls.cispr32classa_template.copy()
        if inputtemplate is None:
            return template

        template["limits"]["value"] = inputtemplate
        return template

    def wait(self, timesec):
        tstart = time.time()
        while tstart + timesec > time.time():
            time.sleep(0.1)
            if not self.runthread:
                break

    def setinstrument(self, instrument : InstrumentBase):
        self.instrument = instrument

    def setconfig(self, config : dict):
        self.meascfg = { k:v for (k,v) in config.items() if v is not None}


    def measureqp_thread(self, freq):

        self.instrument.set('fstart',freq)
        self.instrument.set('fstop',freq)
        self.instrument.set('fspan',0)
        self.instrument.set('tracemode', 'Maxhold')
        self.instrument.set('detector','QPeak')
        sweeptime = self.instrument.get('sweeptime')
        self.instrument.set('initiate',1)
        time.sleep(sweeptime * self.meascfg['sweepcount'] + 1)
        while(self.instrument.get('sweepcountcurrent') != self.meascfg['sweepcount']):
            self.wait(sweeptime * self.meascfg['sweepcount'] + 1)
        data = self.instrument.get('data')
        #TODO Correction factor somewhere here
        return max(data)    

    def measure_thread(self, msgqueue : queue.SimpleQueue):
        self.runthread = True
        self.ydataRaw = []
        self.ydata = []
        self.meascfg = self.defaultparams | self.meascfg
        self.createsubmeasurements()

        for k,v in self.meascfg.items():
            if v != None:
                #print('setting', k, v)
                self.instrument.set(k,v)
        
        for m in self.submeaslist:            
            self.instrument.set('fstart',m[0])
            self.instrument.set('fstop',m[1])
            self.instrument.set('tracemode', self.meascfg['tracemode'])
            sweeptime = self.instrument.get('sweeptime')
            self.instrument.set('initiate',1)
            time.sleep(sweeptime * self.meascfg['sweepcount'] + 1)
            while(self.instrument.get('sweepcountcurrent') != self.meascfg['sweepcount']):
                self.wait(sweeptime * self.meascfg['sweepcount'] + 1)
            self.ydataRaw.extend(self.instrument.get('data'))
            self.ydata = self.ydataRaw.copy()
            #self.ydata.extend(self.instrument.get('data'))
            self.createfrequencylist(m[1])
            self.applycorrection()
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
        step = (fstop - self.meascfg['fstart']) / len(self.ydata)
        self.xdata = [ int(self.meascfg['fstart'] + step//2 + n * step) for n in range(len(self.ydata))]

    #adjusts data in self.ydata according to self.corr
    def applycorrection(self):       
        for i in range(len(self.ydata)):
            self.ydata[i] = self.ydata[i] + self.getfc(self.xdata[i])
        
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

    def loadcorrectionfile(self, file):
        with open(file, 'r') as f:
            data = json.load(f)
            self.fclist = list(zip(data["correction"]["frequency"], data["correction"]["level"]))

    def setcorrectiondata(self, jsondata):
        freq = json.loads(jsondata["frequency"])
        level =  json.loads(jsondata["level"])
        self.fclist = [(int(f), float(l)) for f, l in zip(freq, level)]

class EUTSetup:
    def __init__(self):
        pass
    
class MeasurementResult:
    def __init__(self):        
        self.measurementconfig = None
        self.xdata = []
        self.ydata = []


