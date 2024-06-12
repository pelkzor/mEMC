import ttkbootstrap as ttk_b
from ttkbootstrap.constants import *
import json     # Import json module
import os       # For directory manipulation
from tkinter import scrolledtext        # Import tkinter module for scroll text box
from tkinter import *                   # Import all tkinter modules
from tkinter import filedialog
from tkinter import ttk

import emc_refactor as emc

'''Global Variables'''
settings_dir_path = ".settings"   # Saves the folder and file to store settings in
theme_file_path = settings_dir_path + "/theme.json" # Theme settings


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
def define_scroll_textbox(container, position_y = 0, position_x = 0, width = None, default_state = "normal", height = None, sticky=None):

    scrollbox = scrolledtext.ScrolledText(container, width=width, height=height, state=default_state)
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
Note: Refer to https://ttkbootstrap.readthedocs.io/en/version-0.5/widgets/treeview.html
'''

def define_treeview(container, position_y, position_x, sticky=None):

    tree = ttk.Treeview(container, show='headings')
    tree.grid(column=position_y, row=position_x, padx=2, pady=2, sticky=sticky)

    return tree

'''
Function Description: Create a custom menu bar with options

Parameters: None

Return: Instance of menubar
'''
def create_menubar(window):

    # Create a new menu bar
    menu_bar = Menu(window)
    window.config(menu=menu_bar)

    # Create sub menus
    theme_menu = Menu(menu_bar)

    menu_bar.add_cascade(label="Theme", menu=theme_menu)
    theme_menu.add_command(label="Default", command=lambda: set_theme(window,theme["default"]))
    theme_menu.add_command(label="Dark", command=lambda: set_theme(window,theme["dark"]))
    theme_menu.add_command(label="Light", command=lambda: set_theme(window,theme["light"]))

    return menu_bar


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


# Generates a session plot window as a separate process. terminate current process
class plot_session():

    # Generates new window
    def __init__(self):
        # Init class variables
        self.window = None              # Parent window
        self.entry_directory = None     # folder directory textbox
        self.button_directory = None    # Folder search button
        self.tree_json = None           # tree shows available json files
        self.tree_measurement = None    # tree for measurements in each jason file
        self.button_moveright = None    # Button to select measurements 
        self.button_moveleft = None     # Button to deselect measurements
        self.button_plot = None         # Plot selected measurements
        self.selection_tree = None      # Tree for measurements selected 
        
        self.curr_directory = os.getcwd()   # Get current directory

        self.json_files = {}    # Dictionary of filenames and paths
        self.selected_json_data = {}   # Dictionary of current select json file data
        self.selected_measurement = {}    # Dictionary of selected measurement data from selected json file

        # Parent window size
        sizex = 1490
        sizey = 600

        '''
        Frame Definitions
        '''
        # Generate GUI window
        self.window = ttk_b.Window(themename = theme["default"])
        # Define window size
        self.window.geometry(str(sizex) + 'x' + str(sizey))
        # Set title for window
        self.window.title("EMC_Sessions_Plots")
        # Ensure display frame expands with window
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

        # Print to sessions to tree
        for file in self.json_files:
            self.tree_json.insert('',END, values= file.get("filename"))

        '''
        Main loop
        '''
        self.window.mainloop()

    
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
    Function: Called when the user selects a json file. Writes 
                description and measurements list to widgets
    '''
    def json_selected(self, event):
        # Get list of items selected
        selected_items = self.tree_json.selection()
        # Check if no item selected
        if not selected_items:
            return
        
        # Store first selected item
        selected_item = self.tree_json.item(selected_items[0])["values"][0]
        # Deselect all other items. Ensure only 1 item can be selected
        for item in self.tree_json.get_children():
            if item != selected_item:
                self.tree_json.selection_remove(item)

        # Load json data
        for file in self.json_files:
            if file.get("filename") == selected_item:
                self.selected_json_data = emc.load_sessiondata(selected_item)
        
        # Update metadata field with file name, desription etc
        self.entry_metadata.delete("1.0",END)
        self.entry_metadata.insert(END, f'File Name: \t\t{self.selected_json_data["File Name"]}\n')
        self.entry_metadata.insert(END, f'Date Created: \t\t{self.selected_json_data["Date Created"]}\n')
        self.entry_metadata.insert(END, f'Description: \t\t{self.selected_json_data["Description"]}\n')

        # Update measurements tree with measurement from selected json
        # Clear json tree
        for item in self.tree_measurement.get_children():
            self.tree_measurement.delete(item) 
        # Iterate through the json file for each measure keyword until none are left
        for i in range(100):
            measure_key = f"measure{i}"
            # Search for measurement key in json file
            measurement = self.selected_json_data.get(measure_key, "Nonexistent")
            # Return nonexisent keyword if not found
            if(measurement == "Nonexistent"):
                # Assume all keys found and listed. Exit
                break
            # List on measurement tree
            self.tree_measurement.insert('',END, values=measure_key)
            
            ''' # Access all information and isolate
            data = measurement["Sig_Level"]
            datax = measurement["Frequency"]
            note = measurement["Note"]
            config = measurement["Configuration"]
            image_note = f'{note}\nConfig: {config}'
            '''

    def measurement_selected(self, event):
        # Get list of items selected
        selected_items = self.tree_measurement.selection()
        # Check if no item selected
        if not selected_items:
            return
        
        # Store first selected item
        selected_item = self.tree_measurement.item(selected_items[0])["values"][0]
        # Deselect all other items. Ensure only 1 item can be selected
        for item in self.tree_measurement.get_children():
            if item != selected_item:
                self.tree_measurement.selection_remove(item)

        # Temporarily save measurement data
        self.selected_measurement = self.selected_json_data[selected_item]
        # Append the name of measurement to dictionary
        self.selected_measurement["Name"] = selected_item

        # Update Metadata box
        self.entry_metadata.delete("1.0",END)
        self.entry_metadata.insert(END, f'Time Stamp: \t\t{self.selected_measurement["TimeStamp"]}\n')
        self.entry_metadata.insert(END, f'Configuration: \t\t{self.selected_measurement["Configuration"]}\n')
        self.entry_metadata.insert(END, f'Note: \t\t{self.selected_measurement["Note"]}\n')

        
    def rb_pressed(self):
        
        # List measurement selected on selection tree
        self.tree_selection.insert('',END, values=self.selected_measurement["Name"])

        # Add measurement data to plotting dictionary

        pass

    def lb_pressed(self):

        # Delete measurement selected in selection tree

        # Remove measurement data to plotting dictionary

        pass

    def pltb_pressed(self):

        # plot plotting dictionary
        
        pass

    def clrb_pressed(self):

        # Clear selection tree
        for item in self.tree_selection.get_children():
            self.tree_selection.delete(item) 

    '''
    Function Description: Generate required frames

    Parameters: None

    Return: None
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
        # Add some spacing
        self.frame_directory.grid(padx=5, pady=5)
        # Ensure the box expands with the frame in the x axis
        self.frame_directory.columnconfigure(0, weight=1)
        self.frame_directory.rowconfigure(0, weight=1)
        # Ensure the frame expands across all columns
        self.frame_directory.grid(columnspan=4)

        # Define parent directory frame at the top
        self.frame_metadata = define_frame(self.window, pos_metadata_frame[0], pos_metadata_frame[1], NSEW)
        # Add some spacing
        self.frame_metadata.grid(padx=5, pady=5)
        # Ensure the box expands with the frame in the x axis
        self.frame_metadata.columnconfigure(0, weight=1)
        self.frame_metadata.rowconfigure(0, weight=1)
        # Ensure the frame expands across all columns
        self.frame_metadata.grid(columnspan=4)

        # define Json file list on the left
        self.frame_json = define_frame(self.window, pos_json_frame[0], pos_json_frame[1], NSEW)
        # Add some spacing
        self.frame_json.grid(padx=5, pady=5)
        # Ensure the box expands with the frame in x,y axis
        self.frame_json.columnconfigure(0, weight=1)
        self.frame_json.rowconfigure(1, weight=1)
        
        # define measurement in selected json file on the right of above
        self.frame_measurement = define_frame(self.window, pos_measurement_frame[0], pos_measurement_frame[1], NSEW)
        # Add some spacing
        self.frame_measurement.grid(padx=5, pady=5)
        # Ensure the box expands with the frame in x,y axis
        self.frame_measurement.columnconfigure(0, weight=1)
        self.frame_measurement.rowconfigure(1, weight=1)

        # define buttons frame on right of above (Select, Clear, Plot)
        self.frame_buttons = define_frame(self.window, pos_buttons_frame[0], pos_buttons_frame[1], NSEW)
        # Add some spacing
        self.frame_buttons.grid(padx=5, pady=5)

        # define final selection frame on the right of above
        self.frame_selection = define_frame(self.window, pos_selection_frame[0], pos_selection_frame[1], NSEW)
        # Add some spacing
        self.frame_selection.grid(padx=5, pady=5)
        # Ensure the box expands with the frame in the x,y axis
        self.frame_selection.columnconfigure(0, weight=1)
        self.frame_selection.rowconfigure(1, weight=1)

        # Define lower buffer frame at bottom
        frame_buf = define_frame(self.window, pos_buf_frame[0], pos_buf_frame[1], S)
        # Add some spacing
        frame_buf.grid(padx=5, pady=5)
        # Ensure the frame expands across all columns
        frame_buf.grid(columnspan=4)



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
        self.button_directory = define_button(self.frame_directory, pos_directory_button[0], pos_directory_button[1], "Browse", self.update_directory)

        '''frame_metadata widgets'''
        self.entry_metadata = define_scroll_textbox(self.frame_metadata, pos_metadata_scrollbox[0], pos_metadata_scrollbox[1], width=10, height=3, sticky=NSEW)

        '''frame_json widgets'''
        define_label(self.frame_json, pos_session_label[0], pos_session_label[1], "Session", sticky=N)
        self.tree_json = define_treeview(self.frame_json, pos_session_tree[0], pos_session_tree[1], sticky=NSEW)
        self.tree_json.config(columns=('Filename'))
        self.tree_json.bind('<<TreeviewSelect>>', self.json_selected)

        '''frame_measurement widgets'''
        define_label(self.frame_measurement, pos_measurement_label[0], pos_measurement_label[1], "Measurement", sticky=N)
        self.tree_measurement = define_treeview(self.frame_measurement, pos_measurement_tree[0], pos_measurement_tree[1], sticky=NSEW)
        self.tree_measurement.config(columns=('Measurement'))
        self.tree_measurement.bind('<<TreeviewSelect>>', self.measurement_selected)

        '''frame_buttons widgets'''
        define_label(self.frame_buttons, pos_empty_label[0], pos_empty_label[1], sticky=NSEW)
        self.button_moveright = define_button(self.frame_buttons, pos_moveright_button[0], pos_moveright_button[1], " > ", function_call=self.rb_pressed, sticky=NSEW)
        self.button_moveleft  = define_button(self.frame_buttons, pos_moveleft_button[0], pos_moveleft_button[1], " < ", function_call=self.lb_pressed, sticky=NSEW)
        self.button_plot =    define_button(self.frame_buttons, pos_plot_button[0], pos_plot_button[1], "Plot", function_call=self.pltb_pressed, sticky=NSEW)
        self.button_plot =    define_button(self.frame_buttons, pos_clear_button[0], pos_clear_button[1], "Clear", function_call=self.clrb_pressed, sticky=NSEW)

        '''frame_selection widgets'''
        define_label(self.frame_selection, pos_selection_label[0], pos_selection_label[1], "Plot Selection", sticky=N)
        self.tree_selection = define_treeview(self.frame_selection, pos_selection_tree[0], pos_selection_tree[1], sticky=NSEW)
        self.tree_selection.config(columns=('Selection'))

plot_session()