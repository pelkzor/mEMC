import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import emc_refactor


# Create a window
root = ttk.Window(themename="cosmo")

# Set the window title
root.title("Plot Measurements")

# Set the window size
root.geometry("400x300")

# Add a button
button = ttk.Button(root, text="Click Me", bootstyle="success")
button.pack(pady=20)

# Add a label
label = ttk.Label(root, text="Hello, TtkBootstrap!", bootstyle="info")
label.pack(pady=20)

# Add an entry
entry = ttk.Entry(root)
entry.pack(pady=20)

# Start the main loop
root.mainloop()
