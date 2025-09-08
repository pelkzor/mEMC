#External imports
import tkinter as tk
from tkinter import ttk, filedialog

import ttkbootstrap as ttk_b
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox

from secrets import token_hex
import json
import time
import queue
import logging
import os

import numpy as np
from scipy.signal import find_peaks
from enum import IntEnum, auto

from pathlib import Path

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.ticker import LinearLocator
import mplcursors
from matplotlib.backend_bases import key_press_handler

#Internal imports
from utils.message import *
from utils.reportgenerator import generate_report
from config import LOCAL_IP

from instruments import measurement
from instruments.measurement import Measurement
#from DSA832_instrument import DSA832
#from simulator_instrument import Simulator

logger = logging.getLogger(__name__)
logging.basicConfig(filename='emc.log', encoding='utf-8', level=logging.ERROR)
logger.error('Starting')

_UNDEFINED_ENTRY = 'NA'

_DEFAULT_PAD = 5

_MEASUREMENT_PATH = './config/meastempl'
_EUT_PATH = './config//euttempl'
_CORRECTION_PATH = './config//correction'
_STANDARD_PATH = './config//standards'

_TEMPLATETYPE_MEASUREMENT = 'measurementtemplate'
_TEMPLATETYPE_EUT = 'euttemplate'
_TEMPLATETYPE_CORRECTION = 'correctiontemplate'
_TEMPLATETYPE_STANDARD = 'standardtemplate'
_TEMPLATE_KEY = 'template'
_CORRECTION_KEY = 'correction'
_STANDARD_KEY = 'limits'

#Set to true for quicker debug cycles
#Preselects all dropdowns
SIMULATOR_MODE = os.environ.get('SIMULATOR_MODE', 'False') == 'True'

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
    import inspect
    for fname in filenames:
        try:
            mod = load_module(fname, token_hex(16))
            if hasattr(mod, "Instrument"):
                inst = mod.Instrument
                name = inst.name
                ilist.append((name, inst))
        except Exception as e:
            print(fname, f'failed to load because: {e}')
    #extract loaded instrument names and display in terminal
    names = [name for name, _ in ilist]
    result = "Loaded instruments: " +", ".join(names)
    print(result)
    return ilist

