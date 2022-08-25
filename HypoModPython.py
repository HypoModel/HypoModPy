## HypoModPy
##
## Started 5/11/18
## Continued 24/8/22
##
## Duncan MacGregor
##


import wx
from pathlib import Path

     
        
class ToolBox(wx.Frame):
    def __init__(self, parent, tag, title, pos, size, 
    style = wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_TOOL_WINDOW | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX):
        wx.Frame.__init__(self, parent, title = title, pos = pos, size = size, style = style)
        self.panel = wx.Panel()
        self.boxtag = tag

# alt style = wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_TOOL_WINDOW | wx.CAPTION | wx.RESIZE_BORDER


class ToolSet():
    def __init__(self):
        self.boxset = {}

    def AddBox(self, newbox):
        self.boxset[newbox.boxtag] = newbox

    def GetBox(self, tag):
        if(tag in self.boxset):
             return self.boxset[tag]
        else:
             return False



class DiagBox(ToolBox):
    def __init__(self, parent, title, pos, size):
        ToolBox.__init__(self, parent, "DiagBox", title, pos, size)
        self.textbox = wx.TextCtrl(self, -1, "", wx.DefaultPosition, wx.Size(300, 400), wx.TE_MULTILINE)
    def Write(self, text):
        self.textbox.AppendText(text)    


class MainFrame(wx.Frame):
    def __init__(self, title, pos, size, rpath, mpath):
        super(MainFrame, self).__init__(None, wx.ID_ANY, title, pos, size)
        self.ostype = GetSystem()
        self.statusbar = self.CreateStatusBar()
        self.diagbox = DiagBox(self, "Diagnostic", wx.Point(0, 0), wx.Size(400, 500))
        self.diagbox.Write('Diagnostic Box OK\n')

        respath = rpath;  # defaults to "" for Windows, bundle resource path for OSX
        self.diagbox.Write("MainFrame respath " + respath + "\n")
        self.mainpath = mpath
        self.modpath = ""
        
        self.colourpen = {}
        self.colourpen["black"] = wx.Colour("#000000")
        self.colourpen["red"] = wx.Colour("#F50000")
        self.colourpen["green"] = wx.Colour("#000000")
        self.colourpen["blue"] = wx.Colour("#0000F5")
        self.colourpen["yellow"] = wx.Colour("#F5F500")
        self.colourpen["purple"] = wx.Colour("#F500F5")
        self.colourpen["lightred"] = wx.Colour("#FF8080")
        self.colourpen["lightgreen"] = wx.Colour("#80FF80")
        self.colourpen["lightblue"] = wx.Colour("#8080FF")
        self.colourpen["custom"] = wx.Colour("#000000")
         
        self.toolset = ToolSet()
        self.toolset.AddBox(self.diagbox)     

    def MainStore(self):
	    # TextFile outfile, opfile;
        initpath = self.mainpath + "/Init/"
        if not wx.DirExists(initpath): 
            wx.Mkdir(initpath)

	    # box store
        filename = "mainbox.ini"
        outfile = TextFile(initpath + filename)
        outfile.Open()
        
        for box in self.toolset:
            outfile.WriteLine("{} {} {} {} {}".format(box.mpos.x, box.mpos.y, box.size.x, box.size.y, box.IsVisible()))
        
        outfile.Close()




class HypoMain(MainFrame):
    def __init__(self, title, pos, size, respath, mainpath):
        super(HypoMain, self).__init__(title, pos, size, respath, mainpath)
        self.diagbox.Show(True)
        


class MyFrame(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(200,100))
        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.Show(True)
        
        
def GetSystem():
    oslabel = wx.GetOsDescription()
    if oslabel.startswith("Windows"): return 1
    if oslabel.startswith("Mac") or oslabel.startswith("mac"): return 2
    if oslabel.startswith("Linux"): return 3
    return 0


class TextFile():
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.readonly = True

    def Exists(self):
        return self.filepath.is_file()

    def Open(self, mode):
        if mode == 'r' & self.Exists() == False:
            return False
        self.file = open(self.filepath, mode)
        self.unread = True
        return self.file

    def WriteLine(self, text):
        self.file.write(text + '\n')

    def Close(self):
        self.file.close()

	# Postscript Writing
	#void MoveTo(double x, double y);
	#void LineTo(double x, double y);
	#void DrawLine(double xf, double yf, double xt, double yt);
	#void DrawText(wxString, double x, double y);
	#void DrawEllipse(double x, double y, double width, double height);
	#void SetColour(wxString);




app = wx.App(False)
pos = wx.DefaultPosition
size = wx.Size(800, 1000)
mainpath = ""
respath = ""
mainwin = HypoMain("HypoMod", pos, size, respath, mainpath)
mainwin.Show()
app.MainLoop()


