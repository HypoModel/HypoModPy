
from math import sqrt
import wx
from pathlib import Path
from pubsub import pub


def GetSystem():
    oslabel = wx.GetOsDescription()
    if oslabel.startswith("Windows"): return 'Windows'
    if oslabel.startswith("Mac") or oslabel.startswith("mac"): return 'Mac'
    if oslabel.startswith("Linux"): return 'Linux'
    return 0


def DiagWrite(text):
    pub.sendMessage("diagbox", message=text)


class TextFile():
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.readonly = True

    def Exists(self):
        return self.filepath.is_file()

    def Open(self, mode):
        if mode == 'r' and self.Exists() == False: 
            return False
        self.file = open(self.filepath, mode)
        self.unread = True
        return self.file

    def WriteLine(self, text):
        self.file.write(text + '\n')

    def ReadLine(self):
        return self.file.readline()

    def ReadLines(self):
        return self.file.readlines()

    def Close(self):
        self.file.close()

	# Postscript Writing
	#void MoveTo(double x, double y);
	#void LineTo(double x, double y);
	#void DrawLine(double xf, double yf, double xt, double yt);
	#void DrawText(wxString, double x, double y);
	#void DrawEllipse(double x, double y, double width, double height);
	#void SetColour(wxString);


def DistXY(p1, p2):
    return sqrt(pow(p2.x - p1.x) + pow(p2.y - p1.y, 2))


def numstring(number, places=0):
    return f"{number:.{places}f}"


# Paths
mainpath = ""
projectpath = "/Users/duncan/Model"
modpath = "/Users/duncan/Model"

# Control IDs
ID_Sync = wx.NewIdRef()
ID_Store = wx.NewIdRef()
ID_Load = wx.NewIdRef()
ID_Run = wx.NewIdRef()
ID_AutoRun = wx.NewIdRef()
ID_Default = wx.NewIdRef()

# Events
#EVT_MODTHREAD_COMPLETE_ID = wx.NewIdRef()

#def EVT_MODTHREAD_COMPLETE(win, func):
#    """Define Result Event."""
 #   win.Connect(-1, -1, EVT_MODTHREAD_COMPLETE_ID, func)

#class ModThreadCompleteEvent(wx.PyEvent):
#    """Simple event to carry arbitrary result data."""
#    def __init__(self, data):
 #       """Init Result Event."""
#        wx.PyEvent.__init__(self)
 #       self.SetEventType(EVT_MODTHREAD_COMPLETE_ID)
#        self.data = data



