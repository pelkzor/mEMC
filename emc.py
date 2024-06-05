import socket
import json
import time
from matplotlib import pyplot as plt
from matplotlib import ticker
import mplcursors

from itertools import groupby
import numpy as np

#cfg = {'rbw':None, 'vbw':None, 'amp':0, 'atten':1, 'detector':'POSitive'

class Config:
    pass

def cfg_condqp():   #conducted emf by cable - quasi filter
    return {'continuous':0, 'xscale':'LIN', 'fstart':150000, 'fstop':30000000, 'sweeptime': 15, 'rbw':9000, 'vbw':9000, 'amp':0, 'atten':0, 'detector':'QPEak', 'emifilter':1, 'sweeppoints':601, 'sweepcount':1, 'tracemode':'MAXHold', 'unit':'dBuV', 'offset':10}

def cfg_cond2():    #generic cibduced emf
    return {'continuous':0, 'xscale':'LIN', 'fstart':150000, 'sweeptime': 0.2, 'fstop':30000000, 'rbw':9000, 'vbw':9000, 'amp':0, 'atten':0, 'detector':'POSitive', 'emifilter':1, 'sweeppoints':601, 'sweepcount':1, 'tracemode':'MAXHold', 'unit':'dBuV', 'offset':10}        
    
def cfg_cond1():    #generic condiced emf
    return {'continuous':0, 'xscale':'LIN', 'fstart':150000, 'sweeptime': 0.2, 'fstop':30000000, 'rbw':9000, 'vbw':9000, 'amp':0, 'atten':0, 'detector':'POSitive', 'emifilter':1, 'sweeppoints':601, 'sweepcount':20, 'tracemode':'MAXHold', 'unit':'dBuV', 'offset':10}

def cfg_rad1():     #datiation emmission
    return {'continuous':0, 'xscale':'LIN', 'offset': 0, 'fstart':30000000, 'fstop':1000000000, 'sweeptime': 0.2, 'rbw':120000, 'vbw':120000, 'amp':1, 'atten':0, 'detector':'POSitive', 'emifilter':1, 'sweeppoints':601, 'sweepcount':20, 'tracemode':'MAXHold', 'unit':'dBuV', 'offset':0}

def cfg_radcoarse():    #Less resolution
    return {'continuous':0, 'xscale':'LIN', 'offset': 0, 'fstart':30000000, 'fstop':1000000000, 'sweeptime': 0.2, 'rbw':1000000, 'vbw':1000000, 'amp':1, 'atten':0, 'detector':'POSitive', 'emifilter':1, 'sweeppoints':601, 'sweepcount':20, 'tracemode':'MAXHold', 'unit':'dBuV', 'offset':0}

def cfg_mt100():        #Specifc to measurement transformer
    return {'continuous':0, 'xscale':'LIN', 'offset': 0, 'fstart':150000, 'fstop':100000000, 'sweeptime': 0.2, 'rbw':9000, 'vbw':9000, 'amp':1, 'atten':0, 'detector':'POSitive', 'emifilter':1, 'sweeppoints':601, 'sweepcount':20, 'tracemode':'MAXHold', 'unit':'dBuV', 'offset':0}

