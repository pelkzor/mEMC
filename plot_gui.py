import ttkbootstrap as ttk_b            # Import TTKBootstrap
from ttkbootstrap.constants import *
import json                             # Import json module
import os                               # For directory manipulation
from tkinter import scrolledtext        # Import tkinter module for scroll text box
from tkinter import *                   # Import all tkinter modules
from tkinter import filedialog          
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
'''
Add name of measurement. "name" field to be added.display in measure list box
'''

import emc

'''Constants'''
MAX_POSSIBLE_MEASUREMENTS   = 1000
DEFAULT_PADDING             = 5

'''Global Variables'''
settings_dir_path = ".settings"   # Saves the folder and file to store settings in
theme_file_path = settings_dir_path + "/theme.json" # Theme settings
configs_file_path = settings_dir_path + "/configs.json"   # Measurement configurations

dev = None
#dev = emc.DSA832()      # Create a device object representing the device used to get readings

# Dictionary of possible themes (Refer to ttkbootstrap manpage)
theme = {                
        "default"   : "superhero",
        "dark"      : "darkly",
        "light"     : "journal"
        }

'''
Function Description: Define a frame for the UI objects

Parameters: container - Main window object
position_y - column index for frame position
position_x - row index for frame position
frame_sticky - Frame side to attach to
theme = colour scheme

Note: Refer to https://ttkbootstrap.readthedocs.io/en/latest/styleguide/frame/

Return: frame object
'''
def define_frame(container, position_y = 0, position_x = 0, frame_sticky=None, theme='default'):

    frame = ttk_b.Frame(container, bootstyle=theme)
    frame.grid(column=position_y, row=position_x)
    frame.grid(sticky=frame_sticky)

    return frame

'''Functions: Widget Definitions'''
'''
Function Description: Define a drop down menu UI object

Parameters: container - Main window object
content_list - list of option in the drop down menu
position_y - columnm index for frame position
position_x - row index for frame position
default_state - default option selected by drop down menu
theme - colour scheme
sticky - Frame side to attach to

Note: Refer to https://ttkbootstrap.readthedocs.io/en/latest/styleguide/combobox/

Return: drop down object
'''
def define_drop_down(container, position_y = 0, position_x = 0, content_list = None, default_state = 'readonly', 
                     theme = 'default', sticky=None, width = 30):

    menu = ttk_b.Combobox(container, value=content_list, state=default_state, bootstyle = theme, width=width)
    menu.grid(column=position_y, row=position_x, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, sticky=sticky)

    return menu


'''
Function Description: Define a button UI object that can be used to call a function
when selected

Parameters: container - Main window object
position_y - columnm index for frame position
position_x - row index for frame position
text - label for the button
default_state - active / inactive
function_call - callback function triggered when button is pressed
theme - colour scheme
sticky - Frame side to attach to

Note: Refer to https://ttkbootstrap.readthedocs.io/en/latest/styleguide/button/

Return: button object
'''
def define_button(container, position_y = 0, position_x = 0, text = '', function_call = None, default_state = 'normal', theme = 'default', sticky=None):
    
    button = ttk_b.Button(container, text=text, command=function_call, state=default_state, bootstyle=theme)
    button.grid(column=position_y, row=position_x, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, sticky=sticky)

    return button


'''
Function Description: Define a label UI object

Parameters: container - Main window object
text - label text
position_y - columnm index for frame position
position_x - row index for frame position
theme - colour scheme
sticky - Frame side to attach to

Note: Refer to https://ttkbootstrap.readthedocs.io/en/latest/styleguide/label/

Return: button object
'''
def define_label(container, position_y = 0, position_x = 0, text = '', theme = 'normal', sticky=None):

    label = ttk_b.Label(container, text=text, bootstyle=theme)
    label.grid(column=position_y, row=position_x, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, sticky=sticky)
    return label


'''
Function Description: Define a checkbox UI object

Parameters: container - Main window object
position_y - columnm index for frame position
position_x - row index for frame position
text - label text
status_variable - checked / unchecked
function_call - function to call on change of state
default_state - active / inactive
theme - colour scheme

Note: Refer to https://ttkbootstrap.readthedocs.io/en/latest/styleguide/checkbutton/

Return: button object
'''
def define_checkbox(container, position_y = 0, position_x = 0, text = '', status_variable = None, function_call = None, 
                    default_state = 'normal', theme = 'default'):

    checkbox = ttk_b.Checkbutton(container, text=text, variable=status_variable, command=function_call, 
                                 state=default_state, bootstyle=theme)
    checkbox.grid(column=position_y, row=position_x, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)

    return checkbox


'''
Function Description: Define a scroll terminal

Parameters: container - Main window object
width - width of the textbox
height - height of the textbox
default_state - State of widget (Active / disabled)
position_y - columnm index for frame position
position_x - row index for frame position
sticky - Frame side to attach to

Return: textbox object
'''
def define_scroll_textbox(container, position_y = 0, position_x = 0, width = None, height = None, default_state = "normal", sticky=None):

    scrollbox = scrolledtext.ScrolledText(container, width=width, height=height, state=default_state)
    scrollbox.grid(column=position_y, row=position_x, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, sticky=sticky)
    scrollbox.configure(font=("Times New Roman", 10))

    return scrollbox


