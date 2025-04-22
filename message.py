from enum import IntEnum, auto

class MSG(IntEnum):

    CONNECT = auto()
    DISCONNECT = auto()
    BTNMEASURE = auto()
    SETWORKDIR = auto()
    SETMEASTEMPLATE = auto()
    SETEUTTEMPLATE = auto()
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

