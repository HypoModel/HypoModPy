

import wx
import random
import numpy as np

from hypomods import *
from hypoparams import *
from hypodat import *
from hypogrid import *
from spikedat import *


class SpikeMod(Mod):
    def __init__(self, mainwin, tag):
        Mod.__init__(self, mainwin, tag)

        if mainwin.modpath != "": self.path = mainwin.modpath + "/Spike"
        else: self.path = "Spike"

        if os.path.exists(self.path) == False: 
            os.mkdir(self.path)

        self.mainwin = mainwin

        self.gridbox = GridBox(self, "Data Grid", wx.Point(0, 0), wx.Size(320, 500), 100, 20)
        self.spikebox = SpikeBox(self, "spike", "Spike", wx.Point(0, 0), wx.Size(320, 500))
        #self.neurobox = NeuroBox(self, "spikedata", "Spike Data", wx.Point(0, 0), wx.Size(320, 500))

        self.gridbox.NeuroButton()

        # link mod owned boxes
        mainwin.gridbox = self.gridbox

        self.modtools[self.spikebox.boxtag] = self.spikebox
        self.modtools[self.gridbox.boxtag] = self.gridbox
        #self.modtools[self.neurobox.boxtag] = self.neurobox

        self.spikebox.Show(True)
        self.modbox = self.spikebox

        mainwin.toolset.AddBox(self.spikebox)  
        mainwin.toolset.AddBox(self.gridbox)  
        #mainwin.toolset.AddBox(self.neurobox)  

        self.ModLoad()
        print("Spike Model OK")

        self.celldata = []
        #self.celldata = NeuroDat()

        self.cellspike = SpikeDat()
        self.modspike = SpikeDat()
        self.PlotData()
        self.graphload = True


    ## PlotData() defines all the available plots, each linked to a data array in osmodata
    ##
    def PlotData(self):
        # Data plots
        #
        # AddPlot(PlotDat(data array, xfrom, xto, yfrom, yto, label string, plot type, bin size, colour), tag string)
        # ----------------------------------------------------------------------------------
        self.plotbase.AddPlot(PlotDat(self.cellspike.hist5, 0, 2000, 0, 500, "Hist 5ms", "line", 1, "blue"), "datahist")
        self.plotbase.AddPlot(PlotDat(self.cellspike.haz1, 0, 2000, 0, 100, "datahaz", "line", 1, "blue"), "datahaz")
        self.plotbase.AddPlot(PlotDat(self.modspike.hist1, 0, 2000, 0, 100, "modhist", "line", 1, "green"), "modhist")
        self.plotbase.AddPlot(PlotDat(self.modspike.haz1, 0, 2000, 0, 100, "modhaz", "line", 1, "green"), "modhaz")


    def DefaultPlots(self):
        if len(self.mainwin.panelset) > 0: self.mainwin.panelset[0].settag = "datahist"
        if len(self.mainwin.panelset) > 1: self.mainwin.panelset[1].settag = "datahaz"
        if len(self.mainwin.panelset) > 2: self.mainwin.panelset[2].settag = "modhist"


    def NeuroData(self):
        DiagWrite("NeuroData() call\n")

        self.cellindex = 0
        self.cellspike.Analysis(self.celldata[self.cellindex])
        self.cellspike.id = self.cellindex
        self.cellspike.name = self.celldata[self.cellindex].name

        self.mainwin.scalebox.GraphUpdateAll()


    def OnModThreadComplete(self, event):
        self.mainwin.scalebox.GraphUpdateAll()
        #DiagWrite("Model thread OK\n\n")


    def RunModel(self):
        self.mainwin.SetStatusText("Spike Model Run")
        modthread = SpikeModel(self)
        modthread.start()


