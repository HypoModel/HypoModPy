
import wx
from hypobase import *



class ToolPanel(wx.Panel):
    def __init__(self, toolbox, pos, size):
        wx.Panel.__init__(self, toolbox, wx.ID_ANY, pos, size)
        self.toolbox = toolbox
        #self.mainwin = toolbox.mainwin
        self.PanelInit()

    def PanelInit(self):
        if GetSystem() == 'Mac':
            self.buttonheight = 25
            self.boxfont = wx.Font(wx.FontInfo(12).FaceName("Tahoma"))
            self.confont = wx.Font(wx.FontInfo(10).FaceName("Tahoma"))
        else:
            self.buttonheight = 23
            self.boxfont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))
            self.confont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))

        #self.Bind(wx.EVT_LEFT_UP, self.OnLeftClick)
        #self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        #self.Bind(wx.EVT_RIGHT_DCLICK, self.OnRightDClick)
	




# alt style = wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_TOOL_WINDOW | wx.CAPTION | wx.RESIZE_BORDER

class ToolBox(wx.Frame):
    def __init__(self, parent, tag, title, pos, size, 
    style = wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_TOOL_WINDOW | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX):
        wx.Frame.__init__(self, parent, title = title, pos = pos, size = size, style = style)
        self.panel = wx.Panel()
        self.boxtag = tag
        self.BoxInit()
        #self.mpos = wx.Point()
        self.mpos = pos
        self.mainwin = parent


    def BoxInit(self):
        self.status = None

        self.buttonheight = 23
        self.boxfont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))
        self.confont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))

        self.panel = ToolPanel(self, wx.DefaultPosition, wx.DefaultSize)
        self.panel.SetFont(self.boxfont)
        self.mainbox = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.mainbox)

        self.selfstore = False
        self.activepanel = self.panel
        #self.paramset.panel = self.panel

        #self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.SetPosition()


    def OnMove(self, event):
        newpos = self.GetPosition()
        newsize = self.GetSize()
        shift = wx.Point()

        shift.x = newpos.x - self.oldpos.x
        shift.y = newpos.y - self.oldpos.y
        
        self.mpos.x = self.mpos.x + shift.x
        self.mpos.y = self.mpos.y + shift.y
        self.oldpos = newpos

        snum = "Box x {} y {} x {} y {}".format(self.mpos.x, self.mpos.y, newpos.x, newpos.y)
        self.mainwin.SetStatus(snum)


    def OnSize(self, event):
        newsize = self.GetSize()
        pos = self.GetPosition()

        snum = "Box Size X {} Y {}".format(newsize.x, newsize.y)
        self.mainwin.SetStatus(snum)

        self.boxsize = newsize
        wx.Frame.OnSize(event)


    def SetPosition(self):
        if(self.mainwin):
            mainpos = self.mainwin.GetPosition()
            mainsize = self.mainwin.GetSize()
        else:
            mainpos = wx.Point(0, 0)
            mainsize = wx.Size(0, 0)

        self.Move(mainpos.x + mainsize.x + self.mpos.x, mainpos.y + self.mpos.y + 5)
        self.oldpos = self.GetPosition()
        
        return wx.Point(mainpos.x + mainsize.x + self.mpos.x, mainpos.y + self.mpos.y + 5)



class ParamSet:
    con = {}
    paramstore = {}
