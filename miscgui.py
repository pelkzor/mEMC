import tkinter as tk
import ttkbootstrap as ttk_b
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox

from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from matplotlib import ticker
import mplcursors
from matplotlib.backend_bases import key_press_handler

from measurement import Measurement
#from DSA832_instrument import DSA832
#from simulator_instrument import Simulator
from secrets import token_hex
import json
import time

from enum import IntEnum, auto
from message import *
import queue
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='emc.log', encoding='utf-8', level=logging.ERROR)
logger.error('Starting')



_UNDEFINED_ENTRY = 'NA'

_DEFAULT_PAD = 5

_MEASUREMENT_PATH = './meastempl'
_EUT_PATH = './euttempl'
_CORRECTION_PATH = './correction'

_TEMPLATETYPE_MEASUREMENT = 'measurementtemplate'
_TEMPLATETYPE_EUT = 'euttemplate'
_TEMPLATE_KEY = 'template'


import sys
import importlib.util

def load_module(source, module_name):
	
	spec = importlib.util.spec_from_file_location(module_name, source)
	module = importlib.util.module_from_spec(spec)
	sys.modules[module_name] = module
	spec.loader.exec_module(module)
	return module


def load_instruments():
    ilist = []
    filenames = list(Path('./instruments').glob('*.py'))
    for fname in filenames:
        mod = load_module(fname, token_hex(16))
        inst = mod.Instrument
        name = inst.name
        ilist.append((name, inst))
    return ilist

def get_measurementconfigs():
    filenames = list(Path(_MEASUREMENT_PATH).glob('*.json'))    
    mconfigs = {}

    for fname in filenames:
        try:
            with open(fname,'r') as f:
                cfg = json.loads(f.read())            
                if cfg['type'] == 'measconfigtemplate':
                    mconfigs[cfg['name']] = fname.resolve()
        except Exception as e:
            print(e)
    
    return mconfigs
    
def get_eutconfigs():
    filenames = list(Path(_EUT_PATH).glob('*.json'))
    cfglist = []

    for fname in filenames:
        try:
            with open(fname,'r') as f:
                cfg = json.loads(f.read())            
                if cfg['type'] == 'eutcfg':
                    cfglist.append((cfg['name'],fname))
        except:
            pass
        return cfglist

def get_templates(path, tmpltype):
    filenames = list(Path(path).glob('*.json'))    
    mconfigs = {}

    for fname in filenames:
        try:
            with open(fname,'r') as f:
                tmpl = json.loads(f.read())            
                if tmpl['type'] == tmpltype:
                    mconfigs[tmpl['name']] = fname.resolve()
        except Exception as e:
            print(e)
    
    return mconfigs

def load_template(path, tmpltype):
    try:
        with open(path,'r') as f:
            tmpl = json.loads(f.read())
            if tmpl['type'] == tmpltype:
                return tmpl
    except Exception as e:
        print(e)
          

class DefaultGridField():

    row_classvar = 0

    def __init__(self, **kwargs):        
        self.row = kwargs.get('row',DefaultGridField.row_classvar)
        DefaultGridField.row_classvar += 1

    @classmethod
    def resetrowcount(cls):
        cls.row_classvar = 0

    def place(self,row):
        self.nlabel.grid(row=row, column=0, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky = 'EW')
        self.entry.grid(row=row, column=1, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky = 'EW')
        self.ulabel.grid(row=row, column=2, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD)

    def unplace(self):
        self.nlabel.grid_forget()
        self.entry.grid_forget()
        self.ulabel.grid_forget()

class EntryFrame(ttk_b.Frame):

    def __init__(self, parent, varname, title, value, evttarget=None):

        super().__init__(parent)
        if evttarget is None:
            evttarget = parent

        self.sval = ttk_b.StringVar()
        self.sval.trace_add('write', lambda *_: evttarget.onevent((MSG.SETVAR,varname,self.sval.get()))) #changed to validate function
        self.nlabel = ttk_b.Label(self, text = title, anchor='w')
        self.entry = ttk_b.Entry(self, textvariable=self.sval )#, validate='focusout', validatecommand=self.validate)        
        self.nlabel.grid(row=0, column=0, padx=5, pady=5, sticky='EW')
        self.entry.grid(row=0, column=1, padx=5, pady=5, sticky='EW')

    def get(self):
        return self.sval.get()

