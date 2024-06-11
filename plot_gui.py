import ttkbootstrap as ttk_b
from ttkbootstrap.constants import *
import json     # Import json module
import os       # For directory manipulation
from tkinter import scrolledtext        # Import tkinter module for scroll text box
from tkinter import ttk
from tkinter import *                   # Import all tkinter modules

import emc_refactor

'''Global Variables'''
settings_dir_path = ".settings"   # Saves the folder and file to store settings in
theme_file_path = settings_dir_path + "/theme.json" # Theme settings

sizex = 1490
sizey = 600

'''
Frame Position values (y,x coordinate in main window)
'''
pos_directory_frame     = 0,0
pos_json_frame          = 0,1
pos_measurement_frame   = 1,1
pos_buttons_frame       = 2,1
pos_selection_frame     = 3,1
pos_buf_frame           = 0,2

'''
Widget Positions
'''
pos_session_label           = 0,0
pos_session_scrollbox       = 0,1

pos_measurement_label       = 0,0
pos_measurement_scrollbox   = 0,1

pos_selection_label         = 0,0
pos_selection_scrollbox     = 0,1

pos_empty_label         = 0,0
pos_moveright_button    = 0,1
pos_moveleft_button     = 0,2
pos_plot_button         = 0,3

pos_directory_entrybox  = 0,0
pos_directory_button    = 1,0    
pos_metadata_scrollbox  = 0,1

theme = {                # Dictionary of possible themes (Refer to ttkbootstrap manpage)
        "default"   : "superhero",
        "dark"      : "darkly",
        "light"     : "journal"
        }

'''Object Definitions'''
'''
Function Description: Define a frame for the UI objects

Parameters: container - Main window object
position_y - column index for frame position
position_x - row index for frame position
theme = colour scheme

Note: Refer to https://ttkbootstrap.readthedocs.io/en/latest/styleguide/frame/

Return: frame object
'''
def define_frame(container, position_y, position_x, frame_sticky=None, theme='default'):

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

Note: Refer to https://ttkbootstrap.readthedocs.io/en/latest/styleguide/combobox/

Return: drop down object
'''
def define_drop_down(container, position_y, position_x, content_list, default_state = 'normal', theme = 'default'):

    menu = ttk_b.Combobox(container, value=content_list, state=default_state, bootstyle = theme)
    menu.grid(column=position_y, row=position_x, padx=1, pady=1)

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

Note: Refer to https://ttkbootstrap.readthedocs.io/en/latest/styleguide/button/

Return: button object
'''
def define_button(container, position_y, position_x, text = '', function_call = None, default_state = 'normal', theme = 'default', sticky=None):
    
    button = ttk_b.Button(container, text=text, command=function_call, state=default_state, bootstyle=theme)
    button.grid(column=position_y, row=position_x, padx=2, pady=2, sticky=sticky)

    return button


'''
Function Description: Define a label UI object

Parameters: container - Main window object
text - label text
position_y - columnm index for frame position
position_x - row index for frame position
theme - colour scheme

Note: Refer to https://ttkbootstrap.readthedocs.io/en/latest/styleguide/label/

Return: button object
'''
def define_label(container, position_y, position_x, text = '', theme = 'normal', sticky=None):

    label = ttk_b.Label(container, text=text, bootstyle=theme)
    label.grid(column=position_y, row=position_x, padx=2, pady=2, sticky=sticky)
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
def define_checkbox(container, position_y, position_x, text = '', status_variable = None, function_call = None, 
                    default_state = 'normal', theme = 'default'):

    checkbox = ttk_b.Checkbutton(container, text=text, variable=status_variable, command=function_call, 
                                 state=default_state, bootstyle=theme)
    checkbox.grid(column=position_y, row=position_x, padx=2, pady=2)

    return checkbox


'''
Function Description: Define a scroll terminal

Parameters: container - Main window object
width - width of the textbox
height - height of the textbox
position_y - columnm index for frame position
position_x - row index for frame position

Return: textbox object
'''
def define_scroll_textbox(container, position_y = 0, position_x = 0, width = None, height = None, sticky=None):

    scrollbox = scrolledtext.ScrolledText(container, width=width, height=height, state="disabled")
    scrollbox.grid(column=position_y, row=position_x, padx=2, pady=2, sticky=sticky)
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

Note: Refer to https://ttkbootstrap.readthedocs.io/en/latest/styleguide/entry/

Return: entrybox object
'''
def define_entry_textbox(container, position_y = 0, position_x = 0, width = 10, state = 'normal', theme = 'default', sticky = None):
    entrybox = ttk_b.Entry(container, width=width, state=state, bootstyle=theme)
    entrybox.grid(column=position_y, row=position_x, padx=2, pady=2)
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
def define_radiobutton(container, position_y, position_x, text = '', status_variable = None, function_call = None, 
                       default_state = 'normal', theme = 'default'):
    
    radiobutton = ttk_b.Radiobutton(container, text=text, variable=status_variable, command=function_call, 
                                    state=default_state, bootstyle=theme)
    radiobutton.grid(column=position_y, row=position_x, padx=2, pady=2)

    return radiobutton



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
def set_theme(term_theme = None):

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


'''
Function Description: Create a custom menu bar with options

Parameters: None

