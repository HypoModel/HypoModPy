

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

        # link mod owned boxes
        mainwin.gridbox = self.gridbox

        self.modtools[self.spikebox.boxtag] = self.spikebox
        self.modtools[self.gridbox.boxtag] = self.gridbox

        self.spikebox.Show(True)
        self.modbox = self.spikebox

        mainwin.toolset.AddBox(self.spikebox)  
        mainwin.toolset.AddBox(self.gridbox)  

        self.ModLoad()
        print("Spike Model OK")

        self.celldata = SpikeDat()
        self.moddata = SpikeDat()
        self.PlotData()
        self.graphload = True


    ## PlotData() defines all the available plots, each linked to a data array in osmodata
    ##
    def PlotData(self):
        # Data plots
        #
        # AddPlot(PlotDat(data array, xfrom, xto, yfrom, yto, label string, plot type, bin size, colour), tag string)
        # ----------------------------------------------------------------------------------
        self.plotbase.AddPlot(PlotDat(self.celldata.hist1, 0, 2000, 0, 5000, "datahist", "line", 1, "blue"), "datahist")
        self.plotbase.AddPlot(PlotDat(self.celldata.haz1, 0, 2000, 0, 100, "datahaz", "line", 1, "blue"), "datahaz")
        self.plotbase.AddPlot(PlotDat(self.moddata.hist1, 0, 2000, 0, 100, "modhist", "line", 1, "green"), "modhist")
        self.plotbase.AddPlot(PlotDat(self.moddata.haz1, 0, 2000, 0, 100, "modhaz", "line", 1, "green"), "modhaz")


    def DefaultPlots(self):
        if len(self.mainwin.panelset) > 0: self.mainwin.panelset[0].settag = "datahist"
        if len(self.mainwin.panelset) > 1: self.mainwin.panelset[1].settag = "datahaz"
        if len(self.mainwin.panelset) > 2: self.mainwin.panelset[2].settag = "modhist"







class SpikeBox(ParamBox):
    def __init__(self, mod, tag, title, position, size):
        ParamBox.__init__(self, mod, title, position, size, tag, 0, 1)

        self.autorun = True

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
        self.paramset.AddCon("waterloss", "Water Loss", 0, 0.00001, 5)

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
