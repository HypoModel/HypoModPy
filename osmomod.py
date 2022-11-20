
import wx
import random

from hypomods import *
from hypoparams import *
from hypodat import *



class OsmoMod(Mod):
    def __init__(self, mainwin, tag):
        Mod.__init__(self, mainwin, tag)

        if modpath != "": self.path = modpath + "/Osmo"
        else: self.path = "Osmo"

        if os.path.exists(self.path) == False: 
            os.mkdir(self.path)

        self.osmobox = OsmoBox(self, "osmo", "Osmo", wx.Point(0, 0), wx.Size(320, 500))
        self.modtools[self.osmobox.boxtag] = self.osmobox
        self.osmobox.Show(True)
        mainwin.toolset.AddBox(self.osmobox)  
        self.modbox = self.osmobox

        self.ModLoad()
        print("Osmo Model OK")

        self.osmodata = OsmoDat()
        self.PlotData()


    def PlotData(self):

        ## Data plots
        ##
        ## PlotDat(data pointer, xfrom, xto, yfrom, yto, label string, plot type, bin size, colour)
        ## ----------------------------------------------------------------------------------
        self.plotbase.Add(PlotDat(self.osmodata.water, 0, 2000, 0, 5000, "water", 4, 1, "blue"), "water")
        self.plotbase.Add(PlotDat(self.osmodata.salt, 0, 2000, 0, 100, "salt", 4, 1, "red"), "salt")
        self.plotbase.Add(PlotDat(self.osmodata.osmo, 0, 2000, 0, 100, "osmo", 4, 1, "green"), "osmo")
        # self.graphbaseAdd(PlotDat(self.osmodata.heat, 0, 2000, 0, 100, "heat", 4, 1, "lightred"), "heat")
        # self.graphbase.Add(PlotDat(self.osmodata.vaso, 0, 2000, 0, 100, "vaso", 4, 1, "purple"), "vaso")

        # Initial plots
        self.pcodes.append("water")
        self.pcodes.append("salt")
        self.pcodes.append("osmo")
        # gcodes[3] = "heat";
        # gcodes[4] = "vaso";
        # gcodes[5] = "water";

        self.gcount = 3
        self.gsmode = 1


    def OnModThreadComplete(self, event):
        #runmute->Lock();
        #runflag = 0;
        #runmute->Unlock();
        self.mainwin.scalebox.GraphUpdate()
        self.DiagWrite("Model thread OK\n\n")


    def RunModel(self):
        self.mainwin.SetStatusText("Osmo Model Run")
        modthread = OsmoModel(self)
        modthread.start()



class OsmoDat():
    def __init__(self):
        self.water = []
        self.salt = []
        self.osmo = []
        self.vaso = []



class OsmoBox(ParamBox):
    def __init__(self, model, tag, title, position, size):
        ParamBox.__init__(self, model, title, position, size, tag, 0, 1)

        # Parameter controls
        #
        # AddCon(tag string, display string, initial value, click increment, decimal places)
        # ----------------------------------------------------------------------------------

        self.paramset.AddCon("runtime", "Run Time", 2000, 1, 0)
        self.paramset.AddCon("hstep", "h Step", 1, 0.1, 1)
        self.paramset.AddCon("waterloss", "Water Loss", 0, 0.001, 4)

        self.ParamLayout(2)

        # ----------------------------------------------------------------------------------

        runbox = self.RunBox()
        paramfilebox = self.StoreBoxSync()

        self.mainbox.AddSpacer(5)
        self.mainbox.Add(self.pconbox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddStretchSpacer(5)
        self.mainbox.Add(runbox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        self.mainbox.Add(paramfilebox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)	
        self.mainbox.AddSpacer(2)

        self.panel.Layout()



class OsmoModel(ModThread):
    def __init__(self, mod):
        ModThread.__init__(self, mod.modbox, mod.mainwin)

        self.mod = mod
        self.osmobox = mod.osmobox
        #self.osmodata = mod.osmodata
        self.mainwin = mod.mainwin
        self.scalebox = mod.mainwin.scalebox

        self.randomflag = True


    def run(self):
        print("OsmoModel thread running")

        if self.randomflag: random.seed(0)
        else: random.seed(datetime.now())

        self.osmomodel()

        wx.QueueEvent(self.mod, ModThreadEvent(ModThreadCompleteEvent))

        #self.scalebox.GraphUpdate()


    def osmomodel(self):
        osmoparams = self.mod.osmobox.GetParams()

        runtime = int(osmoparams["runtime"])
        waterloss = osmoparams["waterloss"]

        print("runtime {}".format(runtime))
        print("waterloss {}".format(waterloss))



