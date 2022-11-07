
import wx
from hypomod import *
from hypoparams import *



class OsmoBox(ParamBox):
    def __init__(self, model, title, position, size):
        ParamBox.__init__(self, model, title, position, size, "Osmo", 0, 0)

        # Parameter controls
        #
        # AddCon(tag string, display string, initial value, click increment, decimal places)
        # ----------------------------------------------------------------------------------

        self.paramset.AddCon("runtime", "Run Time", 2000, 1, 0)
        self.paramset.AddCon("hstep", "h Step", 1, 0.1, 1)
        self.paramset.AddCon("waterloss", "Water Loss", 0, 0.001, 4)

        self.ParamLayout(2)

        # ----------------------------------------------------------------------------------

        runbox = wx.BoxSizer(wx.HORIZONTAL)
        runcount = self.NumPanel(50, wx.ALIGN_CENTRE, "---")
        self.AddButton(ID_Run, "RUN", 70, runbox)
        runbox.AddSpacer(5)
        runbox.Add(runcount)

        paramfilebox = self.StoreBoxSync()

        self.mainbox.AddSpacer(5)
        self.mainbox.Add(self.parambox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddStretchSpacer(5)
        self.mainbox.Add(runbox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        self.mainbox.Add(paramfilebox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)	
        self.mainbox.AddSpacer(2)

        self.panel.Layout()



class OsmoModel(Model):
    def __init__(self, mainwin, tag):
        Model.__init__(self, mainwin, tag)

        self.osmobox = OsmoBox(self, tag, wx.Point(0, 0), wx.Size(320, 500))

        #mainwin.toolset.AddBox(self.osmobox)  

