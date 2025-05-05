import ttkbootstrap as ttk_b            # Import TTKBootstrap
from ttkbootstrap.constants import *
import json                             # Import json module
import os                               # For directory manipulation
from tkinter import scrolledtext        # Import tkinter module for scroll text box
from tkinter import *                   # Import all tkinter modules
from tkinter import filedialog          
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from miscgui import *
from resultbrowser import *


# Dictionary of possible themes (Refer to ttkbootstrap manpage)
theme = {                
    "default"   : "superhero",
    "dark"      : "darkly",
    "light"     : "journal"
}

def exitapp():
    plt.cla()
    plt.close()
    rbrowser.destroy()
    window.destroy()


# Generate GUI window

window = MeasureWindow(themename = theme["default"])
# Make the window resizable
window.resizable(1,1)
rbrowser = ResultBrowser()
window.protocol("WM_DELETE_WINDOW",exitapp)         # Install window close routine
window.mainloop()