class ValueField(DefaultGridField):

    def __init__(self, parent, displayname, value=None, unit=None, **kwargs):
        super().__init__(**kwargs)
        self.sval = ttk_b.StringVar()
        self.nlabel = ttk_b.Label(parent, text = displayname, anchor='w')
        self.entry = ttk_b.Entry(parent, textvariable=self.sval, validate='focusout', validatecommand=self.validate)        
        self.ulabel = ttk_b.Label(parent, text = unit if unit is not None else '', width=8)

        self.valid = True                       
        
        self.minval = kwargs.get('minval', None)
        self.maxval = kwargs.get('maxval', None)
        self.readonly = True if 'state' in kwargs and kwargs['state'] == 'readonly' else False
        self.hidden = True if 'state' in kwargs and kwargs['state'] == 'hidden' else False
        self.allowundefined = True if ('allowundefined' in kwargs and kwargs['allowundefined']) or (value is None or not len(str(value)) or str(value).casefold() == _UNDEFINED_ENTRY.casefold()) else False

        tip = kwargs.get('tip','')
        if self.minval is not None:
            tip = tip + '\n' if len(tip) else tip
            tip += 'Minimum value {}'.format(str(kwargs['minval']))
        if self.maxval is not None:
            tip = tip + '\n' if len(tip) else tip
            tip += 'Maximum value {}'.format(str(kwargs['maxval']))          
        if self.readonly:
            self.entry.configure(validate='key')
            tip = tip + '\n' if len(tip) else tip
            tip = tip + 'Value is set to "read only" '
        if self.allowundefined:
            tip = tip + '\n' if len(tip) else tip
            tip = tip + 'Value is allowd to be empty "NA"'

        if value is None:
            self.sval.set(_UNDEFINED_ENTRY)    
        else:
            self.sval.set(str(value))
                
        if not self.hidden:             
            self.place(row=self.row)

        if len(tip):
            ToolTip(self.entry, tip)

    def isundefined(self):
        if hasattr(self,'allowundefined') and self.allowundefined: # field is allowed to be empty or 'NA'
            if hasattr(self, 'sval') and (self.sval.get().casefold() == _UNDEFINED_ENTRY.casefold() or not len(self.sval.get())):                 
                return True
        return False
    
    def getvalue(self):
        try:
            if self.valid and not self.isundefined():
                if hasattr(self, 'valueconversion'):
                    return self.valueconversion(self.sval.get())
                return self.sval.get()
        except ValueError:
            pass
        return None
        
    def set_valid(self):
        self.entry.configure(style='primary.TEntry')
        self.valid = True

    def set_invalid(self):
        self.entry.configure(style='danger.TEntry')
        self.valid = False
    
    def validate(self):
        
        if self.readonly:           #readonly implemented by failing validation, 
                                    #validation set to 'key' refusing any input            
            self.set_valid()        #field remains valid
            return False            #!!!note: Entry apparently has option for state='readonly'
        
        valid = False
        try:
            if self.isundefined():     
                self.entry.after(200, lambda : self.sval.set(_UNDEFINED_ENTRY))         #workaround to set entry text without ruining validation
                valid = True
            elif hasattr(self,'valueconversion'):
                valid = True                
                val = self.valueconversion(self.sval.get())
                if self.minval is not None and val < self.minval:
                    valid = False
                if self.maxval is not None and val > self.maxval:
                    valid = False
            else:
                valid = True        
        except ValueError:
            valid = False            
        if valid:
            self.set_valid()
        else:
            self.set_invalid()        
        return valid

class ValueFieldSelect(DefaultGridField):
    def __init__(self, parent, displayname, value=None, unit='', option=None, **kwargs):
        super().__init__(**kwargs)
        self.valid = True
        self.sval = ttk_b.StringVar()        
        self.nlabel = ttk_b.Label(parent, text = displayname, anchor='w')
        self.entry = ttk_b.Combobox(parent, values=option, textvariable=self.sval, state='readonly') #(self, textvariable=self.sval, validate='focusout', validatecommand=self.validate)
        self.ulabel = ttk_b.Label(parent, text = unit, width=8)                

        if value is not None:
            try:
                self.entry.current = option.index(value)
                self.sval.set(value)
            except:
                self.entry.current = 0
        self.place(row=self.row)

        #tooltip
        if 'tip' in kwargs:
            ToolTip(self.entry, kwargs['tip'])

    def getvalue(self):        
        return self.sval.get()
        
