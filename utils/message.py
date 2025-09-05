import inspect
from enum import IntEnum, auto

class MSG(IntEnum):

    INIT = auto()
    CONNECT = auto()
    DISCONNECT = auto()
    BTNMEASURE = auto()
    SETWORKDIR = auto()
    SETMEASTEMPLATE = auto()
    SETEUTTEMPLATE = auto()
    SETCORRECTION = auto()
    SETSTANDARD = auto()
    MEASURE = auto()
    SETVAR = auto()
    LOG = auto()
    THREAD = auto()

class THREADMSG(IntEnum):
    INIT = auto()
    STOP = auto()
    ERROR = auto()
    STEP = auto()
    TEXT = auto()
    DATA = auto()
    DONE = auto()
    PROGRESS = auto()

EVT_CONNECT = lambda : (MSG.CONNECT,)
EVT_DISCONNECT = lambda : (MSG.CONNECT,)

#decorator for onevent_ methods
def eventhandler(key):
    def decorator(func):
        def registerhandler(self, evt, *args, **kwargs):            
            if evt == (MSG.INIT,):
                return key
            func(self, evt, *args, **kwargs)            
        return registerhandler
    return decorator

class EventHandler:

    def __init__(self, *args, **kwargs):        
        self.handlers = {}
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        for m in methods:
            if m[0].startswith('onevent_'):
                self.handlers[m[1]((MSG.INIT,))] = m[1]

    def onevent(self, evt):
        for i in range(len(evt),0,-1):
            if evt[:i] in self.handlers:
                return self.handlers[evt[:i]](*evt)
            
        print('no handler')
        return False  



