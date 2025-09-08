import ttkbootstrap as ttk_b            # Import TTKBootstrap
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview

from pathlib import Path
import json
import os

class ResultTable(ttk_b.Frame):

    def __init__(self, parent):
        super(ResultTable, self).__init__(parent)
        self.results = {}

        coldata = [
            {'text': 'Time', "width": 100},
            {"text": "Name", "stretch": False},
            "EUT Configuration",
            {"text": "Start Frequency", "stretch": False},
        ]        

        self.table = Tableview(self, coldata=coldata, paginated=False, searchable=True, bootstyle=PRIMARY)#, stripecolor=(colors.light, None))
        self.table.pack(side='left', fill=BOTH, expand=True)
        self.table.view.bind('<Double-1>', self.on_dclick)
        self.tvscroll = ttk_b.Scrollbar(self, orient='vertical', command=self.table.view.yview)
        self.table.view.config(yscrollcommand=self.tvscroll.set)
        self.tvscroll.pack(side='left',fill='y')        
        self.table.load_table_data()
        #print(self.table.get_rows())
    
    def on_dclick(self, evt):
        rowid = self.table.view.identify_row(evt.y)
        row = self.table.get_row(iid=rowid)
        print(row.values)
    
    def delete_rows(self):
        rows = self.table.get_rows()
        for i in reversed(range(len(rows))):
            try:
                self.table.delete_row(i)
            except:
                continue

    def get_results_directory(self):
        working_dir = os.environ.get('WORKING_DIR')
        
        if working_dir:
            results_dir = Path(working_dir)
        else:
            # Fall back to default "results" folder
            results_dir = Path('results')
            print("WORKING_DIR not set, using default 'results' folder")
        results_dir.mkdir(exist_ok=True)
        return results_dir

    def loadfiles(self):
        results_dir = self.get_results_directory()
        filenames = list(results_dir.glob('*.json'))
        rows = []
        for name in filenames:
            with open(name, 'r') as f:
                result = json.loads(f.read())
                self.results[result['time']] = result
                
                # Format time display
                original_time = result['time']
                if len(original_time) == 10:
                    date_part = original_time[:6]
                    time_part = original_time[6:]
                    formatted_time = f"{date_part} {time_part[:2]}:{time_part[2:]}"  # YYMMDD HH:MM
                else:
                    formatted_time = original_time  # Fallback
                
                rows.append([formatted_time, result['name'], result['eutconfig']['EUT Name'], result['measurementconfig']['fstart']])
        
        self.table.insert_rows('end', rows)
        self.table.load_table_data()
class ResultBrowser(ttk_b.Toplevel):    

    def __init__(self):
        super().__init__()        
        #self.tv = TreeFrame(self)
        #self.tv.pack()
        self.table = ResultTable(self)
        self.table.pack()
        self.table.loadfiles()

    def refresh_results(self):
        self.table.delete_rows()
        self.table.loadfiles()        

    

        