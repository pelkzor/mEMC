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
from gui import *

# Dictionary of possible themes (Refer to ttkbootstrap manpage)
theme = {                
    "default"   : "superhero",
    "dark"      : "darkly",
    "light"     : "journal"
}

def printWelcomeScreen():
    print("╔═════════════════════════════════════╗")
    print("║     ███████╗███╗   ███╗ ██████╗     ║")
    print("║     ██╔════╝████╗ ████║██╔════╝     ║")
    print("║     █████╗  ██╔████╔██║██║          ║")
    print("║     ██╔══╝  ██║╚██╔╝██║██║          ║")
    print("║     ███████╗██║ ╚═╝ ██║╚██████╗     ║")
    print("║     ╚══════╝╚═╝     ╚═╝ ╚═════╝     ║")
    print("║     ── mEMC Test Application ──     ║")
    print("╚═════════════════════════════════════╝")

def exitapp():
    plt.cla()
    plt.close()
    rbrowser.destroy()
    window.destroy()


# Generate GUI window
window = MeasureWindow(themename = theme["default"])


window.title('mEMC Test')
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
desired_width = 1920
desired_height = 1080

window_width = min(desired_width, screen_width)
window_height = min(desired_height, screen_height)

# Center the window
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

window.geometry(f"{window_width}x{window_height}+{x}+{y}")
#window.attributes("-fullscreen", True)
# Make the window resizable
window.resizable(1,1)
rbrowser = ResultBrowser()
rbrowser.title("mEMC Results")
window.protocol("WM_DELETE_WINDOW",exitapp)         # Install window close routine

printWelcomeScreen()
window.mainloop()