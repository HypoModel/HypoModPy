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

from pubsub import pub
     
        

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

        self.textbox = wx.TextCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE)
        self.mainbox.Add(self.textbox, 1, wx.EXPAND)


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

        if mainpath == "": self.initpath = "Init"
        else: self.initpath = mainpath + "/Init"
        
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

        pub.subscribe(self.status_listener, "status_listener")
        pub.subscribe(self.toolclose_listener, "toolclose_listener")

        self.Bind(wx.EVT_LEFT_UP, self.OnLeftClick)

        self.MainLoad()


    def status_listener(self, message, arg2=None):
        self.SetStatusText(message)


    def toolclose_listener(self, boxtag, arg2=None):
        del self.toolset.boxset[boxtag]


    def MainStore(self):
        self.initpath = self.mainpath + "/Init/"
        if os.path.exists(self.mainpath) == False: 
            os.mkdir(self.initpath)

	    # box store
        filename = "mainbox.ini"
        outfile = TextFile(self.initpath + filename)
        outfile.Open('w')
        
        for box in self.toolset.boxset.values():
            outfile.WriteLine("{} {} {} {} {} {}".format(box.boxtag, box.mpos.x, box.mpos.y, box.boxsize.x, box.boxsize.y, box.IsShown()))
        
        outfile.Close()
        print('MainStore OK')


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
            #if boxtag in self.toolset.boxset: 
            check = boxtag in self.toolset.boxset
            if check: print('boxtag OK')
            #continue  
            if check: 
                print('tag' + ' ' + boxtag + ' ' + 'data1' + ' ' + linedata[1])          
                pos = wx.Point(int(linedata[1]), int(linedata[2]))
                size = wx.Size(int(linedata[3]), int(linedata[4]))
                if linedata[5] == 'True\n': visible = True
                else: visible = False
                print(linedata[5])
                #self.toolset.boxset[boxtag].Show(False)
                self.toolset.boxset[boxtag].visible = visible
                self.toolset.boxset[boxtag].mpos = pos
                self.toolset.boxset[boxtag].boxsize = size
        infile.Close()

        for box in self.toolset.boxset.values():
            box.SetSize(box.boxsize)
            box.SetPosition(self.GetPosition(), self.GetSize())
            box.Show(box.visible)
            

    def OnLeftClick(self, event):
        for box in self.toolset.boxset.values():
            if box.IsShown(): box.Show(False)
            else: box.Show(True)
           
	

class HypoMain(MainFrame):
    def __init__(self, title, pos, size, respath, mainpath):
        super(HypoMain, self).__init__(title, pos, size, respath, mainpath)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        
    def OnClose(self, event):
        #OptionStore()
        MainFrame.MainStore(self)
        #if(project.mod): 
        #    project.Store()
        #if(mod):
        #    mod.Close()
        #    mod.Store()
        event.Skip()

    
    def OnMove(self, event):
        for box in self.toolset.boxset.values():
            box.SetPosition(self.GetPosition(), self.GetSize())
        event.Skip()


    def OnSize(self, event):
        for box in self.toolset.boxset.values():
            box.SetPosition(self.GetPosition(), self.GetSize())
        event.Skip()



app = wx.App(False)
pos = wx.DefaultPosition
size = wx.Size(400, 500)
mainpath = ""
respath = ""
mainwin = HypoMain("HypoMod", pos, size, respath, mainpath)
mainwin.Show()
app.MainLoop()