Return: Instance of menubar
'''
def create_menubar():

    # Create a new menu bar
    menu_bar = Menu(window)
    window.config(menu=menu_bar)

    # Create sub menus
    theme_menu = Menu(menu_bar)

    menu_bar.add_cascade(label="Theme", menu=theme_menu)
    theme_menu.add_command(label="Default", command=lambda: set_theme(theme["default"]))
    theme_menu.add_command(label="Dark", command=lambda: set_theme(theme["dark"]))
    theme_menu.add_command(label="Light", command=lambda: set_theme(theme["light"]))

    return menu_bar


'''
Function Description: Generate required frames

Parameters: None

Return: None
'''
def create_frames():
    # Define parent directory frame at the top
    frame_directory = define_frame(window, pos_directory_frame[0], pos_directory_frame[1], NSEW)
    # Add some spacing
    frame_directory.grid(padx=5, pady=5)
    # Ensure the box expands with the frame in the x axis
    frame_directory.columnconfigure(0, weight=1)
    frame_directory.rowconfigure(0, weight=1)
    # Ensure the frame expands across all columns
    frame_directory.grid(columnspan=4)

    # define Json file list on the left
    frame_json = define_frame(window, pos_json_frame[0], pos_json_frame[1], NSEW)
    # Add some spacing
    frame_json.grid(padx=5, pady=5)
    # Ensure the box expands with the frame in x,y axis
    frame_json.columnconfigure(0, weight=1)
    frame_json.rowconfigure(1, weight=1)
    
    # define measurement in selected json file on the right of above
    frame_measurement = define_frame(window, pos_measurement_frame[0], pos_measurement_frame[1], NSEW)
    # Add some spacing
    frame_measurement.grid(padx=5, pady=5)
    # Ensure the box expands with the frame in x,y axis
    frame_measurement.columnconfigure(0, weight=1)
    frame_measurement.rowconfigure(1, weight=1)

    # define buttons frame on right of above (Select, Clear, Plot)
    frame_buttons = define_frame(window, pos_buttons_frame[0], pos_buttons_frame[1], NSEW)
    # Add some spacing
    frame_buttons.grid(padx=5, pady=5)

    # define final selection frame on the right of above
    frame_selection = define_frame(window, pos_selection_frame[0], pos_selection_frame[1], NSEW)
    # Add some spacing
    frame_selection.grid(padx=5, pady=5)
    # Ensure the box expands with the frame in the x,y axis
    frame_selection.columnconfigure(0, weight=1)
    frame_selection.rowconfigure(1, weight=1)

    # Define lower buffer frame at bottom
    frame_buf = define_frame(window, pos_buf_frame[0], pos_buf_frame[1], S)
    # Add some spacing
    frame_buf.grid(padx=5, pady=5)
    # Ensure the frame expands across all columns
    frame_buf.grid(columnspan=4)

    # Generate Widgets for each frame
    '''frame_directory widgets'''
    # Create scroll box for folder directory
    entry_directory = define_entry_textbox(frame_directory, pos_directory_entrybox[0], pos_directory_entrybox[1], width=10, sticky=NSEW)
    button_directory = define_button(frame_directory, pos_directory_button[0], pos_directory_button[1], "Folder")
    entry_metadata = define_scroll_textbox(frame_directory, pos_metadata_scrollbox[0], pos_metadata_scrollbox[1], width=10, height=5, sticky=NSEW)

    '''frame_json widgets'''
    # Create scroll box for folder directory
    label_json = define_label(frame_json, pos_session_label[0], pos_session_label[1], "Session", sticky=N)
    scroll_json = define_scroll_textbox(frame_json, pos_session_scrollbox[0], pos_session_scrollbox[1], width=10, height=10, sticky=NSEW)

    '''frame_measurement widgets'''
    label_measurement = define_label(frame_measurement, pos_measurement_label[0], pos_measurement_label[1], "Measurement", sticky=N)
    scroll_measurement = define_scroll_textbox(frame_measurement, pos_measurement_scrollbox[0], pos_measurement_scrollbox[1], width=10, 
                                               height=10, sticky=NSEW)

    '''frame_buttons widgets'''
    label_empty = define_label(frame_buttons, pos_empty_label[0], pos_empty_label[1], sticky=NSEW)
    button_moveright = define_button(frame_buttons, pos_moveright_button[0], pos_moveright_button[1], " > ", sticky=NSEW)
    button_moveleft  = define_button(frame_buttons, pos_moveleft_button[0], pos_moveleft_button[1], " < ", sticky=NSEW)
    button_plot =    define_button(frame_buttons, pos_plot_button[0], pos_plot_button[1], "Plot", sticky=NSEW)

    '''frame_selection widgets'''
    label_selection = define_label(frame_selection, pos_selection_label[0], pos_selection_label[1], "Plot Selection", sticky=N)
    scroll_selection = define_scroll_textbox(frame_selection, pos_selection_scrollbox[0], pos_selection_scrollbox[1], width=10, height=10, sticky=NSEW)

'''
Frame Definitions
'''
# Generate GUI window
window = ttk_b.Window(themename = theme["default"])
# Define window size
window.geometry(str(sizex) + 'x' + str(sizey))
# Set title for window
window.title("EMC_Sessions_Plots")
# Ensure display frame expands with window
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(3, weight=1)
window.rowconfigure(1, weight=1)

# Create a menu Bar
menu_bar = create_menubar()
# Set previously saved theme
set_theme()
# Create framework
create_frames()

# Bind Enter key to plot button
# window.bind("<Return>", )

'''
Main loop
'''
window.mainloop()