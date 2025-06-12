import ttkbootstrap as ttk_b            # Import TTKBootstrap
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview

from pathlib import Path
import json

class ResultTable(ttk_b.Frame):

    def __init__(self, parent):
        super(ResultTable, self).__init__(parent)
        self.results = {}

        coldata = [
            {'text': 'Time', 'width': 40},
            {"text": "Name", "stretch": False},
            "EUT Cfg",
            {"text": "Meas Cfg", "stretch": False},
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
        if row.values[0] == 'X':
            row.values[0] = ''
        else:
            row.values[0] = 'X'
        row.refresh()
        print(row.values)

    def loadfiles(self):
        filenames = list(Path('.').glob('*.json'))
        rows = []
        for name in filenames:
            print(name)
            with open(name, 'r') as f:
                result = json.loads(f.read())                   #!!!note: should probably drop data to reduce memory usage
                self.results[result['time']] = result
                rows.append([result['time'],result['name'], result['comment'], 'None'])
        self.table.insert_rows('end',rows)
        self.table.load_table_data()
        print('done')
           
class ResultBrowser(ttk_b.Toplevel):    

    def __init__(self):
        super().__init__()        
        #self.tv = TreeFrame(self)
        #self.tv.pack()
        self.table = ResultTable(self)
        self.table.pack()
        #self.table.loadfiles()               

    

        