'''
Function Description: Define textbox to entry data into

Parameters: container - Main window object
width - width of the textbox
position_y - columnm index for frame position
position_x - row index for frame position
default_state - active / inactive
theme - colour scheme
sticky - Frame side to attach to
state - State of widget (Active / disabled)

Note: Refer to https://ttkbootstrap.readthedocs.io/en/latest/styleguide/entry/

Return: entrybox object
'''
def define_entry_textbox(container, position_y = 0, position_x = 0, width = 10, state = 'readonly', theme = 'default', sticky = None):
    entrybox = ttk_b.Entry(container, width=width, state=state, bootstyle=theme)
    entrybox.grid(column=position_y, row=position_x, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
    entrybox.configure(font=("Times New Roman", 10))
    entrybox.grid(sticky=sticky)

    return entrybox


'''
Function Description: Define a radio button UI object

Parameters: container - Main window object
position_y - columnm index for frame position
position_x - row index for frame position
text - label text
status_variable - checked / unchecked
function_call - function to call when change of state occurs
default_state - active / inactive
theme - colour scheme to use

Note: Refer to https://ttkbootstrap.readthedocs.io/en/latest/styleguide/radiobutton/#radio-default

Return: button object
'''
def define_radiobutton(container, position_y = 0, position_x = 0, text = '', status_variable = None, function_call = None, 
                       default_state = 'normal', theme = 'default'):
    
    radiobutton = ttk_b.Radiobutton(container, text=text, variable=status_variable, command=function_call, 
                                    state=default_state, bootstyle=theme)
    radiobutton.grid(column=position_y, row=position_x, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)

    return radiobutton

'''
Function Description: Define a tree view widget

Parameters: container - Main window object
position_y - columnm index for frame position
position_x - row index for frame position
sticky - frame side to attach to
selectmode - Item selection options (browse / extended)

Note: Refer to https://ttkbootstrap.readthedocs.io/en/version-0.5/widgets/treeview.html
'''
def define_treeview(container, position_y = 0, position_x = 0, selectmode = 'browse', sticky=None):

    tree = ttk.Treeview(container, show='headings', selectmode=selectmode)
    tree.grid(column=position_y, row=position_x, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING, sticky=sticky)
    return tree

'''
Function Description: Create a custom menu bar with options

Parameters: None

Return: Instance of menubar

Note: Refer to https://tkinterpython.top/menustoolbars/
'''
def create_menubar(window):

    # Create a new menu bar
    menu_bar = Menu(window)
    window.config(menu=menu_bar)

    # Create sub menus
    session_menu = Menu(menu_bar)
    theme_menu = Menu(menu_bar)

    menu_bar.add_cascade(label="Session", menu=session_menu)
    session_menu.add_command(label="Plot", command=lambda: switch_mode_plot(window))
    session_menu.add_command(label="Measure", command=lambda: switch_mode_measure(window))
    
    menu_bar.add_cascade(label="Theme", menu=theme_menu)
    theme_menu.add_command(label="Default", command=lambda: set_theme(window,theme["default"]))
    theme_menu.add_command(label="Dark", command=lambda: set_theme(window,theme["dark"]))
    theme_menu.add_command(label="Light", command=lambda: set_theme(window,theme["light"]))

    return menu_bar


def define_plot(container, position_y = 0, position_x = 0, sticky = None, xlabel = "x-axis", ylabel = "y-axis", title = "Plot", toolbar = False):
    # Create a Matplotlib figure and plot
    fig = Figure()
    ax = fig.add_subplot(111, facecolor=(0.0,0.5,1.0,0.1))
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()

    # Create a canvas and add the figure to it
    canvas = FigureCanvasTkAgg(fig, master=container)
    canvas.draw()
    canvas.get_tk_widget().grid(row=position_x, column=position_y, sticky=sticky)
    if toolbar == True:
        toolbar = NavigationToolbar2Tk(canvas, container, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=position_x+1, column=position_y, sticky=sticky)
    return canvas, ax

'''
Function Description: Alterate between modes (Plot vs Measurement)
'''
def switch_mode_plot(window):
    plot_session(window)

def switch_mode_measure(window):
    measure_session(window)

'''
Theme Functions
'''

'''
Function Description: Saves current theme to json file

Parameters: theme - string with theme name

Return: None
'''
def save_theme(theme: str):

    # Check if the settings hidden folder exists
    if os.path.isdir(settings_dir_path) == FALSE:
        # Create it if it doesnt exist
        os.mkdir(settings_dir_path)

    # Write to file
    with open(theme_file_path, 'w') as json_file:
        json.dump({"theme":theme}, json_file)
    
    return

'''
Function Description: Sets the theme of curretn session
based on given parameter or theme json file

Parameters: term_theme - Theme name

Return: None
'''
def set_theme(window, term_theme = None):

    if term_theme == None:
        # Load theme from the saved file
        term_theme = load_theme()

    # Perform a theme change if required
    window.style.theme_use(term_theme)   

    # Save the latest set theme
    save_theme(term_theme)

    return

'''
Function Description: Load theme from json file

Parameters: None

Return: None
'''
def load_theme():

    # Check if the theme hidden folder exists
    if os.path.isdir(settings_dir_path) == FALSE:
        # Create it if it doesnt exist
        os.mkdir(settings_dir_path)

    # Check if the theme json file exists
    if os.path.isfile(theme_file_path):
        # If yes, open and read it
        with open(theme_file_path, 'r') as f:
            data = json.load(f)
            saved_theme = data.get("theme")
    else:
        # If not, create one and set the default theme
        saved_theme = theme["default"]
        save_theme(saved_theme)

    return saved_theme


class measure_session():
    def __init__(self, window):
        # Init class variables
        self.window = window
        self.curr_directory = os.getcwd()   # Get current directory
        self.meas_count = 0         # Tracks how many measurements have been taken in a session
        self.session_obj = None     # Each sessions object
        self.session_description = ''   # Current sessions description given by user

        # Widgets
        self.meas_configs = []  # List of all measurement configurations available
        self.config_dropdown = None
        self.filepath = None
        self.new_measurement_button = None  # New measurement button
        self.save_measurement_button = None    # Save measurement button
                
        # Parent window size
        sizex = 1600
        sizey = 900

        # Load measurement configuration file
        self.load_meas_configfile()

        '''
        Frame Definitions
        '''
        # Generate GUI window
        # Define window size (XxY + XY offset)
        self.window.geometry(str(sizex) + 'x' + str(sizey) + "+100+100")
        # Set title for window
        self.window.title("EMC_Sessions_Measurements")

        # Clear previous window configurations
        # Clear widgets
        #for widget in window.winfo_children():
            #widget.grid_forget()
            #widget.destroy()
        list = self.window.grid_slaves()
        for l in list:
            l.grid_forget()
            l.destroy()

        # Ensure display frame expands with window as required
        self.window.columnconfigure(2, weight=1)
        self.window.rowconfigure(1, weight=1)

        # Create a menu Bar
        create_menubar(self.window)
        # Set previously saved theme
        set_theme(self.window)
        # Create framework
        self.create_parent_frames()


    ''' Frame Definition Functions '''

    ''' UI for Parent Window Generation Functions '''
    
    '''
    Function Description: Creates a frame to show the path of the current
    session savefile
    '''
    def create_frame_directory(self, position):

        # Define parent directory frame at the top
        frame_directory = define_frame(self.window, position[0], position[1], NSEW)
        # Ensure the box expands with the frame in the x axis
        frame_directory.columnconfigure(0, weight=1)
        # Add padding
        frame_directory.grid(pady=5)
        # Expand across columns
        frame_directory.grid(columnspan=3)

        '''
        Widget Positions (y,x coordinate in main window)
        '''
        pos_session_entrybox                = 0,0
        pos_new_session_button              = 1,0
        
        self.session_entry_box = define_entry_textbox(frame_directory, pos_session_entrybox[0], 
                                              pos_session_entrybox[1], width=50, sticky=NSEW)
        
        session_new_button = define_button(frame_directory, pos_new_session_button[0],
                                                pos_new_session_button[1], text="New Session", sticky=NSEW, 
                                                function_call=self.cb_create_new_session)


    '''
    Function Description: Creates all the widgets associated with
    configuration parameters
    '''
    def create_config_para_widgets(self, frame_config, state = 'disabled'):
        
        pos_config_label                    = 0,0
        pos_config_para_label               = 1,1

        pos_config_continuous_label         = 0,2
        pos_config_fstart_label             = 0,3
        pos_config_fstop_label              = 0,4
        pos_config_rbw_label                = 0,5
        pos_config_vbw_label                = 0,6
        pos_config_amp_label                = 0,7
        pos_config_atten_label              = 0,8
        pos_config_detector_label           = 0,9
        pos_config_emifilter_label          = 0,10
        pos_config_sweeppoints_label        = 0,11
        pos_config_sweepcount_label         = 0,12
        pos_config_tracemode_label          = 0,13
        pos_config_unit_label               = 0,14
        pos_config_offset_label             = 0,15
        pos_config_step_label               = 0,16
        pos_config_xscale_label             = 0,17

        pos_config_continuous_textbox        = 1,2
        pos_config_fstart_textbox           = 1,3
        pos_config_fstop_textbox            = 1,4
        pos_config_rbw_textbox              = 1,5
        pos_config_vbw_textbox              = 1,6
        pos_config_amp_textbox              = 1,7
        pos_config_atten_textbox            = 1,8
        pos_config_detector_textbox         = 1,9
        pos_config_emifilter_textbox        = 1,10
        pos_config_sweeppoints_textbox      = 1,11
        pos_config_sweepcount_textbox       = 1,12
        pos_config_tracemode_textbox        = 1,13
        pos_config_unit_textbox             = 1,14
        pos_config_offset_textbox           = 1,15
        pos_config_step_textbox             = 1,16
        pos_config_xscale_textbox           = 1,17

        config_label = define_label(frame_config, pos_config_label[0], pos_config_label[1], text="Configuration Name", sticky=NSEW)
        config_para_label = define_label(frame_config, pos_config_para_label[0], pos_config_para_label[1], text="----- Parameters -----", sticky=EW)
        config_para_label.config(anchor="center")

        config_continuous_label = define_label(frame_config, pos_config_continuous_label[0],
                                              pos_config_continuous_label[1], text="continuous", sticky=NSEW)
        config_fstart_label = define_label(frame_config, pos_config_fstart_label[0],
                                                pos_config_fstart_label[1], text="fstart", sticky=NSEW)
        config_fstop_label = define_label(frame_config, pos_config_fstop_label[0], 
                                              pos_config_fstop_label[1], text="fstop", sticky=NSEW)
        config_rbw_label = define_label(frame_config, pos_config_rbw_label[0], 
                                        pos_config_rbw_label[1], text="rbw", sticky=NSEW)
        config_vbw_label = define_label(frame_config, pos_config_vbw_label[0], 
                                        pos_config_vbw_label[1], text="vbw", sticky=NSEW)
        config_amp_label = define_label(frame_config, pos_config_amp_label[0],
                                        pos_config_amp_label[1], text="amp", sticky=NSEW)
        config_atten_label = define_label(frame_config, pos_config_atten_label[0],
                                          pos_config_atten_label[1], text="atten", sticky=NSEW)
        config_detector_label = define_label(frame_config, pos_config_detector_label[0], 
                                             pos_config_detector_label[1], text='detector', sticky=NSEW)
        config_emifilter_label = define_label(frame_config, pos_config_emifilter_label[0], 
                                              pos_config_emifilter_label[1], text='emifilter', sticky=NSEW)
        config_sweeppoints_label = define_label(frame_config, pos_config_sweeppoints_label[0],
                                                pos_config_sweeppoints_label[1], text="sweep points", sticky=NSEW)
        config_sweepcount_label = define_label(frame_config, pos_config_sweepcount_label[0],
                                               pos_config_sweepcount_label[1], text="sweepcount", sticky=NSEW) 
        config_tracemode_label = define_label(frame_config, pos_config_tracemode_label[0],
                                              pos_config_tracemode_label[1], text="tracemode", sticky=NSEW)
        config_unit_label = define_label(frame_config, pos_config_unit_label[0], 
                                         pos_config_unit_label[1], text="unit", sticky=NSEW)
        config_offset_label = define_label(frame_config, pos_config_offset_label[0], 
                                           pos_config_offset_label[1], text="offset", sticky=NSEW)
        config_step_label = define_label(frame_config, pos_config_step_label[0], 
                                         pos_config_step_label[1], text="step", sticky=NSEW)
        config_xscale_label = define_label(frame_config, pos_config_xscale_label[0], 
                                           pos_config_xscale_label[1], text="xscale", sticky=NSEW)
        
        config_continuous_textbox = define_entry_textbox(frame_config, pos_config_continuous_textbox[0],
                                                        pos_config_continuous_textbox[1], sticky=NSEW)
        config_fstart_textbox = define_entry_textbox(frame_config, pos_config_fstart_textbox[0],
                                                     pos_config_fstart_textbox[1], sticky=NSEW)
        config_fstop_textbox = define_entry_textbox(frame_config, pos_config_fstop_textbox[0],
                                                    pos_config_fstop_textbox[1], sticky=NSEW)
        config_rbw_textbox = define_entry_textbox(frame_config, pos_config_rbw_textbox[0],
                                                  pos_config_rbw_textbox[1], sticky=NSEW)
        config_vbw_textbox = define_entry_textbox(frame_config, pos_config_vbw_textbox[0],
                                                  pos_config_vbw_textbox[1], sticky=NSEW)
        config_amp_textbox = define_entry_textbox(frame_config, pos_config_amp_textbox[0],
                                                  pos_config_amp_textbox[1], sticky=NSEW)
        config_atten_textbox = define_entry_textbox(frame_config, pos_config_atten_textbox[0],
                                                    pos_config_atten_textbox[1], sticky=NSEW)
        config_detector_textbox = define_entry_textbox(frame_config, pos_config_detector_textbox[0],
                                                       pos_config_detector_textbox[1], sticky=NSEW)
        config_emifilter_textbox = define_entry_textbox(frame_config, pos_config_emifilter_textbox[0],
                                                        pos_config_emifilter_textbox[1], sticky=NSEW)
        config_sweeppoints_textbox = define_entry_textbox(frame_config, pos_config_sweeppoints_textbox[0],
                                                          pos_config_sweeppoints_textbox[1], sticky=NSEW)
        config_sweepcount_textbox = define_entry_textbox(frame_config, pos_config_sweepcount_textbox[0],
                                                         pos_config_sweepcount_textbox[1], sticky=NSEW)
        config_tracemode_textbox = define_entry_textbox(frame_config, pos_config_tracemode_textbox[0],
                                                        pos_config_tracemode_textbox[1], sticky=NSEW)
        config_unit_textbox = define_entry_textbox(frame_config, pos_config_unit_textbox[0],
                                                   pos_config_unit_textbox[1], sticky=NSEW)
        config_offset_textbox = define_entry_textbox(frame_config, pos_config_offset_textbox[0],
                                                     pos_config_offset_textbox[1], sticky=NSEW)
        config_step_textbox = define_entry_textbox(frame_config, pos_config_step_textbox[0],
                                                   pos_config_step_textbox[1], sticky=NSEW)
        config_xscale_textbox = define_entry_textbox(frame_config, pos_config_xscale_textbox[0],
                                                     pos_config_xscale_textbox[1], sticky=NSEW)


        # Add to dictionary and return
        config_dict = {}
        config_dict['continuous'] = config_continuous_textbox
        config_dict["fstart"] = config_fstart_textbox
        config_dict["fstop"] = config_fstop_textbox
        config_dict["rbw"] = config_rbw_textbox
        config_dict["vbw"] = config_vbw_textbox
        config_dict["amp"] = config_amp_textbox
        config_dict["atten"] = config_atten_textbox
        config_dict["detector"] = config_detector_textbox
        config_dict["emifilter"] = config_emifilter_textbox
        config_dict["sweeppoints"] = config_sweeppoints_textbox
        config_dict["sweepcount"] = config_sweepcount_textbox
        config_dict["tracemode"] = config_tracemode_textbox
        config_dict["unit"] = config_unit_textbox
        config_dict["offset"] = config_offset_textbox
        config_dict["step"] = config_step_textbox
        config_dict["xscale"] = config_xscale_textbox

        # Set state to active if required
        if state == 'normal':
            for i in config_dict:
                config_dict[i].config(state = 'normal')

        return config_dict

    
    '''
    Function Description: Creates the configuration frame. Has a dropdown for
    possible configurations, a button to add new and textboxes to display
    current configuration
    '''
    def create_frame_config(self, position):

        # Define config directory frame
        frame_config = define_frame(self.window, position[0], position[1], NW)
        # Ensure the box expands with the frame in the x axis
        frame_config.columnconfigure(1, weight=1)
        # Add a boundary
        frame_config.config(relief=SOLID, padding=5)

        '''
        Widget Positions (y,x coordinate in main window)
        '''
        pos_config_dropdown                 = 1,0
        pos_new_config_button               = 2,0

        # Get available config names to populate drop down
        config_list = self.get_available_config_names()

        self.config_dropdown = define_drop_down(frame_config, pos_config_dropdown[0], 
                                                pos_config_dropdown[1], content_list=config_list, sticky=NW)
        # Set the first configuration as the default on startup
        self.config_dropdown.set(config_list[0])
        # Create widgets
        config_para_widgets = self.create_config_para_widgets(frame_config)
        # Bind a functio to update parameter textboxes when user makes a selection
        self.config_dropdown.bind("<<ComboboxSelected>>", lambda event: self.update_para_widgets(widgets=config_para_widgets))

        config_new_button = define_button(frame_config, pos_new_config_button[0], 
                                          pos_new_config_button[1], text="New Config", sticky=NW,
                                          function_call=self.cb_create_add_config_window)
        
        self.update_para_widgets(config_para_widgets)
        

    '''
    Function Description: Creates the button frame. It has the save and new measurement
    buttons along with a nested frame with settings to identify peaks
    '''
    def create_frame_buttons(self, position):

        # Define button configuration frame
        frame_buttons = define_frame(self.window, position[0], position[1], N)
        # Add additional padding
        frame_buttons.config(padding=5)
        # Ensure the box expands with the frame in the x axis
        frame_buttons.columnconfigure(0, weight=1)

        '''
        Widget Positions (y,x coordinate in main window)
        '''
        pos_new_measurement_button          = 0,0
        pos_save_measurement_button         = 0,1
        pos_peaks_config_frame              = 0,2

        self.new_measurement_button = define_button(frame_buttons, pos_new_measurement_button[0],
                                               pos_new_measurement_button[1], sticky=NSEW, text="New Measurement"
                                               ,function_call=self.cb_new_measure)
        self.new_measurement_button.config(state='disabled')
        self.save_measurement_button = define_button(frame_buttons, pos_save_measurement_button[0],
                                                pos_save_measurement_button[1], sticky=NSEW, text="Save Masurement",
                                                function_call=self.cb_create_save_measurement_window)
        self.save_measurement_button.config(state='disabled')

        # define a nested frame for the peaks configurations
        self.create_frame_peaks_config(frame_buttons, pos_peaks_config_frame)
        
    '''
    Function Description: Creates a frame with textboxes for settings used to
    identfy peaks in the graph
    
    Note: frame exists inside button frame
    '''
    def create_frame_peaks_config(self, container, position):

        # Note: Nested in button configuration frame
        # Define peaks configuration frame
        frame_peaks_config = define_frame(container, position[0], 
                                               position[1], NSEW)
        # Ensure the box expands with the frame
        frame_peaks_config.columnconfigure(0, weight=1)
        frame_peaks_config.columnconfigure(1, weight=1)
        # Add a boundary
        frame_peaks_config.config(relief=SOLID, padding=5)

        '''
        Widget Positions (y,x coordinate in main window)
        '''
        pos_peakframe_label                   = 0,0
        pos_lags_label                        = 0,1
        pos_threshold_label                   = 0,2
        pos_influence_label                   = 0,3
        pos_lags_entrybox                     = 1,1
        pos_threshold_entrybox                = 1,2
        pos_influence_entrybox                = 1,3

        peakframe_label = define_label(frame_peaks_config, pos_peakframe_label[0], pos_peakframe_label[1], text="Peak Selection Config", 
                                       sticky=EW)
        peakframe_label.config(anchor="center")
        peakframe_label.grid(columnspan=2)
        lags_label = define_label(frame_peaks_config, pos_lags_label[0], 
                                           pos_lags_label[1], text="Lags",sticky=W)
        threshold_label = define_label(frame_peaks_config, pos_threshold_label[0], 
                                         pos_threshold_label[1], text="Threshold", sticky=W)
        influence_label = define_label(frame_peaks_config, pos_influence_label[0], 
                                           pos_influence_label[1], text="Influence", sticky=W)
        
        # Create stringvar variables to track when an update to the entry box is made
        lags_var = StringVar()
        threshold_var = StringVar()
        influence_var = StringVar()
        # Set up a trace on the StringVar to call on_entry_change whenever it changes
        lags_var.trace_add("write", None)   # PLACE PLOTTING FUNCTIONHERE
        threshold_var.trace_add("write", None)   # PLACE PLOTTING FUNCTIONHERE
        influence_var.trace_add("write", None)   # PLACE PLOTTING FUNCTIONHERE
        # Create entry boxes
        lags_textbox = define_entry_textbox(frame_peaks_config, pos_lags_entrybox[0], 
                                            pos_lags_entrybox[1], state='normal')
        lags_textbox.config(textvariable=lags_var)
        threshold_textbox = define_entry_textbox(frame_peaks_config, pos_threshold_entrybox[0], 
                                         pos_threshold_entrybox[1], state='normal')
        threshold_textbox.config(textvariable=threshold_var)
        influence_textbox = define_entry_textbox(frame_peaks_config, pos_influence_entrybox[0],
                                         pos_influence_entrybox[1], state='normal') 
        influence_textbox.config(textvariable=influence_var)   
    
    '''
    Function Description: Creates a frame to host the matplotlib interactive graph
    '''
    def create_frame_graph(self, position):

        # Define graph frame
        frame_graph = define_frame(self.window, position[0], position[1], NSEW)
        # Ensure the box expands with the frame
        frame_graph.columnconfigure(0, weight=1)
        frame_graph.rowconfigure(0, weight=1)
        # Add padding
        frame_graph.grid(padx=10)

        canvas, ax = define_plot(frame_graph, sticky=NSEW, toolbar=True)
        # Temp plot for testing
        ax.plot([1, 2, 3, 4], [10, 20, 25, 30])
        
    '''
    Function Description: Creates a frame to act as a buffer for padding against the bottom of
    the window
    '''
    def create_frame_buf(self, position):

        # Define lower buffer frame at bottom
        frame_buf = define_frame(self.window, position[0], position[1], NSEW)
        # Define height
        frame_buf.config(height=50)
        # Ensure the frame expands across all columns
        frame_buf.grid(columnspan=3)

    '''
    Function Description: Generate required frames for GUI
    '''
    def create_parent_frames(self):
        
        '''
        Frame Position values (y,x coordinate in main window)
        '''
        pos_directory_frame     = 0,0
        pos_graph_frame         = 2,1
        pos_button_frame        = 1,1
        pos_config_frame        = 0,1
        pos_buf_frame           = 0,2

        '''
        Frame Definitions
        '''
        self.create_frame_directory(pos_directory_frame)
        self.create_frame_config(pos_config_frame)
        self.create_frame_buttons(pos_button_frame)
        self.create_frame_graph(pos_graph_frame)
        self.create_frame_buf(pos_buf_frame)

    '''Configurations Functions'''

    '''Function Description: Loads the configuration json file with
    all configurations for measurements. If it does not exist,
    creates it with default configurations
    '''
    def load_meas_configfile(self):
        
        self.meas_configs = []
        
        # Check if the configs json file exists
        if os.path.isfile(configs_file_path):
            # If yes, open and read it
            with open(configs_file_path, 'r') as f:
                self.meas_configs = json.load(f)
        
        else:
            # If not, load default names
            for i in range(emc.Config.CONFIGS_AVAIL):
                self.meas_configs.append(emc.Config.get_config(i))
        
    def save_configs(self):
        
        # Save new added config to config file
        # Write to file
        data = []
        for i in self.meas_configs:
            data.append(i)
        with open(configs_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)


    def get_available_config_names(self):
        
        meas_config_names = []

        self.load_meas_configfile()
        for i in self.meas_configs:
            meas_config_names.append(i['Name'])

        return meas_config_names


    def update_para_widgets(self, widgets, readonly = TRUE):
        curr_config = None
        # Find confguration parameters of currently
        # selected config
        config_name = self.config_dropdown.get()
        for i in self.meas_configs:
            if (config_name == i["Name"]):
                curr_config = i
                break

        # enable edits to textboxes
        for i in widgets:
            widgets[i].config(state='normal')
            # Clear each entrybox
            widgets[i].delete('0',END)

        # insert new data 
        widgets['continuous'].insert(END, curr_config['continuous'])
        widgets["fstart"].insert(END, curr_config['fstart'])
        widgets["fstop"].insert(END, curr_config['fstop'])
        widgets["rbw"].insert(END, curr_config['rbw'])
        widgets["vbw"].insert(END, curr_config['vbw'])
        widgets["amp"].insert(END, curr_config['amp'])
        widgets["atten"].insert(END, curr_config['amp'])
        widgets["detector"].insert(END, curr_config['detector'])
        widgets["emifilter"].insert(END, curr_config['emifilter'])
        widgets["sweeppoints"].insert(END, curr_config['sweeppoints'])
        widgets["sweepcount"].insert(END, curr_config['sweepcount'])
        widgets["tracemode"].insert(END, curr_config['tracemode'])
        widgets["unit"].insert(END, curr_config['unit'])
        widgets["offset"].insert(END, curr_config['offset'])
        #widgets["step"].insert(END, curr_config['step'])
        widgets["xscale"].insert(END, curr_config['xscale'])

        if readonly == TRUE:
            # disable edits to textboxes
            for i in widgets:
                widgets[i].config(state='readonly')


    ''' Callback Functions '''

    '''----CONFIG WINDOW CALLBACKS START ----'''
    '''
    Function Description: Defines a new window called when the new configuration button
    is pressed. Allows user to fill a new configuration which is saved.
    '''
    def cb_create_add_config_window(self):
        # Create new window over the main window
        window = Toplevel()
        window.geometry("260x750+400+100")
        #window.resizable(width=False, height=False)
        window.title("New Configuration")

        # Disabled access to main terminal window
        window.grab_set()
        window.focus()
        # Install window close routine
        window.protocol("WM_DELETE_WINDOW",window.destroy)
        # Ensure frame can expand to window borders
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        # Create a frame 
        frame_config = define_frame(window, 0, 0, NW)
        # Ensure widgets expand as required
        frame_config.columnconfigure(0, weight=1)
        frame_config.rowconfigure(0, weight=1)
        frame_config.columnconfigure(1, weight=1)
        frame_config.rowconfigure(1, weight=1)

        # Define entry box not defined in function to create parameter widgets
        config_name_entry = define_entry_textbox(frame_config, 1, 0, sticky=NSEW)
        config_name_entry.config(state='normal')

        # Define config widgets
        widgets = self.create_config_para_widgets(frame_config, state = 'normal')
        self.update_para_widgets(widgets, readonly=FALSE)

        # Create a frame for save and cancel buttons
        save_frame = define_frame(window, 0, 1, frame_sticky=SE)
        
        # Append config name entrybox to widgets list
        widgets['Name'] = config_name_entry
        # Saves the name and description given by the user
        save_button = define_button(save_frame, 0, 0, " Save ", function_call= lambda: self.cb_config_save_button_pressed(window, widgets))
        # Kill the save window
        cancel_button = define_button(save_frame, 1, 0, "Cancel", function_call=window.destroy)


    def cb_config_save_button_pressed(self, window, widgets):
        
        # Get user input in each textbox and place in a dictionary
        new_config = {}
        new_config['Name'] = widgets['Name'].get()      # Get data from Config Name widget
        new_config['continuous'] = widgets['continuous'].get()
        new_config['fstart'] = widgets['fstart'].get()
        new_config['fstop'] = widgets['fstop'].get()
        new_config['rbw'] = widgets['rbw'].get()
        new_config['vbw'] = widgets['vbw'].get()
        new_config['amp'] = widgets['amp'].get()
        new_config['atten'] = widgets['atten'].get()
        new_config['detector'] = widgets['detector'].get()
        new_config['emifilter'] = widgets['emifilter'].get()
        new_config['sweeppoints'] = widgets['sweeppoints'].get()
        new_config['sweepcount'] = widgets['sweepcount'].get()
        new_config['tracemode'] = widgets['tracemode'].get()
        new_config['unit'] = widgets['sweeppoints'].get()
        new_config['offset'] = widgets['sweepcount'].get()
        new_config['xscale'] = widgets['tracemode'].get()

        # Perform input validation
        # Return

        # Append new config to list
        self.meas_configs.append(new_config)

        # Save to config json file
        self.save_configs()

        # Update the drop down box in the main windows config frame
        # Get available config names to populate drop down
        config_list = self.get_available_config_names()
        self.config_dropdown['values'] = config_list

        # Terminate the window
        window.destroy()

        return
    '''----CONFIG WINDOW CALLBACKS END ----'''

    '''----NEW MEASUREMENT WINDOW CALLBACKS START----'''
    '''
    Function Description: Defines a new window called when the save measurement button is
    pressed. Allows user to fill a measurement name and notes
    '''
    def cb_create_save_measurement_window(self):
        # Create new window over the main window
        window = Toplevel()
        window.geometry("400x200+300+400")
        #window.resizable(width=False, height=False)
        window.title("Save Measurement")
        # Ensure frame can expand to window borders
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        # Disabled access to main terminal window
        window.grab_set()
        window.focus()
        # Install window close routine
        window.protocol("WM_DELETE_WINDOW",window.destroy)

        # Create a frame 
        frame = define_frame(window, 0, 0, frame_sticky=NSEW)
        frame.grid(padx=5, pady=5)
        # Ensure widgets expand as required
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Create widgets
        new_meas_label = define_label(frame, 0, 0, "Name")
        description_label = define_label(frame, 0, 1, "Notes")

        new_meas_entrybox = define_entry_textbox(frame, 1, 0, sticky=EW)
        new_meas_entrybox.config(state='normal')
        description_scrollbox = define_scroll_textbox(frame, 1, 1, 40, 5, sticky=NSEW)

        # Create a nested frame for save and cancel buttons
        nested_frame = define_frame(frame, 1, 2, frame_sticky=SE)
        
        # Saves the name and description given by the user
        save_button = define_button(nested_frame, 
                                    0, 0, " Save ", 
                                    function_call= lambda: self.cb_new_meas_save_button_pressed(window, 
                                                                meas_name=new_meas_entrybox.get(), 
                                                                meas_desc=description_scrollbox.get('1.0', END)))
        # Kill the save window
        cancel_button = define_button(nested_frame, 1, 0, "Cancel", function_call=window.destroy)

    '''----NEW MEASUREMENT WINDOW CALLBACKS END----'''

    '''----GENERAL CALLBACKS START----'''

    def cb_new_session_descr_save_button_pressed(self, window, desc):

        self.session_description = desc

        # check if a description was given, else mark as NA
        if self.session_description == '':
            self.session_description = 'NA'

        window.destroy()


    def create_new_session_desc_window(self):
        # Create new window over the main window
        window = Toplevel()
        window.geometry("400x200+300+400")
        #window.resizable(width=False, height=False)
        window.title("Session Description")
        # Ensure frame can expand to window borders
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        # Disabled access to main terminal window
        window.grab_set()
        window.focus()
        # Install window close routine
        window.protocol("WM_DELETE_WINDOW",window.destroy)

        # Create a frame 
        frame = define_frame(window, 0, 0, frame_sticky=NSEW)
        frame.grid(padx=5, pady=5)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        description_scrollbox = define_scroll_textbox(frame, 0, 0, 40, 5, sticky=NSEW)

        # Create a nested frame for save and cancel buttons
        nested_frame = define_frame(frame, 0, 1, frame_sticky=SE)
        
        # Saves the name and description given by the user
        save_button = define_button(nested_frame, 
                                    0, 0, " Save ", 
                                    function_call= lambda: self.cb_new_session_descr_save_button_pressed(window,  
                                                                desc=description_scrollbox.get('1.0', END)))
        # Kill the save window
        cancel_button = define_button(nested_frame, 1, 0, "Cancel", function_call=window.destroy)

        # pause program till this window is closed
        self.window.wait_window(window)
            

    '''
    Function Description: Defines a new window called when the new session
    button is clicked. Allows user to save a new session file and add
    a description of the new session being started
    '''        
    def cb_create_new_session(self):
        
        # Destroy previous session object
        if self.session_obj != None:
            self.session_obj.destroy()
            self.session_description = ''

        # update new savefile path with a savefile prompt
        self.filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[('JSON File', '.json')])

        # User cancels save
        if self.filepath == '':
            return

        # Open session description window            
        self.create_new_session_desc_window()    

        # Check if cancel button was pressed in the new session description window
        if self.session_description == '':
            return 

        # Enable other widgets

        # load current filepath in textbox
        self.session_entry_box.config(state='normal')
        self.session_entry_box.delete(0, END)
        self.session_entry_box.insert(END, self.filepath)
        self.session_entry_box.config(state='readonly')

        # Create sessions object
        # /todo add ability to give description
        self.session_obj = emc.Session(dev, self.filepath, "")

        # Enable new measurement button
        self.new_measurement_button.config(state='normal')
        self.save_measurement_button.config(state='normal')


    def cb_new_measure(self):

        # Get a new meausurement
        self.session_obj.measure()

    def cb_new_meas_save_button_pressed(self, window, meas_name, meas_desc, event=None):

        # Get measurement
        # Save the new measurements name and description as required
        self.session_obj.savemeasure(self.filepath, meas_name=meas_name, note=meas_desc)
        
        # Destroy the save window
        window.destroy()

    '''----GENERAL CALLBACKS END----'''