class ValueFieldText(DefaultGridField):             #needs DefaultGridField for row count

    def __init__(self, parent, displayname, value=None, unit='', **kwargs):       
        super().__init__(**kwargs)
        self.valid = True
        self.nlabel = ttk_b.Label(parent, text = displayname, anchor='w')
        #self.entry = ttk_b.Text(parent, width=10, height=4)   changed to ScrolledText
        self.entry = ttk_b.ScrolledText(parent, width=10, height=4)        
                
        #self.yscroll = ttk_b.Scrollbar(parent,command=self.entry.yview)
        #self.entry['yscrollcommand'] = self.yscroll.set        

        self.place(row=self.row)

        if value is not None:
            self.entry.delete(1.0, 'end')
            self.entry.insert('end', value)

        #tooltip
        if 'tip' in kwargs:
            ToolTip(self.entry, kwargs['tip'])
    
    def place(self, row):
        self.nlabel.grid(row=row, column=0, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky = 'EW')
        self.entry.grid(row=row, column=1, columnspan=2, padx=_DEFAULT_PAD+5, pady=_DEFAULT_PAD, sticky = 'EW')
        #self.yscroll.grid(row=row, column=2, padx=0, pady=0, sticky='NSW')    

    def unplace(self):
        self.nlabel.grid_forget()
        self.entry.grid_forget()
        #self.yscroll.grid_forget()
    
    def getvalue(self):
        return self.entry.get("1.0",END)

class ValueFieldFloat(ValueField):
    
    def __init__(self, parent, displayname, value, unit='', **kwargs):
        super().__init__(parent, displayname, value, unit, **kwargs)
        self.valueconversion = float

class ValueFieldInt(ValueField):

    def __init__(self, parent, displayname, value, unit = '', **kwargs):
        super().__init__(parent, displayname, value, unit, **kwargs)        
        self.valueconversion = int

class ConfigEditor(ttk_b.Frame):

    def __init__(self, parent, template=None, applybtn = True):
        super().__init__(parent)
        self.displayapplybtn = applybtn
        self.rowcount = 0
        self.fields = {}
        #self.columnconfigure(0, weight=1)
        
        self.scrollframe = ScrolledFrame(self)        
        self.scrollframe.columnconfigure(1, weight=1)
        self.scrollframe.pack(expand=True, fill='both')

        if template is not None:
            self.addfields(template)      
        #    if self.displayapplybtn:
        #        self.applybtn = ttk_b.Button(self.scrollframe, text='Apply', command=self.applychanges)
        #        self.applybtn.grid(row = DefaultGridField.row_classvar, column = 1, columnspan=2, padx = _DEFAULT_PAD, pady = _DEFAULT_PAD)        

    def updateconfig(self, template):                
        for i in list(self.fields.keys()):
            self.fields[i].unplace()
            del self.fields[i]
        self.rowcount = 0
        
        if hasattr(self,'applybtn'):
            self.applybtn.grid_forget()
            del self.applybtn

        self.addfields(template)

    def isvalid(self):
        #valid = True
        #for name,field in self.fields.items():
        #    if hasattr(field, 'readonly') and field.readonly == False:
        #        if hasattr(field, 'validate') and not field.validate():            
        #            valid = False
        #            print('Field', name, 'is invalid')
        #return valid
        return all( ( field.valid for field in self.fields.values()) )
    
    def unplacefield(self, name):
        self.fields[name].unplace()

    def deletefield(self, ):
        pass

    def deleteall(self):
        pass

    def addfields(self, fields):

        DefaultGridField.resetrowcount()
        for k,v in fields.items():                     
            newfield = None
            if not 'displayname' in v:
                v['displayname'] = k                            #if no displayname provided use key (variable name)
            match v:
                case {'type':'int'}:
                    newfield = ValueFieldInt(self.scrollframe, **v)
                case {'type':'float'}:
                    newfield = ValueFieldFloat(self.scrollframe, **v)
                case {'type':'str'}:
                    newfield = ValueField(self.scrollframe, **v)
                case {'type':'select'}:
                    newfield = ValueFieldSelect(self.scrollframe, **v)
                case {'type':'text'}:
                    newfield = ValueFieldText(self.scrollframe, **v)
                case _:
                    newfield = ValueField(self.scrollframe, **v)
            if newfield:
                self.rowcount += 1
                self.fields[k]=newfield            

        if self.displayapplybtn:
            self.applybtn = ttk_b.Button(self.scrollframe, text='Apply', command=self.applychanges)
            self.applybtn.grid(row = DefaultGridField.row_classvar, column = 1, columnspan=2, padx = _DEFAULT_PAD, pady = _DEFAULT_PAD)             

        self.isvalid()          #validate all fields (unlikely to be wrong value in template but...)

    def applychanges(self):
        #!!! finish
        print('apply \n', self.getdata())

    def __getitem__(self, x):
        return self.fields[x].getvalue()
    
    def __setitem__(self,x, v):
        self.fields[x].val = v
        self.fields[x].svar.set(str(v))

    def getdata(self):               
        return {k: v.getvalue() for k,v in self.fields.items()}


