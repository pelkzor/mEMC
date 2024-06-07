import socket
import json
import time


from instrument_abstract import Instrument

'''
Desc: Stores configuration information / methods
Para: Instrument abstract class
Return None
'''
class DSA832(Instrument):

    # Initialise communication 
    # Read data from cmd's file
    def __init__(self, ip = "192.168.1.70"):
        self.data = b''         # Raw data recieved from device
        self.trace = None       # trace data recovered from raw data recieved
        #self.scalex = 0       

        # Load commands
        self.loadcmd()

        # Establish connection to device
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, 5555))
        self.sock.setblocking(False)
    
    # Load commands from json file
    def loadcmd(self):
        # Load list of commands
        with open('vars.json','r') as f:
            self.inst = json.loads(f.read())
        

    # prepares cmd ascii message to be sent to device
    def cmd(self, cmd, arg1 = None, arg2 = None):
        
        # Check if command given is part of list of valid
        # commands loaded from file
        if not cmd in self.inst:
            print("No such command")

        # Return scpi field of command
        c = self.inst[cmd]['scpi']
    
        # check if arg1 has been given
        if arg1 != None:
            # Return type field of command
            t = self.inst[cmd]['type']
            
            if arg1 == '?':         # used for enquiries
                c = c + '?'            
            # Adjust command based on type specifier
            elif t == 'int' or t == 'float':
                if isinstance(arg1, int) or isinstance(arg1,float):
                    c = c + ' ' + str(arg1)
                if isinstance(arg2, int) or isinstance(arg2,float):
                    c = c + ' ' + str(arg2)
            elif t == 'intns':
                if isinstance(arg1, int):
                    c = c + str(arg1)              
            elif t == 'enum':
                if isinstance(arg1, int):
                    c = c + ' ' + self.inst[cmd]['enum'][arg1]
                else:
                    c = c + ' ' + arg1
            elif t == 'filename':
                c = c + ' E:\\' + arg1
            print(c)
            
        # Send command to instrument    
        self.send(c)
        
        # Check for read field in command typle. If yes, means 
        # expect data to be returned from device
        fmt = None
        if 'read' in self.inst[cmd]:
            fmt = self.inst[cmd]['read']
            self.data = b''
            time.sleep(1)
            d = self.recv()
            if fmt == 'trace':
                return self.processtrace(d)
        
        # Return data after casting as required type 
        elif arg1 == '?':
            fmt = self.inst[cmd]['type']
            time.sleep(0.2)
            d = self.recv()
            # If no data recieved, re-attempt reading 
            if d is None:
                time.sleep(1)
                d = self.recv()
            if fmt == 'int':
                return int(d)
            elif fmt == 'float':
                return float(d)
            
    # Send command
    def send(self, cmd):
        self.sock.send((cmd+'\r\n').encode('utf-8'))        
    
    # Receive message from device
    def recv(self) -> bytes:

        # make 2 attempts to recieve expected data        
        for i in range(2):
            self.data = b'' 
            try:
                d = self.sock.recv(2048)
                # Check if any data was received 
                if len(d):
                    self.data = self.data + d
                print(d.decode('utf-8'))
                # Returns binary data as ascii
                return d.decode('utf-8')
            except Exception as e:
                print(e)
                time.sleep(2)
        
    # Format trace data
    def processtrace(self, data) -> float:
        v = data.split(',')
        v[0] = v[0].split()[1]
        return [ float(n) for n in v]
