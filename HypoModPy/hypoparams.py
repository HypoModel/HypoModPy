
import wx
from HypoModPy.hypobase import *
from pubsub import pub


class ParamText(wx.StaticText):
    def __init__(self, parent, toolbox, tag, label, pos, size, style):
        wx.StaticText.__init__(self, parent, wx.ID_ANY, label, pos, size, style)
        self.toolbox = toolbox
        self.tag = tag

        self.Bind(wx.EVT_LEFT_UP, self.OnLeftClick)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self.Bind(wx.EVT_RIGHT_DCLICK, self.OnRightDClick)


    def OnLeftDClick(self, event):
        if self.toolbox: 
            self.toolbox.pinmode = 1 - self.toolbox.pinmode
            pub.sendMessage("diagbox", message=f"LDClick pin {self.toolbox.pinmode}\n")


    def OnRightDClick(self, event):
        if self.toolbox:
            self.toolbox.pinmode = 1 - self.toolbox.pinmode
            pub.sendMessage("diagbox", message=f"RDClick pin {self.toolbox.pinmode}\n")
            

    def OnLeftClick(self, event):
        if self.toolbox:
            pub.sendMessage("diagbox", message="text click\n")
            self.toolbox.activepanel.OnClick(event.GetPosition())
            self.toolbox.TextClick(self.tag)