# Generates a session plot window
class plot_session():

    # Generates new window
    def __init__(self, window):
        # Init class variables
        self.window = window            # Parent window
        self.entry_directory = None     # folder directory textbox
        self.tree_json = None           # tree shows available json files
        self.tree_measurement = None    # tree for measurements in each jason file
        self.selection_tree = None      # Tree for measurements selected 
        
        self.curr_directory = os.getcwd()   # Get current directory

        # Used for listing files
        self.json_files = []    # List of dictionaries of filenames and paths   {"filename", "filepath"}
        self.json_file_selected = {} # Dictionary of selected filename and path   {"filename", "filepath"}   

        # saves actual data of json files selected by user in list
        self.selected_json_data = {}   # Dictionary of current select json file data.
        
        # List of actual data of measurements selected by user in GUI
        # List of selected measurements data from selected json file 
        # {Sig_Level, Frequency, Note, Configuration, TimeStamp, Name, JSON_filename}
        self.selected_measurement = []   
        # Measurement selected in the selection tree by the user in GUI 
        self.selected_selection_tree = []  
        self.to_plot = []   # List of measurements to plot

        # Parent window size
        sizex = 1490
        sizey = 600

        '''
        Frame Definitions
        '''
        # Generate GUI window
        # self.window = ttk_b.Window(themename = theme["default"])
        # Define window size
        self.window.geometry(str(sizex) + 'x' + str(sizey))
        # Set title for window
        self.window.title("EMC_Sessions_Plots")

        # Clear previous window configurations
        # Iterate over all widgets in the window
                
        # Clear widgets
        #for widget in window.winfo_children():
            #widget.grid_forget()
            #widget.destroy()
        list = self.window.grid_slaves()
        for l in list:
            l.grid_forget()
            l.destroy()


        # Ensure display frame expands with window as required
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.window.columnconfigure(3, weight=1)
        self.window.rowconfigure(2, weight=1)

        # Create a menu Bar
        create_menubar(self.window)
        # Set previously saved theme
        set_theme(self.window)
        # Create framework
        self.create_frames()
        self.create_widgets()
        
        # load current directory in textbox
        self.entry_directory.insert(END,self.curr_directory)
        
        # List all sessions in folder / sub-folders
        self.json_files = emc.list_json_files()

        # Print json files in current directory/sub-directories to sessions tree
        for file in self.json_files:
            self.tree_json.insert('',END, values= file.get("filename"))

        #self.window.mainloop()
    
    '''
    Function Description: return new directory selected by user
    '''
    def update_directory(self):
        self.curr_directory = filedialog.askdirectory()
        # load current directory in textbox
        self.entry_directory.delete(0, END)
        self.entry_directory.insert(END, self.curr_directory)

        # List all sessions in folder / sub-folders
        self.json_files = emc.list_json_files(self.curr_directory)

        # Clear json tree
        for item in self.tree_json.get_children():
            self.tree_json.delete(item) 
        # Print to json tree
        for file in self.json_files:
            self.tree_json.insert('',END, values=file.get("filename"))
    
    '''
    Function Description: Called when the user selects a json file. Writes 
                description and measurements list to widgets
    '''
    def json_selected(self, event):
        # Get list of items selected
        selected_items = self.tree_json.selection()
        # Check if no item selected
        if not selected_items:
            return
        
        # Highlight selection
        for item in selected_items:
            self.tree_json.item(item, tags=("highlight",))
        
        # Store first selected item name
        selected_item = self.tree_json.item(selected_items[0])["values"][0]

        # Load json data
        for file in self.json_files:
            if file.get("filename") == selected_item:
                self.json_file_selected = file  # Save the filename and filepath dictionary
                self.selected_json_data = emc.load_sessiondata(selected_item)   # Load data in json file
        
        # Update metadata field with file name, desription etc
        self.entry_metadata.config(state='normal')
        self.entry_metadata.delete("1.0",END)
        self.entry_metadata.insert(END, f'File Name: \t\t{self.selected_json_data["File Name"]}\n')
        self.entry_metadata.insert(END, f'Date Created: \t\t{self.selected_json_data["Date Created"]}\n')
        self.entry_metadata.insert(END, f'Description: \t\t{self.selected_json_data["Description"]}\n')
        self.entry_metadata.config(state='disabled')

        # Update measurements tree with measurement from selected json
        # Clear json tree
        for item in self.tree_measurement.get_children():
            self.tree_measurement.delete(item) 
        # Iterate through the json file for each measure keyword until none are left
        for i in range(MAX_POSSIBLE_MEASUREMENTS):
            measure_key = f"measure{i}"
            '''
            # Search for measurement key in json file
            measurement = self.selected_json_data.get(measure_key, "Nonexistent")
            # Return nonexisent keyword if not found
            if(measurement == "Nonexistent"):
                # Assume all keys found and listed. Exit
                break
            # List on measurement tree
            self.tree_measurement.insert('',END, values=measure_key)
            '''
            for key in self.selected_json_data:
                if measure_key in key:
                    self.tree_measurement.insert('', END, values=key)
                    

    '''
    Function Description: Called when a measurement is selected in the
        measurement tree. Highlights selected item. Loads the measurement object
        with all measurement data. Appends to list of selected measurements.
        Appends the json file name and path associated with this measurement
        to measurement dictionary to be used for labelling in plots
    '''
    def measurement_selected(self, event):
        
        # Clear previous selection
        self.selected_measurement = []
        
        # Get list of items selected
        selected_items = self.tree_measurement.selection()
        # Check if no item selected
        if not selected_items:
            return
        
        for item in selected_items:
            # Highlight selection
            self.tree_measurement.item(item, tags=("highlight",))
            # Convert item ID to item name
            item_name = self.tree_measurement.item(item)["values"][0]
            # Temporarily save measurement data
            self.selected_measurement.append(self.selected_json_data[item_name])
            # Append name of the measurement
            self.selected_measurement[-1]["Name"] = item_name
            # Append treeview id of the measurement
            self.selected_measurement[-1]["id"] = item
            # Append name of json file
            self.selected_measurement[-1]['JSON_Name'] = self.json_file_selected["filename"].replace(".json",'')

        # Update Metadata box with data from last selected measurement
        self.entry_metadata.config(state='normal')
        self.entry_metadata.delete("1.0",END)
        self.entry_metadata.insert(END, f'Time Stamp: \t\t{self.selected_measurement[-1]["TimeStamp"]}\n')
        self.entry_metadata.insert(END, f'Configuration: \t\t{self.selected_measurement[-1]["Configuration"]}\n')
        self.entry_metadata.insert(END, f'Note: \t\t{self.selected_measurement[-1]["Note"]}\n')
        self.entry_metadata.config(state='disabled')
        
    
    def selection_selected(self, event):

        # Clear previous selection
        self.selected_selection_tree = []
        
        # Get list of items selected
        selected_items = self.tree_selection.selection()
        # Check if no item selected
        if not selected_items:
            return
        
        # Iterate through selected items in selection tree
        # and append to lsit of selected items in selection tree
        for item in selected_items:
            # Highlight selection
            self.tree_selection.item(item, tags=("highlight",))
            # Convert item ID to item name
            item_name = self.tree_selection.item(item)["values"][0]
            # Removed Json file name attached to measurement name
            item_name = item_name.replace(f"{self.json_file_selected["filename"].replace(".json","")}/", "")
            # Temporarily save measurement data
            self.selected_selection_tree.append(self.selected_json_data[item_name])
            # Append name of the measurement
            self.selected_selection_tree[-1]["Name"] = item_name
            # Append treeview id of the measurement
            self.selected_selection_tree[-1]["id"] = item

    '''
    Function Description: Called when the right button is pressed. Moves selected items from measurement tree
            to selection tree. Appends associated measurement objects to list to be plotted
    '''    
    def rb_pressed(self):
        
        # Get list of measurements already in selection tree
        item_names = []
        for item in self.tree_selection.get_children():
            item_names.append(self.tree_selection.item(item)["values"][0])
            
        # iterate through measurements selected in measurement tree
        for meas in self.selected_measurement:
            meas_name = f'{meas["JSON_Name"]}/{meas["Name"]}'
            if meas_name not in item_names:
                self.tree_selection.insert("", END, values=meas_name)
                # Add measurement data to plotting dictionary
                self.to_plot.append(meas)
        
    '''
    Function Description: Called when the left button is pressed. Removes selected items from selection tree. 
                Removes associated measurement objects from list to be plotted 
    '''
    def lb_pressed(self):

        # iterate through measurements selected in selection tree
        for meas in self.selected_selection_tree:
            # Delete from selection tree
            self.tree_selection.delete(meas["id"])
            # Remove measurement data from plotting dictionary
            self.to_plot.remove(meas)

    '''
    Function Description: Called when plot button is pressed. Plots list of measurement objects in selection
            tree
    '''
    def pltb_pressed(self):
        # plot plotting dictionary
        emc.plot(self.to_plot)

    '''
    Function Description: Called when clear button is pressed. Clears list of items from selection tree and 
            clear list of measurement objects to be plotted
    '''
    def clrb_pressed(self):

        # Clear selection tree
        for item in self.tree_selection.get_children():
            self.tree_selection.delete(item) 
        
        # Clear list of measurement to plot
        self.to_plot = []

    '''
    Function Description: Generate required frames for GUI
    '''
    def create_frames(self):
        
        '''
        Frame Position values (y,x coordinate in main window)
        '''
        pos_directory_frame     = 0,0
        pos_metadata_frame      = 0,1
        pos_json_frame          = 0,2
        pos_measurement_frame   = 1,2
        pos_buttons_frame       = 2,2
        pos_selection_frame     = 3,2
        pos_buf_frame           = 0,3


        # Define parent directory frame at the top
        self.frame_directory = define_frame(self.window, pos_directory_frame[0], pos_directory_frame[1], NSEW)
        # Ensure the box expands with the frame in the x axis
        self.frame_directory.columnconfigure(0, weight=1)
        self.frame_directory.rowconfigure(0, weight=1)
        # Ensure the frame expands across all columns
        self.frame_directory.grid(columnspan=4)

        # Define metadata frame at the top
        self.frame_metadata = define_frame(self.window, pos_metadata_frame[0], pos_metadata_frame[1], NSEW)
        # Ensure the box expands with the frame in the x axis
        self.frame_metadata.columnconfigure(0, weight=1)
        self.frame_metadata.rowconfigure(0, weight=1)
        # Ensure the frame expands across all columns
        self.frame_metadata.grid(columnspan=4)

        # define Json file list on the left
        self.frame_json = define_frame(self.window, pos_json_frame[0], pos_json_frame[1], NSEW)
        # Ensure the box expands with the frame in x,y axis
        self.frame_json.columnconfigure(0, weight=1)
        self.frame_json.rowconfigure(1, weight=1)
        
        # define measurement in selected json file on the right of above
        self.frame_measurement = define_frame(self.window, pos_measurement_frame[0], pos_measurement_frame[1], NSEW)
        # Ensure the box expands with the frame in x,y axis
        self.frame_measurement.columnconfigure(0, weight=1)
        self.frame_measurement.rowconfigure(1, weight=1)

        # define buttons frame on right of above (Select, Clear, Plot)
        self.frame_buttons = define_frame(self.window, pos_buttons_frame[0], pos_buttons_frame[1], NSEW)

        # define final selection frame on the right of above
        self.frame_selection = define_frame(self.window, pos_selection_frame[0], pos_selection_frame[1], NSEW)
        # Ensure the box expands with the frame in the x,y axis
        self.frame_selection.columnconfigure(0, weight=1)
        self.frame_selection.rowconfigure(1, weight=1)

        # Define lower buffer frame at bottom
        frame_buf = define_frame(self.window, pos_buf_frame[0], pos_buf_frame[1], S)
        # Ensure the frame expands across all columns
        frame_buf.grid(columnspan=4)


    '''
    Function Description: Defines widgets for each frame
    '''
    def create_widgets(self):

        '''
        Widget Positions (y,x coordinate in main window)
        '''
        pos_session_label           = 0,0
        pos_session_tree            = 0,1

        pos_measurement_label       = 0,0
        pos_measurement_tree        = 0,1

        pos_selection_label         = 0,0
        pos_selection_tree          = 0,1

        pos_empty_label             = 0,0
        pos_moveright_button        = 0,1
        pos_moveleft_button         = 0,2
        pos_plot_button             = 0,3
        pos_clear_button            = 0,4

        pos_directory_entrybox      = 0,0
        pos_directory_button        = 1,0    

        pos_metadata_scrollbox      = 0,0
    
        # Generate Widgets for each frame and assign functions as required
        '''frame_directory widgets'''
        self.entry_directory = define_entry_textbox(self.frame_directory, pos_directory_entrybox[0], pos_directory_entrybox[1], width=10, sticky=NSEW)
        button_directory = define_button(self.frame_directory, pos_directory_button[0], pos_directory_button[1], "Browse", self.update_directory)

        '''frame_metadata widgets'''
        self.entry_metadata = define_scroll_textbox(self.frame_metadata, pos_metadata_scrollbox[0], pos_metadata_scrollbox[1], 
                                                    width=10, height=3, default_state='disabled', sticky=NSEW)

        '''frame_json widgets'''
        define_label(self.frame_json, pos_session_label[0], pos_session_label[1], "Session", sticky=N)
        self.tree_json = define_treeview(self.frame_json, pos_session_tree[0], pos_session_tree[1], sticky=NSEW)
        self.tree_json.config(columns=('Filename'))
        # Called when user selects a json file in the sessions tree
        self.tree_json.bind('<<TreeviewSelect>>', self.json_selected)

        '''frame_measurement widgets'''
        define_label(self.frame_measurement, pos_measurement_label[0], pos_measurement_label[1], "Measurement", sticky=N)
        self.tree_measurement = define_treeview(self.frame_measurement, pos_measurement_tree[0], pos_measurement_tree[1], selectmode='extended', sticky=NSEW)
        self.tree_measurement.config(columns=('Measurement'))
        # Called when user selections measurements in the measurement tree
        self.tree_measurement.bind('<<TreeviewSelect>>', self.measurement_selected)

        '''frame_buttons widgets'''
        define_label(self.frame_buttons, pos_empty_label[0], pos_empty_label[1], sticky=NSEW)
        button_moveright = define_button(self.frame_buttons, pos_moveright_button[0], pos_moveright_button[1], " > ", function_call=self.rb_pressed, sticky=NSEW)
        button_moveleft  = define_button(self.frame_buttons, pos_moveleft_button[0], pos_moveleft_button[1], " < ", function_call=self.lb_pressed, sticky=NSEW)
        button_plot =    define_button(self.frame_buttons, pos_plot_button[0], pos_plot_button[1], "Plot", function_call=self.pltb_pressed, sticky=NSEW)
        button_clear =    define_button(self.frame_buttons, pos_clear_button[0], pos_clear_button[1], "Clear", function_call=self.clrb_pressed, sticky=NSEW)

        '''frame_selection widgets'''
        define_label(self.frame_selection, pos_selection_label[0], pos_selection_label[1], "Plot Selection", sticky=N)
        self.tree_selection = define_treeview(self.frame_selection, pos_selection_tree[0], pos_selection_tree[1], sticky=NSEW, selectmode='extended')
        self.tree_selection.config(columns=('Selection'))
        # Call when the user selects measurements in the selection tree
        self.tree_selection.bind('<<TreeviewSelect>>', self.selection_selected)


# Generate GUI window
window = ttk_b.Window(themename = theme["default"])
window.resizable(1,1)
# Modify window for measure session 
measure_session(window)
#plot_session(window)
# Run mainloop
window.mainloop()