class Measurement:

    def __init__(self, filename=None, descr=''):
        
        self.description=descr
        if type(filename) is str:
            self.loaddata(filename)
            if len(self.description) == 0:
                self.description = filename
        else:
            self.data = []
            
        self.cfg = {'continuous':0, 'fstart':30000000, 'fstop':1000000000, 'rbw':120000, 'vbw':1000000, 'amp':1, 'atten':0, 'detector':'POSitive', 'emifilter':1, 'sweeppoints':601, 'sweepcount':20, 'tracemode':'MAXHold', 'unit':'dBuV', 'offset':0, 'step':None}

    
    def create(self):
        self.span = self.cfg['fstop']-self.cfg['fstart']
        self.totpoints = self.span / self.cfg['rbw']
        self.nmeas = int(self.totpoints / self.cfg['sweeppoints'] + 0.999)
        self.subspan = int(self.span / self.nmeas)
        
        self.mlist = []
        
        fs = self.cfg['fstart']
        fe = fs + self.subspan
        while(fs + 1000 < self.cfg['fstop']):
            self.mlist.append((fs,fe))
            fs = fs + self.subspan
            fe = fe + self.subspan
        
        return self.mlist

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
    
    #loads file with frequency and correction values i.e. fclist a list of tuples (freq,corr)
    def loadcorrection(self, file):
        with open(file, 'r') as f:
            self.fclist = [tuple(x.split(',')) for x in f.read().split('\n')]         # frequency/correction list
    
    def setdatafreq(self):            
        step = (self.cfg['fstop'] - self.cfg['fstart']) / len(self.data)
        self.datax = [ self.cfg['fstart'] + step//2 + n * step for n in range(len(self.data))]
        
    def savedata(self, fname):
        with open(fname,'w') as f:        
            for i in range(len(self.data)):
                f.write(str(self.datax[i]) + ',' + str(self.data[i]) + '\n')
    
    def save(self, fname):
        meas = {}
        meas['meas_cfg'] = self.cfg
        
    
    def loaddata(self, fname):
        self.data = []
        self.datax = []        
        with open(fname, 'r') as f:
            for line in f:
                v = line.split(',')
                self.datax.append(float(v[0]))
                self.data.append(float(v[1]))                       

    def getpeaks2(self):       
        start = 0
        sequence = []
        d = [ int(n) for n in self.data]
        for key, group in groupby(d):
            sequence.append((key, start))
            start += sum(1 for _ in group)

        for (b, bi), (m, mi), (a, ai) in zip(sequence, sequence[1:], sequence[2:]):
            if b < m and a < m:
                yield m, mi

    def getpeaks3(self, c=10, a=0.9, nd = 0.5, ndstep = 1, th = 20):
    
        plist = []
        lmax = 0
        amplim = False
        ndelta = False
        ct = 0
        
        for i in range(len(self.data)):
            
            if self.data[i] > self.data[lmax]:
                lmax = i
                amplim = False
                ct = 0
            else:
                ct += 1               
                
                if self.data[i] < a * self.data[lmax]:                
                    amplim = True                    
                if i > ndstep and self.data[i-ndstep] - self.data[i] > nd * self.data[i-ndstep]:
                    ndelta = True
                
                if (ct > c and amplim ) or self.data[i] < 0.5 * self.data[lmax] or ndelta:
                    if self.data[lmax] >= th:
                        plist.append(lmax)
                    lmax = i
                    amplim = False
                    ndelta = False
                    ct = 0
                    
        return ( [ self.datax[i] for i in plist], [self.data[i] for i in plist] )
   
    def getpeaks(self, lag, threshold, influence):
        signals = np.zeros(len(self.data))
        filteredY = np.array(self.data)
        avgFilter = [0]*len(self.data)
        stdFilter = [0]*len(self.data)
        avgFilter[lag - 1] = np.mean(self.data[0:lag])
        stdFilter[lag - 1] = np.std(self.data[0:lag])
        for i in range(lag, len(self.data)):
            if abs(self.data[i] - avgFilter[i-1]) > threshold * stdFilter [i-1]:
                if self.data[i] > avgFilter[i-1]:
                    signals[i] = 1
                else:
                    signals[i] = -1

                filteredY[i] = influence * self.data[i] + (1 - influence) * filteredY[i-1]
                avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
                stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])
            else:
                signals[i] = 0
                filteredY[i] = self.data[i]
                avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
                stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])

        d = dict(signals = np.asarray(signals),avgFilter = np.asarray(avgFilter),stdFilter = np.asarray(stdFilter))
        #return tuple with lists for datax and data 
        pf = [ self.datax[i] for i in range(len(d['signals'])) if d['signals'][i] > 0]
        pv = [ self.data[i] for i in range(len(d['signals'])) if d['signals'][i] > 0]
        return pf,pv

    def plot(self, ref=None, peaklist = None): 
        limit = [ 50 if x < 230000000 else 58 for x in self.datax]
        
        
        plt.plot(self.datax, self.data, self.datax, limit, linewidth = 0.5)
        if ref:
            plt.plot(ref.datax, ref.data, linewidth = 0.5, ls=':')
            
        if peaklist:            
            plt.scatter(peaklist[0] , peaklist[1])
        
        plt.gcf().text(0.01,0.95,'notes:')
        plt.title("A")
        plt.xlabel("frequency")
        plt.ylabel("dBuV")
        plt.ylim((0,60))
        plt.grid()
        plt.show()

