
import wx
from hypoparams import *
from hypodat import *
from threading import Thread
from datetime import datetime
import wx.lib.newevent


# Custom Thread Event
ModThreadCompleteEvent = wx.NewEventType()
EVT_MODTHREAD_COMPLETE = wx.PyEventBinder(ModThreadCompleteEvent, 0)

class ModThreadEvent(wx.PyCommandEvent):
    def __init__(self, evtType):
        wx.PyCommandEvent.__init__(self, evtType)


# Mod Class
class Mod(wx.EvtHandler):
    def __init__(self, mainwin, tag):
        wx.EvtHandler.__init__(self)

        self.mainwin = mainwin
        self.tag = tag
        self.type = type
        self.graphload = False

        self.modtools = {}
        self.modbox = None

        self.plotbase = PlotBase(mainwin)
        self.settags = []

        self.Bind(EVT_MODTHREAD_COMPLETE, self.OnModThreadComplete)


    def GetPath(self):
        if modpath == "": 
            if self.path != "": fullpath = self.path
            else: fullpath = self.mainwin.initpath
        else:
            if self.path != "": fullpath = modpath + "/" + self.path
            else: fullpath = modpath

        print("path " + self.path)
        print("fullpath " + fullpath)

        if os.path.exists(fullpath) == False: 
            os.mkdir(fullpath)

        return fullpath


    def ModStore(self):
        #filepath = self.GetPath()
        filepath = self.path
        
        # box store
        filename = self.tag + "-box.ini"
        outfile = TextFile(filepath + "/" + filename)
        outfile.Open('w')

        for box in self.modtools.values():
            outfile.WriteLine("{} {} {} {} {} {}".format(box.boxtag, box.mpos.x, box.mpos.y, box.boxsize.x, box.boxsize.y, box.IsShown()))
            if box.storetag != None: box.storetag.HistStore()

        outfile.Close()
        print("ModStore OK")

 
    def ModLoad(self):
        #filepath = self.GetPath()
        filepath = self.path

        # box load
        filename = self.tag + "-box.ini"
        infile = TextFile(filepath + "/" + filename)
        check = infile.Open('r')
        if check == False: 
            print("ModLoad box file not found")
            return
        filetext = infile.ReadLines()

        for line in filetext:
            linedata = line.split(' ')
            boxtag = linedata[0]
            if boxtag in self.modtools.keys():      
                pos = wx.Point(int(linedata[1]), int(linedata[2]))
                size = wx.Size(int(linedata[3]), int(linedata[4]))
                if linedata[5] == 'True\n': visible = True
                else: visible = False
                self.modtools[boxtag].visible = visible
                self.modtools[boxtag].mpos = pos
                self.modtools[boxtag].boxsize = size

        infile.Close()

        for box in self.modtools.values():
            box.SetSize(box.boxsize)
            box.SetPosition(self.mainwin.GetPosition(), self.mainwin.GetSize())
            box.Show(box.visible)

        print("ModLoad OK")


    def GridColumn(self, col):
        return 0


    def GridRow(self, row):
        return 0



class ModThread(Thread):
    def __init__(self, box, mainwin):
        Thread.__init__(self)

        self.modbox = box
        self.mainwin = mainwin
        self.diag = False

    

