
from math import sqrt
import wx
from pathlib import Path


def GetSystem():
    oslabel = wx.GetOsDescription()
    if oslabel.startswith("Windows"): return 'Windows'
    if oslabel.startswith("Mac") or oslabel.startswith("mac"): return 'Mac'
    if oslabel.startswith("Linux"): return 'Linux'
    return 0


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
mainpath = ''
projectpath = ''

# Control IDs
ID_Sync = wx.NewIdRef()
ID_Store = wx.NewIdRef()
ID_Load = wx.NewIdRef()