class DSA832:  
    
    def __init__(self):
        self.loadcmd()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data = b''
        self.trace = None
        self.connect()
    
    def __setitem__(self, name, value):
        if name not in self.inst:            
            print('Error: Unknown command')
    
        if type(value) == tuple:
            return self.cmd(name, *value)
        else:
            return self.cmd(name, value)
            
    def __getitem__(self, name):
        pass
        
    def measure(self, meas):
        meas.create()
        meas.data = []
        
        
        for k,v in meas.cfg.items():
            if v != None:
                self[k] = v

        
        for m in meas.mlist:
            self['fstart'] = m[0]
            self['fstop'] = m[1]            
            self['tracemode'] = meas.cfg['tracemode']            
            sweeptime = self.cmd('sweeptime','?')            
            self['initiate'] = 1            
            print('st = ', sweeptime)
            print ('sleeping ', sweeptime * meas.cfg['sweepcount'] + 1, 's')
            time.sleep(sweeptime * meas.cfg['sweepcount'] + 1)
            while(self.cmd('sweepcountcurrent','?') != meas.cfg['sweepcount']):
                time.sleep(sweeptime * meas.cfg['sweepcount'] + 1)
            meas.data.extend(self.cmd('tracedata',1))
        
        meas.setdatafreq()
        
    def measuresingle(self, meas):
        meas.data = []
        
        for k,v in meas.cfg.items():
            if v != None:
                self[k] = v       
        
        #self['fstart'] = meas.cfg['fstart']
        #self['fstop'] = meas.cfg['fstop']
        #self['tracemode'] = meas.cfg['tracemode']        
        sweeptime = self.cmd('sweeptime','?')
        self['initiate'] = 1        
        print('st = ', sweeptime)
        print ('sleeping ', sweeptime * meas.cfg['sweepcount'] + 1, 's')
        time.sleep(sweeptime * meas.cfg['sweepcount'] + 1)
        while(self.cmd('sweepcountcurrent','?') != meas.cfg['sweepcount']):
            time.sleep(sweeptime * meas.cfg['sweepcount'] + 1)      
        meas.data.extend(self.cmd('tracedata',1))
        
        meas.setdatafreq()
        
    
    def loadcmd(self):
        with open('vars.json','r') as f:
            self.inst = json.loads(f.read())
    

    
    
    def cmd(self, cmd, arg1=None, arg2=None):
    
        if not cmd in self.inst:
            print("No such command")
        c = self.inst[cmd]['scpi']
        
        if arg1 != None:
            t = self.inst[cmd]['type']
            
            if arg1 == '?':
                c = c + '?'            
            elif t == 'int' or t == 'float':
                if type(arg1) == int or type(arg1) == float:
                    c = c + ' ' + str(arg1)
                if type(arg2) == int or type(arg2) == float:
                    c = c + ' ' + str(arg2)
            elif t == 'intns':
                if type(arg1) == int:
                    c = c + str(arg1)              
            elif t == 'enum':
                if type(arg1) == int:
                    c = c + ' ' + self.inst[cmd]['enum'][arg1]
                else:
                    c = c + ' ' + arg1
            elif t == 'filename':
                c = c + ' E:\\' + arg1
            print(c)
            
                   
        self.send(c)
        if 'delay' in self.inst[cmd]:
            time.sleep(self.inst[cmd]['delay'])
        else:
            time.sleep(0.1)
        
        fmt = None
        if 'read' in self.inst[cmd]:
            fmt = self.inst[cmd]['read']
            self.cleardata()
            time.sleep(1)
            d = self.recv()
            if fmt == 'trace':
                return self.processtrace(d)
            
        elif arg1 == '?':
            fmt = self.inst[cmd]['type']
            time.sleep(0.2)
            d = self.recv()
            if d is None:
                time.sleep(1)
                d = self.recv()
            if fmt == 'int':
                return int(d)
            elif fmt == 'float':
                return float(d)
            
                
                
                
                
    def emifilter(on = True):
        if on:
            self.send(':SENSe:BANDwidth:EMIFilter:STATe ON')
        else:
            self.send(':SENSe:BANDwidth:EMIFilter:STATe OFF')
    
    def setrbw(self, rbw):
        self.send(':SENSe:BANDwidth:RESolution '+str(rbw))
        
    def setrbw(self, vbw):
        self.send(':SENSe:BANDwidth:VIDeo '+str(vbw))
    
    def setspan(self, span):
        self.send(':SENSe:FREQuency:SPAN '+str(span))

    def setcenter(self, freq):
        self.send(':SENSe:FREQuency:CENTer '+str(freq))
    
    def settracemode(self, mode, tracenum=1):
        modestr = ('WRITe','MAXHold','MINHold','VIEW','BLANk','VIDeoavg','POWeravg')
        if type(mode) == str:
            self.send(':TRACe'+str(tracenum)+':MODE '+mode)
        if type(mode) == int:
            self.send(':TRACe'+str(tracenum)+':MODE '+modestr[mode])
    
    def setcontinuous(self,cont = True):
        if cont:
            self.send(':INITiate:CONTinuous ON')
        else:
            self.send(':INITiate:CONTinuous OFF')
    
    def connect(self, ip = '192.168.1.70'):
        self.sock.connect(('192.168.1.70', 5555))
        self.sock.setblocking(False)
        
    def send(self, cmd):
        self.sock.send((cmd+'\r\n').encode('utf-8'))
        
    def recv(self, handler=None):
        
        for i in range(2):
            self.data = b''
            try:
                d = self.sock.recv(20000)
                if len(d):
                    self.data = self.data + d
                print(d.decode('utf-8'))
                return d.decode('utf-8')
            except Exception as e:
                print(e)
                time.sleep(2)

    def cleardata(self):
        self.data = b''
        
    def processtrace(self, data):
        v = data.split(',')
        v[0] = v[0].split()[1]
        return [ float(n) for n in v]
    
    def multitrace(self, fstart, fstop, step):
        data = []
        start = fstart
        stop = fstart + step
        while True:
            self.exec('freqstart',start)
            self.exec('freqstop',stop)
            
            self.send(':TRACe:DATA? TRACE' + str(tracenum))
            time.sleep(0.5)
        
    
    def gettrace(self,tracenum=1):
        self.cleardata()
        self.send(':TRACe:DATA? TRACE' + str(tracenum))
        time.sleep(0.5)
        d = self.recv()
        self.trace = self.processtrace(d)
        fstart = 0
        fstop = 3200000000
        self.scalex = [ fstart + n*(fstop-fstart)/len(self.trace) for n in range(len(self.trace))]

