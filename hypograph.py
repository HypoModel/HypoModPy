
import wx

class GraphDisp():
    def __init__(self):
        self.numplots = 0
        self.currentplot = 0



class GraphPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)
        self.numdisps = 0
        self.frontdisp = 0
        self.dispset = []
        wx.StaticText(self, label='GraphPanel')


    def FrontGraph(self, graphdisp):
        if len(self.dispset) == 0: 
            self.dispset.append(graphdisp)
        else:
            self.dispset[0] = graphdisp
            
        

class ScaleBox(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_SIMPLE)
        wx.StaticText(self, label='ScaleBox')