class ParamCon(wx.Control):
    def __init__(self, panel, type, tag, labeltext, initval, step=0, places=0, labelwidth=60, datawidth=45):
        ostype = GetSystem()
        wx.Control.__init__(self, panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE)
        self.numstep = step
        self.tag = tag
        self.labeltext = labeltext
        self.decimals = places
        self.type = type
        self.labelwidth = labelwidth
        self.datawidth = datawidth
        self.buttonwidth = 0
        self.panel = panel
        self.pad = panel.controlborder
        self.cycle = False
        self.oldvalue = initval

        self.diagmode = False

        if ostype == "Mac": pad = 0
        else: pad = 0

        textfont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))

        if ostype == "Mac":
            textfont = wx.Font(wx.FontInfo(11).FaceName("Tahoma"))
            smalltextfont = wx.Font(wx.FontInfo(9).FaceName("Tahoma"))

        self.min = 0
        self.max = 1000000

        if type == 'numcon' or type == 'spincon':
            if initval < 0: self.min = -1000000
            if initval < self.min: self.min = initval * 10
            if initval > self.max: self.max = initval * 100
            oldvalue = initval
            inittext = numstring(initval, places)
        else:
            inittext = initval

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        if labeltext == "":
            self.label = None
            self.labelwidth = 0
        else:
            self.label = ParamText(self, panel.parent, tag, labeltext, wx.DefaultPosition, wx.Size(labelwidth, -1), wx.ALIGN_CENTRE)
            self.label.SetFont(textfont)

        #if ostype == 'Mac' and labelwidth < 40: label.SetFont(smalltextfont)
        self.sizer.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, pad)

        #if type == "textcon": print(f"ParamCon init: {initval}")

        self.numbox = wx.TextCtrl(self, wx.ID_ANY, inittext, wx.DefaultPosition, wx.Size(datawidth, -1), wx.TE_PROCESS_ENTER)
        self.numbox.SetFont(textfont)
        self.sizer.Add(self.numbox, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, pad)

        if type == 'spincon':
            self.spin = wx.SpinButton(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(17, 23), wx.SP_VERTICAL|wx.SP_ARROW_KEYS);  # 21
            self.spin.SetRange(-1000000, 1000000)
            self.sizer.Add(self.spin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
            self.spin.Bind(wx.EVT_SPIN_UP, self.OnSpinUp)
            self.spin.Bind(wx.EVT_SPIN_DOWN, self.OnSpinDown)
            self.spin.Bind(wx.EVT_SPIN, self.OnSpin)

        self.SetInitialSize(wx.DefaultSize)
        self.Move(wx.DefaultPosition)
        self.SetSizer(self.sizer)
        self.Layout()

        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        self.numbox.Bind(wx.EVT_SET_FOCUS, self.OnTextFocus)


    def AddButton(self, label, id, width):
        self.buttonwidth = width
        self.button = wx.Button(self, id, label, wx.DefaultPosition, wx.Size(self.buttonwidth, 25))
        self.button.SetFont(self.panel.confont)
        self.sizer.Add(self.button, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.TOP|wx.BOTTOM, 2)
        #self.SetInitialSize(wx.DefaultSize)
        self.Layout()
        return self.button
    

    def OnTextFocus(self, event):
        self.numbox.SetInsertionPointEnd()
        event.Skip()
    

    def DoGetBestSize(self):
        return wx.Size(self.labelwidth + self.datawidth + self.buttonwidth, 25)


    def Select(self):
        self.panel.toolbox.TextClick(self.tag)


    def GetValue(self):
        if self.type == 'textcon': return 0
        value = self.numbox.GetValue()
        if not isfloat(value): return 0
        return float(value)


    def GetText(self):
        return self.numbox.GetValue()


    def SetText(self, text):
        return self.numbox.SetValue(text)

    
    def Clear(self):
        return self.numbox.SetValue("")


    def SetPen(self, pen):
        self.numbox.SetForegroundColour(pen)


    def SetValue(self, value):
        if self.type == 'textcon': snum = value
        else: snum = numstring(value, self.decimals)
        self.numbox.SetValue(snum)


    def SetMinMax(self, newmin, newmax, cycle = False):
        self.min = newmin
        self.max = newmax
        self.cycle = cycle


    def DoGetBestSize(self): 
        if GetSystem() == 'Mac':
            if self.type == 'spincon': return wx.Size(self.datawidth + self.labelwidth + self.pad * 2 + 17, 23)
            else: return wx.Size(self.datawidth + self.labelwidth + self.pad * 2, 20)

        if self.type == 'spincon': return wx.Size(self.datawidth + self.labelwidth + 17, 25)
        else: return wx.Size(self.datawidth + self.labelwidth + self.pad * 2, 21 + self.pad * 2)


    def OnSpin(self, event):
        if self.panel.toolbox is not None:
            if self.diagmode: pub.sendMessage("diagbox", message="tool spin click\n")
            self.panel.toolbox.SpinClick(self.tag)
        event.Skip()

    
    def OnEnter(self, event):
        if self.panel.toolbox is not None:
            pub.sendMessage("diagbox", message="tool box enter\n")
            self.panel.toolbox.BoxEnter(self.tag)
        event.Skip()

    
    def OnSpinUp(self, event):
        value = float(self.numbox.GetValue())
        newvalue = value + self.numstep
        if newvalue > self.max:
            if self.cycle: newvalue = self.min + (newvalue - self.max) - 1
            else: return
        snum = numstring(newvalue, self.decimals)
        self.numbox.SetValue(snum)


    def OnSpinDown(self, event):
        value = float(self.numbox.GetValue())
        newvalue = value - self.numstep
        #snum = "SpinDown value {} newvalue {} min {}\n".format(value, newvalue, self.min)
        #pub.sendMessage("diagbox", message=snum)
        if newvalue < self.min: 
            if self.cycle: newvalue = self.max + (newvalue - self.min) + 1
            else: return
        snum = numstring(newvalue, self.decimals)
        self.numbox.SetValue(snum)
        


class ParamSet:
    def __init__(self, panel):
        self.pcons = {}         # parameter controls
        self.paramstore = {}    # parameter value store
        self.panel = panel      # ToolPanel link
        self.currlay = 0        # layout counter for use with multiple ParamLayout calls

        # Default field widths
        self.num_labelwidth = 65
        self.num_numwidth = 40
        self.con_labelwidth = 60
        self.con_numwidth = 60
        self.text_labelwidth = 60
        self.text_numwidth = 150


    def Check(self, tag):
        return tag in self.pcons


    def NumParams(self):
        return len(self.pcons)


    def SetMinMax(self, tag, min, max):
        self.pcons[tag].min = min
        self.pcons[tag].max = max


    def GetCon(self, tag):
        if not tag in self.pcons:
            pub.sendMessage("diagbox", message="ParamSet GetCon " + tag + " not found\n")
            return None
        else: return self.pcons[tag]


    def AddCon(self, tag, label, initval, step, places, labelwidth=-1, numwidth=-1): 
        if labelwidth < 0: labelwidth = self.con_labelwidth
        if numwidth < 0: numwidth = self.con_numwidth
        self.pcons[tag] = ParamCon(self.panel, 'spincon', tag, label, initval, step, places, labelwidth, numwidth);   # number + spin
        return self.pcons[tag]


    def AddNum(self, tag, label, initval, places, labelwidth=-1, numwidth=-1):
        if labelwidth < 0: labelwidth = self.num_labelwidth
        if numwidth < 0: numwidth = self.num_numwidth
        self.pcons[tag] = ParamCon(self.panel, 'numcon', tag, label, initval, 0, places, labelwidth, numwidth);   # number
        return self.pcons[tag]


    def AddText(self, tag, label, initval, labelwidth=-1, textwidth=-1):
        if labelwidth < 0: labelwidth = self.text_labelwidth
        if textwidth < 0: textwidth = self.text_numwidth
        self.pcons[tag] = ParamCon(self.panel, 'textcon', tag, label, initval, labelwidth=labelwidth, datawidth=textwidth)     # text
        return self.pcons[tag]

    
    def SetValue(self, tag, value):
        self.pcons[tag].SetValue(value)


    def GetValue(self, tag):
        if not tag in self.pcons: return 0
        value = self.pcons[tag].GetValue()
        return float(value)


    def GetText(self, tag):
        text = self.pcons[tag].GetString()
        return text

    
    def GetParams(self):
        for pcon in self.pcons.values():
            value = pcon.GetValue()
            if value < pcon.min:
                value = pcon.oldvalue
                pcon.SetValue(value)

            if value > pcon.max or value > pcon.max:
                value = pcon.oldvalue
                pcon.SetValue(value)

            self.paramstore[pcon.tag] = value
            pcon.oldvalue = value

        return self.paramstore



