
import wx
from hypoparams import *


class Model(wx.EvtHandler):
    def __init__(self, mainwin, tag):
        self.mainwin = mainwin
        self.tag = tag
        self.type = type
        
