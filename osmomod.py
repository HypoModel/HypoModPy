
import wx
import random
import numpy as np

from hypomods import *
from hypoparams import *
from hypodat import *

ID_heatflag = wx.NewIdRef()



class OsmoMod(Mod):
    def __init__(self, mainwin, tag):
        Mod.__init__(self, mainwin, tag)

        if modpath != "": self.path = modpath + "/Osmo"
        else: self.path = "Osmo"

        if os.path.exists(self.path) == False: 
            os.mkdir(self.path)

        self.mainwin = mainwin

        self.osmobox = OsmoBox(self, "osmo", "Osmo", wx.Point(0, 0), wx.Size(320, 500))
        self.modtools[self.osmobox.boxtag] = self.osmobox
        self.osmobox.Show(True)
        mainwin.toolset.AddBox(self.osmobox)  
        self.modbox = self.osmobox

        self.ModLoad()
        print("Osmo Model OK")

        self.osmodata = OsmoDat()
        self.PlotData()
        self.graphload = True


    def PlotData(self):
        ## Data plots
        ##
        ## PlotDat(data pointer, xfrom, xto, yfrom, yto, label string, plot type, bin size, colour)
        ## ----------------------------------------------------------------------------------
        self.plotbase.AddPlot(PlotDat(self.osmodata.water, 0, 2000, 0, 5000, "water", "line", 1, "blue"), "water")
        self.plotbase.AddPlot(PlotDat(self.osmodata.salt, 0, 2000, 0, 100, "salt", "line", 1, "red"), "salt")
        self.plotbase.AddPlot(PlotDat(self.osmodata.osmo, 0, 2000, 0, 100, "osmo", "line", 1, "green"), "osmo")
        self.plotbase.AddPlot(PlotDat(self.osmodata.vaso, 0, 2000, 0, 100, "vaso", "line", 1, "purple"), "vaso")


    def DefaultPlots(self):
        self.mainwin.panelset[0].settag = "water"
        self.mainwin.panelset[1].settag = "salt"
        #self.mainwin.panelset[2].settag = "osmo"


    def OnModThreadComplete(self, event):
        #runmute->Lock();
        #runflag = 0;
        #runmute->Unlock();
        self.mainwin.scalebox.GraphUpdateAll()
        #DiagWrite("Model thread OK\n\n")


    def RunModel(self):
        self.mainwin.SetStatusText("Osmo Model Run")
        modthread = OsmoModel(self)
        modthread.start()



class OsmoDat():
    def __init__(self):
        self.storesize = 10000

        self.water = np.zeros(self.storesize + 1)
        self.salt = np.zeros(self.storesize + 1)
        self.osmo = np.zeros(self.storesize + 1)
        self.vaso = np.zeros(self.storesize + 1)



class OsmoBox(ParamBox):
    def __init__(self, model, tag, title, position, size):
        ParamBox.__init__(self, model, title, position, size, tag, 0, 1)

        self.autorun = True

        # Initialise Menu 
        self.InitMenu()

        # Model Flags
        self.AddFlag(ID_randomflag, "randomflag", "Fixed Random Seed", 0)
        #self.AddFlag(ID_heatflag, "heatflag", "Heat Effect", 0)


        # Parameter controls
        #
        # AddCon(tag string, display string, initial value, click increment, decimal places)
        # ----------------------------------------------------------------------------------

        self.paramset.AddCon("runtime", "Run Time", 2000, 1, 0)
        self.paramset.AddCon("hstep", "h Step", 1, 0.1, 1)
        self.paramset.AddCon("waterloss", "Water Loss", 0, 0.00001, 5)

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
        #print("OsmoModel thread running")

        if self.randomflag: random.seed(0)
        else: random.seed(datetime.now())

        self.Model()

        wx.QueueEvent(self.mod, ModThreadEvent(ModThreadCompleteEvent))


    def Model(self):
        osmodata = self.mod.osmodata
        osmobox = self.mod.osmobox
        osmoparams = self.mod.osmobox.GetParams()

        # Read parameters
        runtime = int(osmoparams["runtime"])
        waterloss = osmoparams["waterloss"]

        # Initialise variables
        water = 50
        salt = 2000
        osmo = salt / water

        # Initialise record stores
        for i in range(osmodata.storesize):
            osmodata.water[i] = 0 
            osmodata.salt[i] = 0
            osmodata.osmo[i] = 0

        osmodata.water[0] = water
        osmodata.salt[0] = salt
        osmodata.osmo[0] = osmo
        osmobox.countmark = 0

        # Run model loop
        for i in range(1, runtime + 1):

            if i%100 == 0: self.osmobox.SetCount(i * 100 / runtime)     # Update run progress % in model panel

            water = water - (water * waterloss)
            salt = salt
            osmo = salt / water
            vaso = 0

            # Record model variables
            osmodata.water[i] = water
            osmodata.salt[i] = salt
            osmodata.osmo[i] = osmo






