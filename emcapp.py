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
window = ttk_b.Window(themename = theme["default"])
# Make the window resizable
window.resizable(1,1)
# Modify window for measure session
rbrowser = ResultBrowser()
measwnd = MeasureWindow()
rbrowser.protocol("WM_DELETE_WINDOW",rbrowser.destroy)
#plot_session(window)
# Install window close routine
window.protocol("WM_DELETE_WINDOW",exitapp)
# Run mainloop
window.mainloop()