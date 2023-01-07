## HypoModPython
##
## Started 5/11/18
## Continued 24/8/22
##
## Duncan MacGregor
##


import wx
import os
from pubsub import pub
from hypomain import *


app = wx.App(False)
pos = wx.DefaultPosition
size = wx.Size(400, 500)
mainpath = ""
respath = ""
mainwin = HypoMain("HypoMod", pos, size, respath, mainpath)
mainwin.Show()
app.MainLoop()