class TreeFrame(ttk_b.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        #self.l1 = ttk_b.Label(self, text = 'testlabel')
        #self.l1.pack()
        self.treeview = ttk.Treeview(self,columns=('Name','Time','Type','Comment'))
        
        self.treeview.column('#0',anchor='center')
        self.treeview.column('Name',anchor='center')
        self.treeview.column('Time',anchor='center')
        self.treeview.column('Type',anchor='center')
        self.treeview.column('Comment',anchor='center')
        self.treeview.heading('#0', text='File')
        self.treeview.heading('Name',text='Name')
        self.treeview.heading('Time',text='Creation time')
        self.treeview.heading('Type',text='Measurement type')
        self.treeview.heading('Comment',text='Comment')
        self.treeview.pack(side='left',fill='both',expand=True)
        self.tvscroll = ttk.Scrollbar(self, orient='vertical', command=self.treeview.yview)
        self.tvscroll.pack(side='left',fill='y')
        self.treeview.config(yscrollcommand=self.tvscroll.set)        

        for i in range(1000):            
            self.treeview.insert('',ttk_b.END, text=f'Treeitem{i}', values=('abc','345\n456\n234','ert'))                
        #self.treeview.insert('',ttk_b.END, text='Treeitem', values=('abc','345','ert'))
        #self.treeview.insert('',ttk_b.END, text='Treeitem', values=('abc','345','ert'))


class ToolBar(ttk_b.Frame):

    def __init__(self, parent, defaultipaddress='192.168.1.70', ilist=None, defaultinstrument=None):
        super().__init__(parent)        
        self.isconnected = False
        self.parent = parent

        ttk_b.Label(self, text='Instrument',width=25, anchor='e').grid(row=0, column=0, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD,sticky='EW')
        
        self.instrumentvar = ttk_b.StringVar()
        
        self.instrumentvar.trace_add('write', lambda *_: parent.onevent((MSG.SETVAR,'instrumentname',self.instrumentvar.get()))) 
        self.instrumentselect = ttk_b.Combobox(self, values=[i[0] for i in ilist], textvariable=self.instrumentvar, state='readonly', width=32)        
        #self.instrumentselect.bind("<<ComboboxSelected>>", lambda: parent.onevent((MSG.SETVAR,'instrumentname',self.instrumentvar.get())))
        self.instrumentselect.grid(row=0, column=1, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW') 

        ttk_b.Label(self, text='IP address [:port]',width=25, anchor='e').grid(row=1, column=0, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW')
        
        self.ipaddressvar = ttk_b.StringVar()
        self.ipaddressvar.trace_add('write', lambda *_: parent.onevent((MSG.SETVAR,'ipaddress',self.ipaddressvar.get()))) #changed to validate function
        self.ipaddressvar.set(defaultipaddress)
        self.ipaddressentry = ttk_b.Entry(self, textvariable=self.ipaddressvar, width=32)
        self.ipaddressentry.grid(row=1, column=1, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW')

        self.btnconnect = ttk_b.Button(self, text='Connect', command = lambda : parent.onevent((MSG.DISCONNECT if self.isconnected else MSG.CONNECT,self.instrumentvar.get(),self.ipaddressvar.get())))
        self.btnconnect.grid(row=2, column=0, columnspan=2, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='NSEW')

        #self.btnmeasure = ttk_b.Button(self, text='Measure', command = lambda : parent.onevent((MSG.MEASURE,)))
        #self.btnmeasure.grid(row=2, column=2, columnspan=2, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD)

        ttk_b.Label(self, text='Measurement template',width=25, anchor='e').grid(row=0, column=2, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD)
        self.mcfg = ttk_b.StringVar()
        self.mcfgselect = ttk_b.Combobox(self, textvariable=self.mcfg, state='readonly', width=32)
        self.mcfgselect.bind('<<ComboboxSelected>>', lambda _: parent.onevent((MSG.SETMEASTEMPLATE,self.mcfg.get(),self.mconfigs[self.mcfg.get()])) )
        self.mcfgselect.grid(row=0, column=3, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW')

        ttk_b.Label(self, text='EUT Template',width=25, anchor='e').grid(row=0, column=4, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD)
        self.eutcfg = ttk_b.StringVar()
        self.eutcfgselect = ttk_b.Combobox(self, textvariable=self.eutcfg, state='readonly', width=32)
        self.eutcfgselect.bind('<<ComboboxSelected>>', lambda _: parent.onevent((MSG.SETEUTTEMPLATE,self.eutcfg.get(),self.eutconfigs[self.eutcfg.get()])) )
        self.eutcfgselect.grid(row=0, column=5, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW')

        ttk_b.Label(self, text='Working directory',width=25, anchor='e').grid(row=1, column=2, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD)
        self.workdir = ttk_b.StringVar()        
        self.workdirentry = ttk_b.Entry(self, textvariable=self.workdir, state='readonly', width=32)
        self.workdirentry.bind('<1>', self.selectworkdir)
        self.workdirentry.grid(row=1, column=3, columnspan=2, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW')

        self.loadtemplates()

        if defaultinstrument is not None:
            try:
                self.instrumentselect.current = [i[0] for i in ilist].index(defaultinstrument)
                self.instrumentvar.set(defaultinstrument)
            except:
                self.instrumentselect.current = 0

    def selectworkdir(self, e):
        workdir = filedialog.askdirectory(initialdir='.', title='Select working directory')
        
        if len(workdir):
            self.workdir.set(workdir)
            print('workdir set to', workdir)
            self.parent.onevent((MSG.SETVAR,'workdir',workdir))


    def setstate(self, connstate : bool):
        self.isconnected = connstate

        self.btnconnect.config(text = 'Disconnect' if connstate else 'Connect')

        if connstate:
            self.ipaddressentry.config(state='disable')
            self.instrumentselect.config(state='disabled')
        else:
            self.ipaddressentry.config(state='normal')
            self.instrumentselect.config(state='normal')       
    
    def loadtemplates(self):
        self.mconfigs = get_templates(_MEASUREMENT_PATH, _TEMPLATETYPE_MEASUREMENT)
        self.mcfgselect['values'] = [k for k in self.mconfigs.keys()]
        self.eutconfigs = get_templates(_EUT_PATH, _TEMPLATETYPE_EUT)
        self.eutcfgselect['values'] = [k for k in self.eutconfigs.keys()]

class EUTFrame(ttk_b.Frame):
    def __init__(self, parent):
        super().__init__(parent)

class PlotFrame(ttk_b.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.point = None
        self.measurement = None
        self.peaklist = []                      
        self.fig = plt.Figure(figsize=(14, 7), dpi=100)
        self.ax = self.fig.add_subplot()

        # Create a Matplotlib figure and plot        
        log = True
        if log:
            self.ax.set_xscale("log")       
        
        # Create a canvas and add the figure to it
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        #self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=4, sticky='NSEW')
        self.canvas.get_tk_widget().pack(expand=True, fill='both')
        toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        toolbar.update()
        #toolbar.grid(row=1, column=0, columnspan=4, sticky='NSEW')
        toolbar.pack(expand=True, fill='x')
        self.canvas.mpl_connect("key_press_event", lambda event: print(f"you pressed {event.key}"))
        self.canvas.mpl_connect("button_press_event", lambda event: print(f"{event}"))
        #self.canvas.mpl_connect("key_press_event", key_press_handler)
        #self.columnconfigure(0, weight=1)
        #self.rowconfigure(0, weight=1)

        '''self.testentry = ttk_b.Entry(self)
        self.testentry.grid(row=3,column=0)
        self.btn = ttk_b.Button(self, text='test', command=self.btnevent)
        self.btn.grid(row=4,column=0)
        '''
        self.pointframe = ttk_b.Frame(self)
        ttk_b.Label(self.pointframe, text='Add point',width=16, anchor='w').pack(side='left')
        self.pointentryf = ttk_b.Entry(self.pointframe, state='readonly')
        self.pointentryf.pack(side='left')
        self.pointentrys = ttk_b.Entry(self.pointframe, state='readonly')
        self.pointentrys.pack(side='left')
        self.btnaddpoint = ttk_b.Button(self.pointframe, text='Add', command=self.onaddpoint)
        self.btnaddpoint.pack(side='left')
        #self.pointframe.grid(row=2, column=0)
        self.pointframe.pack(expand=True, fill='x')

        self.tvframe = ttk_b.Frame(self)
        self.treeview = ttk_b.Treeview(self.tvframe,columns=('freq','qp','limit','margin'), selectmode=ttk_b.BROWSE)
        self.treeview.pack(side='left')
        self.treeview.column('#0',width=0, stretch='no', anchor='center')
        self.treeview.column('freq',anchor='center')
        self.treeview.column('qp',anchor='center')
        self.treeview.column('limit',anchor='center')
        self.treeview.column('margin',anchor='center')
        #self.treeview.heading('#0', text='File')
        self.treeview.heading('freq',text='Frequency [MHz]')
        self.treeview.heading('qp',text='QP')
        self.treeview.heading('limit',text='Limit')
        self.treeview.heading('margin',text='Margin')
        self.tvscroll = ttk.Scrollbar(self.tvframe, orient='vertical', command=self.treeview.yview)
        self.tvscroll.pack(side='left',fill='y')
        self.treeview.config(yscrollcommand=self.tvscroll.set)
        #self.tvframe.grid(row=3, column=0, columnspan=4, sticky='NSEW')
        self.tvframe.pack(expand=True, fill='both')

        self.btnmeasureqp = ttk_b.Button(self, text='Measure selected QP', command=self.measureqp)
        self.btnmeasureqp.pack()

        #for i in range(10):           
        #    tvi = self.treeview.insert('',ttk_b.END, iid=i, values=('abc','345','ert'))
        #    print(tvi, type(tvi))

    def getpeak(self, iid):
        for p in self.peaklist:
            if iid == p['iid']:
                return p
        return None

    def measureqp(self):
        if self.measurement is None:
            return
        item = self.treeview.focus()
        print('item:', item, 'len(item):', len(item))
        peak = self.getpeak(item)
        if peak is not None:                        
            peak['qpk'] = self.measurement.measureqp_thread(peak['freq'])
            self.updatepeakview()
            self.plotpeaks()

    def onaddpoint(self):
        if self.point is not None:            
            iid = str(round(self.point[0]/1000000,3))
            #self.peaklist.append([iid, self.point[0], self.point[1], None, None])            
            self.peaklist.append({'iid':iid, 'freq':self.point[0], 'pk':self.point[1], 'qpk':None, 'limit': None})            
            self.updatepeakview()
            self.plotpeaks()
            for i in self.peaklist:
                print(i)

    def updatepeakview(self):
        for i in self.treeview.get_children():
            self.treeview.delete(i)
        self.peaklist.sort(key = lambda x: x['freq'])
        for p in self.peaklist:
            MHz = round(p['freq']/1000000,3)
            self.treeview.insert('',ttk_b.END, iid=p['iid'], values=(MHz, p['qpk'], p['limit'], None))

    def btnevent(self):
        s = self.testentry.get()        
        print('set:', self.treeview.set(s))
        print('item:', self.treeview.item(s))
        self.treeview.set(s, 2, 'Test123')

    def plotpeaks(self):
        if len(self.peaklist):            
            if hasattr(self,'peakplot') and self.peakplot is not None:
                self.peakplot.remove()
            if hasattr(self,'qpeakplot') and self.qpeakplot is not None:
                self.qpeakplot.remove()
            peakx = [ i['freq'] for i in self.peaklist if i['qpk'] is None]
            peaky = [ i['pk'] for i in self.peaklist if i['qpk'] is None]            
            
            qpeakx = [ i['freq'] for i in self.peaklist if i['qpk'] is not None]
            qpeaky= [ i['qpk'] for i in self.peaklist if i['qpk'] is not None]
            
            self.peakplot = self.ax.scatter(peakx, peaky, color='blue', marker='x')
            if len(qpeaky):
                self.qpeakplot = self.ax.scatter(qpeakx, qpeaky, color='red', marker='^')
            print('peakplot:', self.peakplot)
            self.canvas.draw()            

    def plot(self, meas, title='title', xlim=(30_000_000,1_000_000_000), ylim=(0,60)):        
        
        if self.measurement is None:
            self.measurement = meas
        # Apply corrections to voltage readings
        #fclist = loadcorrection('tbaf1m.csv')
        #datax = meas["Frequency"]
        #data = applycorrection(meas["Sig_Level"], datax, fclist)

        # Clear the canvas before drawing the plot
        self.ax.clear()        

        #self.fig, self.ax = plt.subplots(1,1)
        #self.ax.set_facecolor((0.0,0.5,1.0,0.1))     # Assign background color
        self.ax.set_title(title)
        self.ax.set_xlabel('Frequency [Hz]')
        self.ax.set_ylabel('dBuV')

        self.fig.text(0.01,0.95,'notes:')
        self.ax.set_ylim(ylim)
        self.ax.set_xlim(xlim)
        self.ax.grid()

        mkfunc = lambda x, pos: '%.1f G' % (x * 1e-9) if x >= 1e9 else '%3.1f M' % (x * 1e-6) if x >= 1e6 else '%3.1f k' % (x * 1e-3)
        mkformatter = ticker.FuncFormatter(mkfunc)
        self.ax.xaxis.set_major_formatter(mkformatter)

        line = self.ax.plot(meas.xdata, meas.ydata, linewidth = 0.5, label = 'test')
        #line2 = self.ax.plot(meas.datax, [x-3 for x in meas.data], linewidth = 0.5, label = 'test')

        cursor = mplcursors.cursor(line)
        cursor.connect('add', self.onpointselect)
        
        #mplcursors.cursor(line2)
        '''if ref:
            axis.plot(ref.datax, ref.data, linewidth = 0.5, ls=':')
            
        if peaklist:            
            axis.scatter(peaklist[0] , peaklist[1], edgecolors='#e86231', facecolor='none')
        

        axis.set_title(title)
        axis.set_xlabel(xlabel)
        axis.set_ylabel(ylabel)
        axis.grid(True)
        '''
        # Plot graph to canvas
        self.canvas.draw()
    
    def onpointselect(self, evt):
        self.point = (evt.target[0], evt.target[1])
        self.pointentryf.config(state = 'normal')
        self.pointentrys.config(state = 'normal')
        self.pointentryf.delete(0,END)
        self.pointentryf.insert(0,str(self.point[0]))
        self.pointentrys.delete(0,END)
        self.pointentrys.insert(0,str(self.point[1]))
        self.pointentryf.config(state = 'readonly')
        self.pointentrys.config(state = 'readonly')

class ConfigView(ttk_b.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.nb = ttk_b.Notebook(self, width=400)
        self.nb.onevent = lambda evt: parent.onevent(evt)   #make nb forward events
        self.measureframe = MeasureFrame(self.nb)
        self.meascfgedit = ConfigEditor(self.nb, template=None)
        self.eutcfgedit = ConfigEditor(self.nb, template=None)
        self.nb.add(self.measureframe, text='Measure')
        self.nb.add(self.eutcfgedit, text='EUT config')
        self.nb.add(self.meascfgedit, text='Measurement config')
        #self.nb.grid(column=0, row=1, rowspan=2, padx=10, pady=10, sticky='NSEW')
        self.nb.pack(expand=True, fill='both')
        self.columnconfigure(1,weight=1)

    def updatestate(self, state):
        self.measureframe.updatestate(state)

    def updateeuttemplate(self, template):
        self.eutcfgedit.updateconfig(template)

    def updatemeasurementtemplate(self, template):
        self.meascfgedit.updateconfig(template)

    def get_eutconfig(self):
        return self.eutcfgedit.getdata()
    
    def get_measconfig(self):
        return self.meascfgedit.getdata()
    
    def isvalid(self):
        return self.eutcfgedit.isvalid() and self.meascfgedit.isvalid()

    #def update_eutcfg(self, path):
    #    self.meascfgedit. 
    #def update_mcfg(self, path):


class MeasurementState(IntEnum):
    DISABLED = auto()
    READY = auto()
    RUNNING = auto()
    DONE = auto()

class MeasureFrame(ttk_b.Frame):
    
    def __init__(self, parent):
        super().__init__(parent)
        #self.measname.trace_add('write', lambda *_: parent.onevent( ('setvar','measname',self.measname.get()))) #changed to validate function
        
        #ttk_b.Label(self, text='Measurement name').grid(row=0, column=0, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD)
        #ttk_b.Entry(self, textvariable=self.measname, validate='focusout', validatecommand=lambda : parent.onevent((MSG.SETVAR,'measname',self.measname.get()))).grid(row=0, column=1, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD)
        self.measname = EntryFrame(self, 'measname', 'Measurement Name', '', parent)
        self.measname.pack()

        self.measurebtn = ttk_b.Button(self, text='measure', command = lambda : parent.onevent((MSG.MEASURE,)))
        self.measurebtn.pack()
        #self.measurebtn = ttk_b.Button(self, text='Start Measurement', command = self.onbtn)
        #self.measurebtn.grid(column=1, row=1)
        self.updatestate(MeasurementState.DISABLED)    

    def updatestate(self, state: MeasurementState):
        match state:
            case MeasurementState.DISABLED:                
                self.measurebtn.config(text='Start Measurment', state='disabled')
            case MeasurementState.READY:
                self.measurebtn.config(text='Start Measurment', state='enabled')
            case MeasurementState.RUNNING:
                self.measurebtn.config(text='Stop Measurment')
            case MeasurementState.DONE:
                self.measurebtn.config(text='Save Measurment')

class _MatchBreak(Exception): pass

class MeasureWindow(ttk_b.Window, EventHandler):

    def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        ttk_b.Window.__init__(self, **kwargs)
        EventHandler.__init__(self)
        self.vars = {}
        self.instrument = None
        self.mcfgpath = None
        self.eutcfgpath = None        
        self.measurement = None
        self.measstate = MeasurementState.DISABLED
        self.msgqueue = queue.SimpleQueue()
        self.savedata = {}
        self.instrumentlist = load_instruments()

        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=1)
        self.columnconfigure(3,weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.tb = ToolBar(self,'192.168.1.70', ilist = self.instrumentlist)
        self.tb.grid(column=0, row=0, columnspan=4, sticky='NSEW')        

        self.plotframe = PlotFrame(self)
        self.plotframe.grid(column=1, row=1, columnspan=3, rowspan=2, sticky='NSEW')        

        self.cfgview = ConfigView(self)
        self.cfgview.grid(column=0, row=1, rowspan=2, padx=10, pady=10, sticky='NSEW')        
        #self.rowconfigure(3, weight=1)
        self.after(500, self.ontimer)        

    def getinstrument(self, name):        
        try:
            index = [i[0] for i in self.instrumentlist].index(name)
            return self.instrumentlist[index][1]
        except:
            return None

    def ready(self):
        if self.mcfgpath is None:            
            return False
        if 'workdir' not in self.vars:            
            return False
        if self.eutcfgpath is None:
            return False
        if self.instrument is None:
            return False
        return True

    def ontimer(self):

        try:            
            match self.measstate:            
                case MeasurementState.DISABLED:
                    if self.ready():
                        self.measstate = MeasurementState.READY
                        print('ready')                
                case MeasurementState.READY:
                    pass
                case MeasurementState.RUNNING:
                    while not self.msgqueue.empty():
                        self.onevent(self.msgqueue.get())
                case MeasurementState.DONE:
                    pass
        except _MatchBreak:
            pass
        
        self.cfgview.updatestate(self.measstate)
        self.after(500, self.ontimer)
        
    def savemeasurement(self):    
        
        self.savedata['type'] = 'result'
        self.savedata['name'] = self.vars.get('measname','undefined')
        self.savedata['time'] = time.strftime('%y%m%d%H%M')
        self.savedata['comment'] = 'testcomment'        
        self.savedata['eutconfig'] = self.cfgview.get_eutconfig()
        self.savedata['ydata'] = self.measurement.ydata
        self.savedata['xdata'] = self.measurement.xdata
        
        fname = self.savedata['time'] + '_' + self.savedata['name'] + '.json'
        with open(Path(self.vars['workdir']) / fname, 'w') as fout:
            fout.write(json.dumps(self.savedata, indent=4))

        return True

    @eventhandler((MSG.CONNECT,))
    def onevent_connect(self, evt, inst, ip):
        
        instrumentclass = self.getinstrument(self.vars.get('instrumentname', ''))
        self.instrument = instrumentclass()
        if self.instrument.connect(self.tb.ipaddress.get()):                
            self.tb.setstate(True)
        else:
            print('connect failed')
        return True
    
    @eventhandler((MSG.DISCONNECT,))
    def onevent_disconnect(self, evt):
        self.instrument.disconnect()
        self.instrument = None
        self.tb.setstate(False)
        return True
    
    @eventhandler((MSG.SETMEASTEMPLATE,))
    def onevent_setmeastemplate(self, evt, name, path):
        self.mcfgpath = path
        templ = load_template(path, _TEMPLATETYPE_MEASUREMENT)
        if templ is not None:
            self.meastemplate = Measurement.modifytemplate(templ[_TEMPLATE_KEY])                    
            self.cfgview.updatemeasurementtemplate(self.meastemplate)
        return True
    
    @eventhandler((MSG.SETEUTTEMPLATE,))
    def onevent_seteuttemplate(self, evt, name, path):
        self.eutcfgpath = path
        tmpl = load_template(path, _TEMPLATETYPE_EUT)
        if tmpl is not None:                    
            self.cfgview.updateeuttemplate(tmpl[_TEMPLATE_KEY])
        return True
    
    @eventhandler((MSG.SETVAR,))
    def onevent_setvar(self, evt, varname, value):
        self.vars[varname] = value
        print(varname, value)
        return True
    
    @eventhandler((MSG.MEASURE,))
    def onevent_measure(self, evt, *args):

        match self.measstate:
            case MeasurementState.DISABLED:
                pass #this should not be possible
            case MeasurementState.READY:
                if self.cfgview.isvalid():
                    self.measurement = Measurement(self.instrument)
                    meascfg = (self.cfgview.get_measconfig())
                    self.savedata['measurementconfig'] = meascfg                            
                    self.measurement.setconfig(meascfg)                
                    #self.measurement = Measurement()
                    #self.measurement.loadconfig(self.mcfgpath)
                    self.measurement.startmeasurement(msgqueue = self.msgqueue)
                    self.measstate = MeasurementState.RUNNING                         
                else:
                    Messagebox.show_error('Some of the values in EUT config or Measurement config\nare invalid', title='Error', alert=True, parent=self)
            case MeasurementState.DONE:
                self.measstate = MeasurementState.READY
                self.savemeasurement()
        return True
    
    @eventhandler((MSG.LOG,))
    def onevent_log(self, evt, level, msg):
        match level:
            case 'debug':
                logger.debug(msg)
            case 'info':
                logger.info(msg)
            case 'error':
                logger.error(msg)

    @eventhandler((MSG.THREAD,))
    def onevent_threadmsg(self, evt, msgtype, data):
        self.processthreadmsg(msgtype, data)
        return True        
    
    def processthreadmsg(self, type, data=None):
        if type == THREADMSG.DATA:
            self.plotframe.plot(self.measurement)
        if type == THREADMSG.DONE:
            self.measstate = MeasurementState.DONE

