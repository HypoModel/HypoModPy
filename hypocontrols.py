
import wx
from hypobase import *
from pubsub import pub



class ToolPanel(wx.Panel):
    def __init__(self, toolbox, pos, size, style = wx.TAB_TRAVERSAL | wx.NO_BORDER):
        wx.Panel.__init__(self, toolbox, wx.ID_ANY, pos, size, style)
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

        self.boxtag = tag
        self.mpos = pos - parent.GetPosition() 
        self.oldpos = pos
        self.boxsize = size
        self.status = None
        self.canclose = False
        self.visible = True

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

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.SetPosition(parent.GetPosition(), parent.GetSize())


    def SetPosition(self, mainpos, mainsize):
        self.Move(mainpos.x + mainsize.x + self.mpos.x, mainpos.y + self.mpos.y + 5)
        self.oldpos = self.GetPosition()
        return wx.Point(mainpos.x + mainsize.x + self.mpos.x, mainpos.y + self.mpos.y + 5)


    def OnMove(self, event):
        if self.IsActive():
            newpos = self.GetPosition()
            newsize = self.GetSize()
           
            shift = newpos - self.oldpos
        
            self.mpos.x = self.mpos.x + shift.x
            self.mpos.y = self.mpos.y + shift.y
            self.oldpos = newpos

            snum = "Box mpos x {} y {} shift x {} y {}".format(self.mpos.x, self.mpos.y, shift.x, shift.y)
            pub.sendMessage("status_listener", message=snum)


    def OnSize(self, event):
        event.Skip()
        newsize = self.GetSize()
        pos = self.GetPosition()

        snum = "Box Size X {} Y {}".format(newsize.x, newsize.y)
        pub.sendMessage("status_listener", message=snum)

        self.boxsize = newsize


    def OnClose(self, event):
        if self.canclose == False:
            self.Show(False)
        else:
            pub.sendMessage("toolclose_listener", message=self.boxtag)
            event.Skip()
    


class ParamSet:
    con = {}
    paramstore = {}



class TextBox(wx.TextCtrl):
    def __init__(self, parent, id, value, pos, size, style):
        wx.TextCtrl.__init__(self, parent, id, value, pos, size, style)
        self.val = 0