def plotoold(meas, ref=None):   
    #limit = [ 50 if x < 230000000 else 58 for x in scalex]
    plt.gcf().text(0.01,0.95,'notes:')
    plt.title("A")
    plt.xlabel("frequency")
    plt.ylabel("dBuV")
    plt.ylim((0,60))
    plt.grid()
    plt.legend(loc="upper left")
    if type(meas) is list:
        for m in meas:
            plt.plot(m.datax, m.data, linewidth = 0.5, ls=':', label=m.description)
        
        #plt.plot(scalex, limit, linewidth = 0.5)
    else:
        plt.plot(meas.datax, meas.data, linewidth = 0.5)
    if ref:
        plt.plot(ref.datax, ref.data, linewidth = 0.5, ls=':', label=ref.description)
        
    plt.legend(loc="upper left")
    plt.show()

def plot(meas, ref=None, ymin = 10, ymax = 70, log=False, lim='none', saveimg=None):   
    #limit = [ 50 if x < 230000000 else 58 for x in scalex]
    limconducted_avgx, limconducted_avgy = [150000,  500000, 5000000, 5000000, 30000000], [56, 46, 46, 50, 50]
    limconducted_qpx, limconducted_qpy = [150000, 500000, 5000000, 5000000, 30000000], [66, 56, 56, 60, 60]
    
    limradiated_avgx, limradiated_avgy = [30000000,  230000000, 230000000, 1000000000], [50, 50, 56, 56]
    limradiated_qpx, limradiated_qpy = [30000000,  230000000, 230000000, 1000000000], [50, 50, 56, 56]
    
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.text(0.01,0.95,'notes:')
    ax.set_title("A")
    ax.set_xlabel("frequency [Hz]")
    ax.set_ylabel("dBuV")
    ax.set_ylim((ymin,ymax))
    ax.grid()
    
    if log:
        ax.set_xscale("log")
    mkfunc = lambda x, pos: '%.1f G' % (x * 1e-9) if x >= 1e9 else '%3.1f M' % (x * 1e-6) if x >= 1e6 else '%3.1f k' % (x * 1e-3)
    #mkfunc = lambda x, pos: '%.1f' % (x * 1e-6)
    mkformatter = ticker.FuncFormatter(mkfunc)
    ax.xaxis.set_major_formatter(mkformatter)
    
    if lim == 'cond':
        ax.plot(limconducted_avgx, limconducted_avgy, linewidth = 1, ls='-', color = 'red', label = 'Lim AVG')
        ax.plot(limconducted_qpx, limconducted_qpy, linewidth = 1, ls='-', color = 'blue', label = 'Lim QP')
    elif lim == 'rad':        
        ax.plot(limradiated_avgx, limradiated_avgy, linewidth = 1, ls='-', color = 'red', label = 'Lim AVG')
        ax.plot(limradiated_qpx, limradiated_qpy, linewidth = 1, ls='-', color = 'blue', label = 'Lim QP')
    
    if type(meas) is list:
        for m in meas:
            ax.plot(m.datax, m.data, linewidth = 0.5, ls='-', label=m.description)
        
        #plt.plot(scalex, limit, linewidth = 0.5)
    else:
        ax.plot(meas.datax, meas.data, linewidth = 0.5)
    if ref:
        ax.plot(ref.datax, ref.data, linewidth = 0.5, ls='-', label=ref.description)
    box = ax.get_position()
    
    plt.tight_layout(rect=[0, 0, 1, 1])
    #cursor = Cursor(ax, useblit=True, color='red', linewidth=0.5)
    mplcursors.cursor()    
    #ax.set_position([box.x0, box.y0, box.width , box.height * 0.8])
    #ax.legend(loc='upper left', bbox_to_anchor=(0.0, 1.3))
    ax.legend(loc="upper right")
    if saveimg:
        plt.savefig(saveimg)
    plt.show(block=False)

def meas(i, name):
    m = Measurement(descr=name)
    m.loadcorrection('tbaf1m.csv')
    i.measure(m)
    m.applycorrection()
    return m

def meascond(i, name,cfg=None):            
    m = Measurement(descr=name)
    if cfg == None:
        m.cfg = cfg_cond1()
    else:
        m.cfg = cfg
    i.measure(m)
    m.savedata(m.description)
    return m
    
    
def measrad(i, name,cfg=None):            
    m = Measurement(descr=name)
    if cfg == None:
        m.cfg = cfg_rad1()
    else:
        m.cfg = cfg
    m.loadcorrection('tbaf1m.csv')
    i.measure(m)
    m.applycorrection()
    m.savedata(m.description)
    return m

#i=DSA832()


#bg=Measurement('comdry-bg.csv')
#t1=Measurement('comdry-back-0deg-lcd-nokeys.csv')
#t2=Measurement('comdry-front-0deg-lcd-nokeys.csv')
#t3=Measurement('comdry-back-90deg-lcd-nokeys.csv')
#t4=Measurement('comdry-front-90deg-lcd-nokeys.csv')
#mlist = [t1,t2,t3,t4]
