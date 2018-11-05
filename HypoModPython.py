## HypoModPy
##
## Started 5/11/18
##
## Duncan MacGregor
##


import wx



class ToolBox1(wx.Frame):
    #panel = wx.Panel
    def __init__(self, parent, title, pos, size):
        wx.Frame.__init__(self, parent, title = title, pos = pos, size = size, 
                          style = wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_TOOL_WINDOW | wx.CAPTION | wx.RESIZE_BORDER)
        self.panel = wx.Panel()
        
        
class ToolBox(wx.Frame):
    #panel = wx.Panel
    def __init__(self, parent, title, pos, size):
        wx.Frame.__init__(self, parent, title = title, pos = pos, size = size, 
                          style = wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_TOOL_WINDOW | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        self.panel = wx.Panel()


class DiagBox(ToolBox):
    def __init__(self, parent, title, pos, size):
        ToolBox.__init__(self, parent, title, pos, size)
        self.textbox = wx.TextCtrl(self, -1, "", wx.DefaultPosition, wx.Size(300, 400), wx.TE_MULTILINE)
    def Write(self, text):
        self.textbox.AppendText(text)    


class MainFrame(wx.Frame):
    def __init__(self, title, pos, size):
        wx.Frame.__init__(self, None, wx.ID_ANY, title, pos, size)
        self.ostype = GetSystem()
        self.statusbar = self.CreateStatusBar()
        self.diagbox = DiagBox(self, "Diagnostic", wx.DefaultPosition, wx.Size(400,500))
        self.diagbox.Write('Diagnostic Box OK\n')
        
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
         
        #self.toolset = ToolSet()
        #self.toolset.AddBox(diagbox, true)       


class HypoMain(MainFrame):
    def __init__(self, title, pos, size):
        MainFrame.__init__(self, title, pos, size)
        self.diagbox.Show(True);
        


class MyFrame(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(200,100))
        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.Show(True)
        
        
def GetSystem():
    oslabel = wx.GetOsDescription()
    if oslabel.startswith('Windows'): return 1
    if oslabel.startswith('Mac') or oslabel.StartsWith('mac'): return 2
    if oslabel.startswith('Linux'): return 3
    return 0



app = wx.App(False)
pos = wx.DefaultPosition
size = wx.Size(500, 500)
mainwin = HypoMain('HypoMod', pos, size)
mainwin.Show()
app.MainLoop()