class SpikeModel(ModThread):
    def __init__(self, mod):
        ModThread.__init__(self, mod.modbox, mod.mainwin)

        self.mod = mod
        self.spikebox = mod.spikebox
        self.mainwin = mod.mainwin
        self.scalebox = mod.mainwin.scalebox

    # Run() is the thread entry function, used to initialise and call the main Model() function   
    def Run(self):
        # Read model flags
        self.randomflag = self.osmobox.modflags["randomflag"]      # model flags are useful for switching elements of the model code while running

        if self.randomflag: random.seed(0)
        else: random.seed(datetime.now().microsecond)

        self.Model()
        wx.QueueEvent(self.mod, ModThreadEvent(ModThreadCompleteEvent))

    # Model() reads in the model parameters, initialises variables, and runs the main model loop
    def Model(self):
        spikedata = self.modspike
        spikebox = self.spikebox
        params = self.spikebox.GetParams()
        #protoparams = self.mod.protobox.GetParams()

        # Read parameters
        runtime = int(params["runtime"])
        Vthresh = params["Vthresh"]
        Vrest = params["Vrest"]

        # Initialise variables
        V = Vrest
        Vinput = 0
        HAP = 0

        # Run model loop
        for i in range(1, runtime + 1):
            if i%100 == 0: spikebox.SetCount(i * 100 / runtime)     # Update run progress % in model panel

            


class SpikeBox(ParamBox):
    def __init__(self, mod, tag, title, position, size):
        ParamBox.__init__(self, mod, title, position, size, tag, 0, 1)

        self.autorun = False

        # Initialise Menu 
        self.InitMenu()

        # Model Flags
        ID_randomflag = wx.NewIdRef()   # request a new control ID
        self.AddFlag(ID_randomflag, "randomflag", "Fixed Random Seed", 0)  # menu accessed flags for switching model code


        # Parameter controls
        #
        # AddCon(tag string, display string, initial value, click increment, decimal places)
        # ----------------------------------------------------------------------------------
        self.paramset.AddCon("runtime", "Run Time", 2000, 1, 0)
        self.paramset.AddCon("hstep", "h Step", 1, 0.1, 1)
        self.paramset.AddCon("Vrest", "Vrest", -62, 0.1, 2)
        self.paramset.AddCon("Vthresh", "Vthresh", -50, 0.1, 2)
        self.paramset.AddCon("Ire", "Ire", 300, 1, 0)
        self.paramset.AddCon("Iratio", "Iratio", 1, 0.1, 2)
        self.paramset.AddCon("pspmag", "pspmag", 3, 0.1, 2)
        self.paramset.AddCon("kHAP", "kHAP", 60, 0.1, 2)
        self.paramset.AddCon("halflifeHAP", "halflifeHAP", 8, 0.1, 2)

        self.ParamLayout(2)   # layout parameter controls in two columns

        # ----------------------------------------------------------------------------------

        runbox = self.RunBox()
        paramfilebox = self.StoreBoxSync()


        ID_Grid = wx.NewIdRef()
        self.AddPanelButton(ID_Grid, "Grid", self.mod.gridbox)

        self.mainbox.AddSpacer(5)
        self.mainbox.Add(self.pconbox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddStretchSpacer(5)
        self.mainbox.Add(runbox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        self.mainbox.Add(paramfilebox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)	
        #self.mainbox.AddStretchSpacer()
        self.mainbox.Add(self.buttonbox, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        #self.mainbox.AddSpacer(2)
        self.panel.Layout()


class NeuroBox(ParamBox):
    def __init__(self, mod, tag, title, position, size):
        ParamBox.__init__(self, mod, title, position, size, tag, 0, 1)

        self.autorun = True

        # Initialise Menu 
        #self.InitMenu()

        # Model Flags
    

        # Parameter controls
        #
        # AddCon(tag string, display string, initial value, click increment, decimal places)
        # ----------------------------------------------------------------------------------
        self.paramset.AddCon("drinkstart", "Drink Start", 0, 1, 0)
        self.paramset.AddCon("drinkstop", "Drink Stop", 0, 1, 0)
        self.paramset.AddCon("drinkrate", "Drink Rate", 10, 1, 0)

        self.ParamLayout(3)   # layout parameter controls in two columns

        # ----------------------------------------------------------------------------------

        self.mainbox.AddSpacer(5)
        self.mainbox.Add(self.pconbox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddStretchSpacer(5)
        self.mainbox.AddSpacer(2)
        self.panel.Layout()