def get_correctionconfigs():
    filenames = list(Path(_CORRECTION_PATH).glob('*.json'))    
    correctionfactors = {}

    for fname in filenames:
        try:
            with open(fname,'r') as f:
                cfg = json.loads(f.read())            
                if cfg['type'] == 'correctiontemplate':
                    correctionfactors[cfg['name']] = fname.resolve()
        except Exception as e:
            print(e)
    
    return correctionfactors

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
    
    def set_state(self, state):
        self.entry.config(state=state)

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
            tip = tip + 'Value is allowed to be empty "NA"'

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

    def __init__(self, parent, defaultipaddress=LOCAL_IP, ilist=None, defaultinstrument=None):
        super().__init__(parent)        
        self.isconnected = False
        self.parent = parent

        ttk_b.Label(self, text='Instrument',width=16, anchor='e').grid(row=0, column=0, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD,sticky='EW')
        
        self.instrumentvar = ttk_b.StringVar()
        self.instrumentvar.trace_add('write', lambda *_: parent.onevent((MSG.SETVAR,'instrumentname',self.instrumentvar.get()))) 
        self.instrumentselect = ttk_b.Combobox(self, values=[i[0] for i in ilist], textvariable=self.instrumentvar, state='readonly', width=16)        
        self.instrumentselect.grid(row=0, column=1, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW') 

        ttk_b.Label(self, text='IP address [:port]',width=16, anchor='e').grid(row=1, column=0, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW')
        
        self.ipaddressvar = ttk_b.StringVar()
        self.ipaddressvar.trace_add('write', lambda *_: parent.onevent((MSG.SETVAR,'ipaddress',self.ipaddressvar.get()))) #changed to validate function
        self.ipaddressvar.set(defaultipaddress)
        self.ipaddressentry = ttk_b.Entry(self, textvariable=self.ipaddressvar, width=16)
        self.ipaddressentry.grid(row=1, column=1, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW')

        self.btnconnect = ttk_b.Button(self, text='Connect', command = lambda : parent.onevent((MSG.DISCONNECT if self.isconnected else MSG.CONNECT,self.instrumentvar.get(),self.ipaddressvar.get())))
        self.btnconnect.grid(row=2, column=0, columnspan=2, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='NSEW')

        ttk_b.Label(self, text='Measurement template',width=25, anchor='e').grid(row=0, column=2, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD)
        self.mcfg = ttk_b.StringVar()
        self.mcfgselect = ttk_b.Combobox(self, textvariable=self.mcfg, state='readonly', width=16)
        self.mcfgselect.bind('<<ComboboxSelected>>', lambda _: parent.onevent((MSG.SETMEASTEMPLATE,self.mcfg.get(),self.mconfigs[self.mcfg.get()])) )
        self.mcfgselect.grid(row=0, column=3, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW')

        ttk_b.Label(self, text='EUT Template',width=25, anchor='e').grid(row=0, column=4, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD)
        self.eutcfg = ttk_b.StringVar()
        self.eutcfgselect = ttk_b.Combobox(self, textvariable=self.eutcfg, state='readonly', width=16)
        self.eutcfgselect.bind('<<ComboboxSelected>>', lambda _: parent.onevent((MSG.SETEUTTEMPLATE,self.eutcfg.get(),self.eutconfigs[self.eutcfg.get()])) )
        self.eutcfgselect.grid(row=0, column=5, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW')

        ttk_b.Label(self, text='Standard',width=16, anchor='e').grid(row=0, column=6, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD)
        self.standardcfg = ttk_b.StringVar()
        self.standardcfgselect = ttk_b.Combobox(self, textvariable=self.standardcfg, state='readonly', width=16)
        self.standardcfgselect.bind('<<ComboboxSelected>>', lambda _: parent.onevent((MSG.SETSTANDARD,self.standardcfg.get(),self.standards[self.standardcfg.get()])) )
        self.standardcfgselect.grid(row=0, column=7, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW')

        ttk_b.Label(self, text='Correction factor',width=25, anchor='e').grid(row=0, column=8, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD)
        self.correctioncfg = ttk_b.StringVar()
        self.correctioncfgselect = ttk_b.Combobox(self, textvariable=self.correctioncfg, state='readonly', width=16)
        self.correctioncfgselect.bind('<<ComboboxSelected>>', lambda _: parent.onevent((MSG.SETCORRECTION,self.correctioncfg.get(),self.correctionfactors[self.correctioncfg.get()])) )
        self.correctioncfgselect.grid(row=0, column=9, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW')

        ttk_b.Label(self, text='Working directory',width=25, anchor='e').grid(row=1, column=2, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD)
        self.workdir = ttk_b.StringVar()
        style = ttk_b.Style()
        style.configure('Placeholder.TEntry', foreground='grey')
        self.workdir.set("Select work directory...")          
        self.workdirentry = ttk_b.Entry(self, textvariable=self.workdir, state='readonly', width=32, style='Placeholder.TEntry')
        self.workdirentry.bind('<1>', self.selectworkdir)
        self.workdirentry.grid(row=1, column=3, columnspan=2, padx=_DEFAULT_PAD, pady=_DEFAULT_PAD, sticky='EW')

        self.loadtemplates()

        self.config_comboboxes = [
            self.instrumentselect,
            self.mcfgselect,
            self.eutcfgselect,
            self.standardcfgselect,
            self.correctioncfgselect,
            self.workdirentry
        ]

        if SIMULATOR_MODE:
            # select simulator instrument
            if len(ilist) > 0:
                sim_names = [i[0] for i in ilist if 'simulator' in i[0].lower()]
                if sim_names:
                    sim_index = [i[0].lower() for i in ilist].index(sim_names[0].lower())
                    self.instrumentselect.current = sim_index
                    self.instrumentvar.set(ilist[sim_index][0])
                else:
                    self.instrumentselect.current = 0
                    self.instrumentvar.set(ilist[0][0])

            # autoset mcfgselect
            if len(self.mcfgselect['values']) > 0:
                self.mcfgselect.current = 0
                if self.mcfgselect['values']:
                    self.mcfg.set(self.mcfgselect['values'][0])
                    
            # autoset eutconfig
            if len(self.eutconfigs) > 0:
                self.eutcfgselect.current = 0
                if self.eutcfgselect['values']:
                    self.eutcfgselect.set(self.eutcfgselect['values'][0])

            if len(self.standards) > 0:
                self.standardcfgselect.current = 0
                if self.standardcfgselect['values']:
                    self.standardcfgselect.set(self.standardcfgselect['values'][0])
                    
            if len(self.correctionfactors) > 0:
                self.correctioncfgselect.current = 0
                if self.correctioncfgselect['values']:
                    self.correctioncfgselect.set(self.correctioncfgselect['values'][0])
            
            # simulator work directory
            # Set working directory to script root folder/simulator
            script_root = os.path.dirname(os.path.abspath(__file__))
            sim_dir = os.path.join(script_root, "simulator")
            os.makedirs(sim_dir, exist_ok=True)  # Create if not exists
            self.workdir.set(sim_dir)
            self.workdirentry.configure(style='TEntry')
            self.parent.onevent((MSG.SETVAR,'workdir',sim_dir))
        
        else:
            results_dir = os.environ.get('WORKING_DIR')
            if results_dir:
                os.makedirs(results_dir, exist_ok=True)
                self.workdir.set(results_dir)
                self.workdirentry.configure(style='TEntry')
                self.parent.onevent((MSG.SETVAR, 'workdir', results_dir))

    def selectworkdir(self, e):
        workdir = filedialog.askdirectory(initialdir='.', title='Select working directory')
        
        if len(workdir):
            self.workdir.set(workdir)
            self.workdirentry.configure(style='TEntry')
            print('workdir set to', workdir)
            self.parent.onevent((MSG.SETVAR,'workdir',workdir))


    def setstate(self, connstate : bool):
        self.isconnected = connstate

        self.btnconnect.config(text = 'Disconnect' if connstate else 'Connect')

        if connstate:
            self.ipaddressentry.config(state='disabled')
            self.instrumentselect.config(state='disabled')
        else:
            self.ipaddressentry.config(state='normal')
            self.instrumentselect.config(state='normal')       
    
    def loadtemplates(self):
        self.mconfigs = get_templates(_MEASUREMENT_PATH, _TEMPLATETYPE_MEASUREMENT)
        self.mcfgselect['values'] = [k for k in self.mconfigs.keys()]
        self.eutconfigs = get_templates(_EUT_PATH, _TEMPLATETYPE_EUT)
        self.eutcfgselect['values'] = [k for k in self.eutconfigs.keys()]
        self.correctionfactors = get_templates(_CORRECTION_PATH, _TEMPLATETYPE_CORRECTION)
        self.correctioncfgselect['values'] = [k for k in self.correctionfactors.keys()]
        self.standards = get_templates(_STANDARD_PATH, _TEMPLATETYPE_STANDARD)
        self.standardcfgselect['values'] = [k for k in self.standards.keys()]

    def update_combobox_states(self, state):
            if state == MeasurementState.RUNNING:
                for cb in self.config_comboboxes:
                    cb.config(state='disabled')
            else:
                for cb in self.config_comboboxes:
                    cb.config(state='readonly')

class EUTFrame(ttk_b.Frame):
    def __init__(self, parent):
        super().__init__(parent)

class PlotFrame(ttk_b.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.point = None
        self.measurement = None
        self.peaklist = []      
        self.fig = plt.Figure(figsize=(5, 7), dpi=100)
        self.fig = plt.Figure()

        self.ax = self.fig.add_subplot()
        # Create a Matplotlib figure and plot        
        # log = True
        # if log:
        #     self.ax.set_xscale("log")       
        xlim=(0,1_000_000_000)
        ylim=(0,125)
        # uncomment to add padding to x axis
        # x_padding = (xlim[0]+xlim[1]) * 0.01
        # xlim = (xlim[0] - x_padding, xlim[1] + x_padding)
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.ax.set_xlabel('Frequency [Hz]')
        self.ax.set_ylabel('dBµV')
        self.ax.grid()
        
        # Create a canvas and add the figure to it
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        
        toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        toolbar.update()
        self.canvas.mpl_connect("key_press_event", lambda event: print(f"you pressed {event.key}"))
        self.canvas.mpl_connect("button_press_event", lambda event: print(f"{event}"))

        self.pointframe = ttk_b.Frame(self)
        ttk_b.Label(self.pointframe, text='Add point', width=16, anchor='w').pack(side='left')
        self.pointentryf = ttk_b.Entry(self.pointframe, state='readonly')
        self.pointentryf.pack(side='left')
        self.pointentrys = ttk_b.Entry(self.pointframe, state='readonly')
        self.pointentrys.pack(side='left')
        self.btnaddpoint = ttk_b.Button(self.pointframe, text='Add', command=self.onaddpoint)
        self.btnaddpoint.pack(side='left')

        self.tvframe = ttk_b.Frame(self)
        self.treeview = ttk_b.Treeview(self.tvframe, columns=('freq','qp','limit','margin'), selectmode=ttk_b.BROWSE)
        self.treeview.pack(side='left', fill='both', expand=True)
        self.treeview.column('#0', width=0, stretch='no', anchor='center')
        self.treeview.column('freq', anchor='center')
        self.treeview.column('qp', anchor='center')
        self.treeview.column('limit', anchor='center')
        self.treeview.column('margin', anchor='center')
        self.treeview.heading('freq', text='Frequency [MHz]')
        self.treeview.heading('qp', text='QP')
        self.treeview.heading('limit', text='Limit')
        self.treeview.heading('margin', text='Margin')
        self.tvscroll = ttk.Scrollbar(self.tvframe, orient='vertical', command=self.treeview.yview)
        self.tvscroll.pack(side='left', fill='y')
        self.treeview.config(yscrollcommand=self.tvscroll.set)

        self.btnmeasureqp = ttk_b.Button(self, text='Measure selected QP', command=self.measureqp, width=20)

        # Grid layout, more weight = more space in height
        self.grid_rowconfigure(0, weight=3)  # Canvas gets most space
        self.grid_rowconfigure(1, weight=0)   # Toolbar
        self.grid_rowconfigure(2, weight=0)   # Point frame
        self.grid_rowconfigure(3, weight=1)   # Treeview gets remaining space
        self.grid_rowconfigure(4, weight=0)   # Button
        self.grid_columnconfigure(0, weight=1)  # Single column that expands

        # Place widgets in grid
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        toolbar.grid(row=1, column=0, sticky='ew', padx=5)
        self.pointframe.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        self.tvframe.grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.btnmeasureqp.grid(row=4, column=0, padx=5, pady=5, sticky='w')

        # Minimum sizes to prevent widgets from becoming too small
        self.tvframe.config(width=400, height=200)

    def remove_limit(self):
        if hasattr(self, 'limit_plot') and self.limit_plot is not None:
            self.limit_plot.remove()
            self.limit_plot = None
            self.canvas.draw()

    def add_limit(self, frequencies, limit):
        # Remove previous limit_plot if it exists
        self.remove_limit()
        # Draw limit over plot width
        xmin, xmax = self.ax.get_xlim()
        frequencies[0] = xmin
        frequencies[-1] = xmax
        # Add new limit_plot and keep reference
        self.limit_plot, = self.ax.plot(frequencies, limit, color='green', linewidth=2)
        self.canvas.draw()

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
            # Debugging print
            # print(f"After measureqp, peaklist: {self.peaklist}")

    def onaddpoint(self):
        if self.point is not None:
            iid = str(round(self.point[0]/1000000,3))
            limit_val = None
            # Calculate limit and margin for this frequency if limit_plot exists
            if hasattr(self, 'limit_plot') and self.limit_plot is not None:
                limit_x = self.limit_plot.get_xdata()
                limit_y = self.limit_plot.get_ydata()
                limit_val = float(np.interp(self.point[0], limit_x, limit_y))
            self.peaklist.append({
                'iid': iid,
                'freq': self.point[0],
                'pk': self.point[1],
                'qpk': None,
                'limit': limit_val,
                'margin': None
            })
            self.updatepeakview()
            self.plotpeaks()
            for i in self.peaklist:
                print("Adding to peaklist")
                print(i)

    def updatepeakview(self):
        for i in self.treeview.get_children():
            self.treeview.delete(i)
        self.peaklist.sort(key = lambda x: x['freq'])
        for p in self.peaklist:
            MHz = f"{(p['freq'] / 1000000):.2f}"
            qpk = f"{p['qpk']:.2f}" if p['qpk'] is not None else "Not measured"
            limit = f"{p['limit']:.2f}" if p['limit'] is not None else "Not measured"
            
            margin = None
            if p['qpk'] is not None and p['limit'] is not None:
                margin = p['limit'] - p['qpk']
                p['margin'] = margin
                margin = f"{margin:.2f}"
            else:
                margin = ""
            
            self.treeview.insert('', ttk_b.END, iid=p['iid'], 
                                values=(MHz, qpk, limit, margin, None))

    def cleanpeakview(self):
        for i in self.treeview.get_children():
            self.treeview.delete(i)
        self.peaklist.clear()

    def btnevent(self):
        s = self.testentry.get()        
        print('set:', self.treeview.set(s))
        print('item:', self.treeview.item(s))
        self.treeview.set(s, 2, 'Test123')

    def plotpeaks(self):
        if len(self.peaklist):            
            peakx = [ i['freq'] for i in self.peaklist if i['qpk'] is None]
            peaky = [ i['pk'] for i in self.peaklist if i['qpk'] is None]            
            
            qpeakx = [ i['freq'] for i in self.peaklist if i['qpk'] is not None]
            qpeaky= [ i['qpk'] for i in self.peaklist if i['qpk'] is not None]
            
            # Color qpeaks red if exceeding limit, green otherwise
            # qpeakcolors = [
            #     'red' if i['qpk'] is not None and i['limit'] is not None and i['qpk'] > i['limit'] else 'green'
            #     for i in self.peaklist if i['qpk'] is not None
            # ]
            self.peakplot = self.ax.scatter(peakx, peaky, color='blue', marker='x')
            if len(qpeaky):
                self.qpeakplot = self.ax.scatter(qpeakx, qpeaky, c='darkblue', marker='o')
            #print('peakplot:', self.peakplot)
            self.canvas.draw()

    def setlimit(self, standardtemplate):
        self.standardtemplate = standardtemplate

    def drawlimitplot(self):
        if self.standardtemplate is None:
            return
        # Add standard limits to plot
        limitstemplate = self.standardtemplate["limits"]["value"]
        frequencies = []
        limits = []

        for entry in limitstemplate:
            min_f = entry.get("min_freq", 0)
            max_f = entry.get("max_freq", 1_000_000_000)
            limit = entry.get("limit", 0)
            frequencies.extend([min_f, max_f if max_f is not None else 1_000_000_000])
            limits.extend([limit, limit])

        self.add_limit(frequencies, limits)           

    def plot(self, meas, title='title', xlim=(0,1_000_000_000), ylim=(0,125)):        
        
        if self.measurement is None:
            self.measurement = meas

        # Remove axes before clearing to avoid exception
        self.remove_limit() 
        if hasattr(self,'exceedslimitplot') and self.exceedslimitplot is not None:
            self.exceedslimitplot.remove()
        if hasattr(self,'peakplot') and self.peakplot is not None:
                self.peakplot.remove()
        if hasattr(self,'qpeakplot') and self.qpeakplot is not None:
                self.qpeakplot.remove()
        # Clear the canvas before drawing the plot
        self.ax.clear()        
       
        self.ax.set_title(title)
        self.ax.set_xlabel('Frequency [Hz]')
        self.ax.set_ylabel('dBµV')

        #self.fig.text(0.01,0.95,'notes:')
        self.ax.set_ylim(ylim)
        # Load x limits from measurement config
        if meas.meascfg is not None:
            xlim = meas.meascfg['fstart'], meas.meascfg['fstop']


        # Add some padding to the min and max x values to improve readability
        # x_padding = (xlim[0]+xlim[1]) * 0.01
        # xlim = (xlim[0] - x_padding, xlim[1] + x_padding)
        self.ax.set_xlim(xlim)
        self.ax.grid()


        mkfunc = lambda x, pos: '%.1f G' % (x * 1e-9) if x >= 1e9 else '%3.1f M' % (x * 1e-6) if x >= 1e6 else '%3.1f k' % (x * 1e-3)
        mkformatter = ticker.FuncFormatter(mkfunc)
        self.ax.xaxis.set_major_formatter(mkformatter)

        line = self.ax.plot(meas.xdata, meas.ydata, linewidth=0.5)
        self.ax.xaxis.set_major_locator(LinearLocator(numticks=6))

        self.drawlimitplot()

        self.cursor = mplcursors.cursor(line)
        self.cursor.connect('add', self.onpointselect)
        self.annotation = None
        self.canvas.mpl_connect("button_press_event", self._on_canvas_click)

        @self.cursor.connect("add")
        def on_add(sel):
            x, y = sel.target
            # Formatting of the textbox which appears when you click the graph
            sel.annotation.set(text=f"x={x/1e6:.1f} M\ny={y:.1f}")
            
            sel.annotation.get_bbox_patch().set(
                boxstyle="round,pad=0.5", 
                facecolor="lightyellow", 
                alpha=0.9
            )
            sel.annotation.arrow_patch.set(
                arrowstyle="simple",
                  fc="orange",
                  ec="orange",
                  alpha=0.9,
                  connectionstyle="arc3,rad=0.2"
                  )

        # After plotting meas.xdata, meas.ydata and drawing the limit plot:
        if hasattr(self, 'limit_plot') and self.limit_plot is not None:
            # Group contiguous indices into regions
            limit_x = self.limit_plot.get_xdata()
            limit_y = self.limit_plot.get_ydata()
            interp_limit = np.interp(meas.xdata, limit_x, limit_y)

            ydata = np.array(meas.ydata)
            xdata = np.array(meas.xdata)

            # Find all peaks
            peak_indices, _ = find_peaks(ydata)

            # Mask of samples above the interpolated limit
            above_mask = ydata > interp_limit

            highlight_x = []
            highlight_y = []

            i = 0
            while i < len(ydata):
                if above_mask[i]:
                    # Start of a region
                    region_indices = []
                    while i < len(ydata) and above_mask[i]:
                        region_indices.append(i)
                        i += 1
                    # Find peaks inside this region
                    region_peaks = [p for p in peak_indices if p in region_indices]
                    if region_peaks:
                        # Pick the highest peak in this region
                        best_peak = max(region_peaks, key=lambda p: ydata[p])
                        highlight_x.append(xdata[best_peak])
                        highlight_y.append(ydata[best_peak])
                else:
                    i += 1

            # Plot only the selected peaks
            self.exceedslimitplot = self.ax.scatter(highlight_x, highlight_y,
                                                    color='red', marker='o', facecolors='none')

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

    def on_right_click(self, event):
        for sel in self.cursor.selections:
            self.cursor.remove_selection(sel)
        self.canvas.draw()

    def _on_canvas_click(self, event):
        # Matplotlib uses button=3 for right-click
        if event.button == 3:
            self.on_right_click(event)

class ConfigView(ttk_b.Frame):

    def __init__(self, parent, toolbar=None):
        super().__init__(parent)
        self.nb = ttk_b.Notebook(self, width=400)
        self.nb.onevent = lambda evt: parent.onevent(evt)   #make nb forward events

        self.toolbar = toolbar
        self.measureframe = MeasureFrame(self.nb, self.toolbar)
        self.meascfgedit = ConfigEditor(self.nb, template=None)
        self.eutcfgedit = ConfigEditor(self.nb, template=None)
        self.correctionedit = ConfigEditor(self.nb, template=None)
        self.standardedit =  ConfigEditor(self.nb, template=None)
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

    def updatecorrectionfactor(self, factor):
        # TODO add to editor?
        self.correctionedit.updateconfig(factor)

    def updatestandard(self, standard):
        # TODO add to editor?
        self.standardedit.updateconfig(standard)

    def get_eutconfig(self):
        return self.eutcfgedit.getdata()
    
    def get_measconfig(self):
        return self.meascfgedit.getdata()
    
    def get_correction(self):
        return self.correctionedit.getdata()

    def get_standard(self):
        return self.standardedit.getdata()

    def isvalid(self):
        return self.eutcfgedit.isvalid() and self.meascfgedit.isvalid() and self.correctionedit.isvalid() and self.standardedit.isvalid()



class MeasurementState(IntEnum):
    DISABLED = auto()
    READY = auto()
    RUNNING = auto()
    DONE = auto()

class MeasureFrame(ttk_b.Frame):
    
    def __init__(self, parent, toolbar, plot_frame=None,):
        super().__init__(parent)

        self.toolbar = toolbar
        self.measname = EntryFrame(self, 'measname', 'Measurement Name', '', parent)
        self.measname.pack(pady=15)

        self.plot_frame = plot_frame

        self.measurebtn = ttk_b.Button(self, text='measure', command = lambda : parent.onevent((MSG.MEASURE,)))
        self.measurebtn.pack(pady=10)

        self.progress = ttk_b.Progressbar(self, mode='indeterminate', length=200)
        self.progress_label = ttk_b.Label(self, text='')

        self.updatestate(MeasurementState.DISABLED)    

    def updatestate(self, state: MeasurementState):
        match state:
            case MeasurementState.DISABLED:                
                self.measurebtn.config(text='Start Measurement', state='disabled')
                self.measname.set_state('disabled')
                self.hide_progress()
            case MeasurementState.READY:
                self.measurebtn.config(text='Start Measurement', state='enabled')
                self.measname.set_state('normal')
                self.hide_progress()
            case MeasurementState.RUNNING:
                self.measurebtn.config(text='Stop Measurement')
                self.measname.set_state('disabled')
                self.show_progress()
                self.progress.config(mode='indeterminate')
                self.progress.start(10)
            case MeasurementState.DONE:
                self.measurebtn.config(text='Save Measurement')
                self.measname.set_state('readonly')
                self.hide_progress()

        if hasattr(self.toolbar, 'update_combobox_states'):
            self.toolbar.update_combobox_states(state)
    
    def show_progress(self):
        if not self.progress.winfo_ismapped():
            self.progress.pack(pady=15)
            self.progress_label.pack()
    
    def hide_progress(self):
        self.progress.stop()
        if self.progress.winfo_ismapped():
            self.progress.pack_forget()
    
    def update_progress(self, progress):
        if self.progress['mode'] != 'determinate':
            self.progress.config(mode='determinate', maximum=100)
        
        self.progress['value'] = progress
        
        if progress >= 100:
            self.progress_label.config(text='Measurement complete!')
        else:
            self.progress_label.config(text=f'Measuring... {progress:.1f}%')

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
        self.rowconfigure(2, weight=2)

        self.tb = ToolBar(self, defaultipaddress=LOCAL_IP, ilist = self.instrumentlist)
        self.tb.grid(column=0, row=0, columnspan=4, sticky='NSEW')        

        self.plotframe = PlotFrame(self)
        self.plotframe.grid(column=1, row=1, columnspan=3, rowspan=2,sticky='NSEW')

        self.cfgview = ConfigView(self, self.tb) 
        self.cfgview.grid(column=0, row=1, rowspan=2, padx=10, pady=10, sticky='NSEW')        
        #self.rowconfigure(3, weight=1)

        if SIMULATOR_MODE:
            # fire events to get get into ready state
            self.onevent((MSG.SETMEASTEMPLATE, self.tb.mcfg.get(),self.tb.mconfigs[self.tb.mcfg.get()]))
            self.onevent((MSG.SETEUTTEMPLATE, self.tb.eutcfg.get(),self.tb.eutconfigs[self.tb.eutcfg.get()])) 
            self.onevent((MSG.SETSTANDARD, self.tb.standardcfg.get(),self.tb.standards[self.tb.standardcfg.get()])) 
            self.onevent((MSG.SETCORRECTION, self.tb.correctioncfg.get(),self.tb.correctionfactors[self.tb.correctioncfg.get()])) 
            self.onevent((MSG.SETVAR,'instrumentname',self.tb.instrumentvar.get()))
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
        #self.savedata['comment'] = 'testcomment' // Räcker väl med "Notes" som finns att lägga till i EUT-configen?        
        self.savedata['eutconfig'] = self.cfgview.get_eutconfig()
        self.savedata['ydata'] = self.measurement.ydata
        self.savedata['xdata'] = self.measurement.xdata

        if (hasattr(self, 'plotframe') and self.plotframe and 
            hasattr(self.plotframe, 'peaklist')):
            self.savedata['peaklist'] = self.plotframe.peaklist
            print(f"Saving {len(self.plotframe.peaklist)} peaks")
        else:
            self.savedata['peaklist'] = []
            print("Warning: No peaklist found to save")
        
        fname = self.savedata['time'] + '_' + self.savedata['name'] + '.json'
        json_path = Path(self.vars['workdir']) / fname
        with open(Path(self.vars['workdir']) / fname, 'w') as fout:
            fout.write(json.dumps(self.savedata, indent=4))
        pdf_path = json_path.with_suffix(".pdf")
        generate_report(json_path, pdf_path, figure=self.plotframe.fig)
        return True

    @eventhandler((MSG.CONNECT,))
    def onevent_connect(self, evt, inst, ip):
        
        instrumentclass = self.getinstrument(self.vars.get('instrumentname', ''))
        self.instrument = instrumentclass()
        if self.instrument.connect(self.tb.ipaddressvar.get()):                
            self.tb.setstate(True)
            print('connect successful')
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
    

    @eventhandler((MSG.SETCORRECTION,))
    def onevent_setcorrectionfactor(self, evt, name, path):
        self.correctionpath = path
        self.correctionname = name
        tmpl = load_template(path, _TEMPLATETYPE_CORRECTION)
        if tmpl is not None:            
            self.correctiontemplate = Measurement.modifycorrectiontemplate(tmpl[_CORRECTION_KEY])                    
            self.cfgview.updatecorrectionfactor(self.correctiontemplate)
        return True
    
    @eventhandler((MSG.SETSTANDARD,))
    def onevent_setstandard(self, evt, name, path):
        self.standardpath = path
        self.standardname = name
        tmpl = load_template(path, _TEMPLATETYPE_STANDARD)
        if tmpl is not None:            
            self.standardtemplate = Measurement.modifystandardtemplate(tmpl[_STANDARD_KEY])                    
            self.cfgview.updatestandard(self.standardtemplate)
            self.plotframe.setlimit(self.standardtemplate)
            self.plotframe.drawlimitplot()
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
                    self.plotframe.cleanpeakview()
                    self.measurement = Measurement(self.instrument)
                    meascfg = (self.cfgview.get_measconfig())
                    self.savedata['measurementconfig'] = meascfg                    
                    self.measurement.setconfig(meascfg)    
                    correction = (self.cfgview.get_correction())
                    self.measurement.setcorrectiondata(correction)
                    self.savedata['correction_factor'] = self.correctionname
                    self.savedata['standard_name'] = self.standardname
                    self.measurement.startmeasurement(msgqueue = self.msgqueue)
                    self.measstate = MeasurementState.RUNNING                         
                else:
                    Messagebox.show_error('Some of the values in EUT config or Measurement config\nare invalid', title='Error', alert=True, parent=self)
            case MeasurementState.DONE:
                self.measstate = MeasurementState.READY
                self.savemeasurement()
                self.result_browser.refresh_results()
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
            self.plotframe.plot(self.measurement, self.vars.get('measname',''))
        elif type == THREADMSG.PROGRESS:
            if hasattr(self.cfgview, 'measureframe') and hasattr(self.cfgview.measureframe, 'update_progress'):
                self.cfgview.measureframe.update_progress(data)
        elif type == THREADMSG.DONE:
            self.measstate = MeasurementState.DONE