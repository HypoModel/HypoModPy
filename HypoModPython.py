## HypoModPy
##
## Started 5/11/18
## Continued 24/8/22
##
## Duncan MacGregor
##


import wx
import os
from pathlib import Path
from hypobase import *
from hypocontrols import *
     
        



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
        #self.mainpath = mpath
        self.mainpath = os.getcwd()
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
        self.initpath = self.mainpath + "/Init/"
        if os.path.exists(self.mainpath) == False: 
            os.mkdir(self.initpath)

	    # box store
        filename = "mainbox.ini"
        outfile = TextFile(self.initpath + filename)
        outfile.Open('w')
        
        for box in self.toolset.boxset:
            outfile.WriteLine("{} {} {} {} {}".format(box.mpos.x, box.mpos.y, box.size.x, box.size.y, box.IsVisible()))
        
        outfile.Close()

    def MainLoad(self):
        # Box Load
        filepath = self.initpath + "/mainbox.ini"
        infile = TextFile(filepath)
        check = infile.Open('r')
        if check == False: return
        filetext = infile.ReadLines()
        for line in filetext:
            linedata = line.split(' ')
            boxtag = linedata[0]
            if self.toolset.Exists(boxtag) == False: continue            
            pos = wx.Point(linedata[1], linedata[2])
            size = wx.Size(linedata[3], linedata[4])
            self.toolset.boxset[boxtag].visible = linedata[5]
            self.toolset.boxset[boxtag].mpos = pos
            self.toolset.boxset[boxtag].boxsixe = size
        infile.Close()

        for box in self.toolset:
            box.ReSize()
            box.Show(box.visible)
	


class HypoMain(MainFrame):
    def __init__(self, title, pos, size, respath, mainpath):
        super(HypoMain, self).__init__(title, pos, size, respath, mainpath)
        self.diagbox.Show(True)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def OnClose(self, event):
        #OptionStore()
        MainFrame.MainStore(self)
        #if(project.mod): 
        #    project.Store()
        #if(mod):
        #    mod.Close()
        #    mod.Store()



class MyFrame(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(200,100))
        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.Show(True)
        
        

app = wx.App(False)
pos = wx.DefaultPosition
size = wx.Size(400, 500)
mainpath = ""
respath = ""
mainwin = HypoMain("HypoMod", pos, size, respath, mainpath)
mainwin.Show()
app.MainLoop()


