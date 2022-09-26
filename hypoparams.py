
import wx
from hypocontrols import *



class ParamCon(wx.Control):
    def __init__(self, panel, type, tag, labeltext, initval, step=0, places=0, labelwidth=60, numwidth=45):
        ostype = GetSystem()
        wx.Control.Create(panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE)
        self.numstep = step
        self.tag = tag
        self.labeltext = labeltext
        self.decimals = places
        self.type = type
        self.labelwidth = labelwidth
        self.numwidth = numwidth
        self.panel = panel
        self.pad = panel.controlborder
        self.cycle = 0

        if ostype == 'Mac': pad = 0

        textfont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))

        if ostype == 'Mac':
            textfont = wx.Font(wx.FontInfo(11).FaceName("Tahoma"))
            smalltextfont = wx.Font(wx.FontInfo(9).FaceName("Tahoma"))

        self.min = 0
        self.max = 1000000

        if type == 'numcon' or type == 'spincon':
            if initval < 0: min = -1000000
            if initval < min: min = initval * 10
            if initval > max: max = initval * 100
            oldvalue = initval
            inittext = numstring(initval, places)
        else:
            inittext = initval

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        if label == "":
            label = None
            self.labelwidth = 0
        else:
            label = ToolText(self, panel.toolbox, tag, labeltext, wx.DefaultPosition, wx.Size(labelwidth, -1), wx.ALIGN_CENTRE)
            label.SetFont(textfont)

        if ostype == 'Mac' and labelwidth < 40: label.SetFont(smalltextfont)
        sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, pad)

        self.numbox = wx.TextCtrl(self, wx.ID_ANY, inittext, wx.DefaultPosition, wx.Size(numwidth, -1), wx.TE_PROCESS_ENTER)
        self.numbox.SetFont(textfont)
        sizer.Add(self.numbox, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, pad)

        if type == 'spincon':
            self.spin = wx.SpinButton(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(17, 23), wx.SP_VERTICAL|wx.SP_ARROW_KEYS);  # 21
            self.spin.SetRange(-1000000, 1000000)
            sizer.Add(self.spin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
            self.spin.Bind(wx.EVT_SPIN_UP, self.OnSpinUp)
            self.spin.Bind(wx.EVT_SPIN_DOWN, self.OnSpinDown)
            self.spin.Bind(wx.EVT_SPIN, self.OnSpin)

        self.SetInitialSize(wx.DefaultSize)
        self.Move(wx.DefaultPosition)
        self.SetSizer(sizer)
        self.Layout()

        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)


    def Select(self):
        self.panel.toolbox.TextClick(self.tag)


    def GetValue(self):
        if type == 'textcon': return 0
        value = self.numbox.GetValue()
        return float(value)


    def GetString(self):
        return self.numbox.GetValue()


    def SetPen(self, pen):
        self.numbox.SetForegroundColour(pen)


    def SetValue(self, value):
        if(type == 'textcon'): snum = value
        else: snum = numstring(value, self.decimals)
        self.numbox.SetValue(snum)


    def SetMinMax(self, newmin, newmax, newcycle):
        self.min = newmin
        self.max = newmax
        self.cycle = newcycle


    def DoGetBestSize(self): 
        if GetSystem() == 'Mac':
            if self.type == 'spincon': return wx.Size(self.numwidth + self.labelwidth + self.pad * 2 + 17, 23)
            else: return wx.Size(self.numwidth + self.labelwidth + self.pad * 2, 20)

        if self.type == 'spincon': return wx.Size(self.numwidth + self.labelwidth + 17, 25)
        else: return wx.Size(self.numwidth + self.labelwidth + self.pad * 2, 21 + self.pad * 2)


    def OnSpin(self, event):
        if not self.panel.toolbox == None:
            pub.sendMessage("diagbox", message="tool spin click\n")
            self.panel.toolbox.SpinClick(self.tag)
        event.Skip()

    
    def OnEnter(self, event):
        if not self.panel.toolbox == None:
            pub.sendMessage("diagbox", message="tool box enter\n")
            self.panel.toolbox.BoxEnter(self.tag)
        event.Skip()

    
    def OnSpinUp(self, event):
        value = self.numbox.GetValue()
        newvalue = value + self.numstep
        if newvalue > max:
            if self.cycle: newvalue = min + (newvalue - max) - 1
            else: return
        snum = numstring(newvalue, self.decimals)
        self.numbox.SetValue(snum)


    def OnSpinDown(self, event):
        value = self.numbox.GetValue()
        newvalue = value - self.numstep
        if newvalue < min: 
            if self.cycle: newvalue = max + (newvalue - min) + 1
        else: return
        snum = numstring(newvalue, self.decimals)
        self.numbox.SetValue(snum)
        


class ParamSet:
    def __init__(self, panel):
        self.con = {}
        self.paramstore = {}
        self.panel = panel
        # currlay = 0;

        # Default field widths
        self.num_labelwidth = 65
        self.num_numwidth = 40
        self.con_labelwidth = 60
        self.con_numwidth = 60
        self.text_labelwidth = 60
        self.text_textwidth = 150


    def SetMinMax(self, tag, min, max):
        self.con[tag].min = min
        self.con[tag].max = max


    def GetCon(self, tag):
        if not tag in self.con:
            pub.sendMessage("diagbox", message="ParamSet GetCon " + tag + " not found\n")
            return None
        else: return self.con[tag]


    def AddCon(self, tag, label, initval, step, places, labelwidth=-1, numwidth=-1): 
        if labelwidth < 0: labelwidth = self.con_labelwidth
        if numwidth < 0: numwidth = self.con_numwidth

        self.con[tag] = ParamCon(self.panel, 'spincon', tag, label, initval, step, places, labelwidth, numwidth);   # number + spin
        return self.con[tag]


    def AddNum(self, tag, label, initval, places, labelwidth=-1, numwidth=-1):
        if labelwidth < 0: labelwidth = self.num_labelwidth
        if numwidth < 0: numwidth = self.num_numwidth

        self.con[tag] = ParamCon(self.panel, 'numcon', tag, label, initval, 0, places, labelwidth, numwidth);   # number
        return self.con[tag]


    def AddText(self, tag, label, initval, labelwidth=-1, textwidth=-1):
        if labelwidth < 0: labelwidth = self.text_labelwidth
        if numwidth < 0: numwidth = self.text_numwidth

        self.con[tag] = ParamCon(self.panel, 'textcon', tag, label, initval, labelwidth, textwidth)     # text
        return self.con[tag]

    
    def SetValue(self, tag, value):
        self.con[tag].SetValue(value)


    def GetValue(self, tag):
        if not tag in self.con: return 0
        value = self.con[tag].GetValue()
        return float(value)


    def GetText(self, tag):
        text = self.con[tag].GetString()
        return text

    
    def GetParams(self):
        for pcon in self.con:
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



class ParamBox(ToolBox):
    def __init__(self, mod, title, pos, size, tag, type = 0, storemode = 0):
        ToolBox.__init__(mod.mainwin, tag, title, pos, size, type)
        
        self.autorun = 0    # auto run model after parameter change
        self.redtag = ""    # store box overwrite warning tag
        self.histmode = 0
        self.storemode = storemode
        self.mod = mod   # parent model      
        self.boxtype = type   # 0 - basic panel, 1 - AUI panel
        self.status = None
        #defbutt = 0;
        #defstore = false;
        self.diagmode = 0   # diagnostic mode
        self.mainwin = mod.mainwin  # main window link
        self.column = 0     # column mode for parameter controls
        self.buttonwidth = 50
        # modmode = 0;

        # model->mainwin->diagbox->Write("ParamBox init\n");

        self.Init()


    def Init(self):
        modparams = {}
        modflags = {}
        conflags = {}


    def ParamLayout(self, columns = 1):                   # Currently for one or two columns, need to generalise
        colsize = 0

        if columns == 1: colsize = self.paramset.numparams
	if(columns == 2) {
		if(!column) colsize = (paramset.numparams+1) / 2;
		else colsize = column; 
	}

	SetVBox(columns);

	for(i=0; i<colsize; i++) {
		vbox[0]->Add(paramset.con[i], 1, wxALIGN_CENTRE_HORIZONTAL|wxALIGN_CENTRE_VERTICAL|wxRIGHT|wxLEFT, 5);
		vbox[0]->AddSpacer(5);
	}
	parambox->Add(vbox[0], 0);

	if(columns == 2) {
		for(i=colsize; i<paramset.numparams; i++) {
			vbox[1]->Add(paramset.con[i], 1, wxALIGN_CENTRE_HORIZONTAL|wxALIGN_CENTRE_VERTICAL|wxRIGHT|wxLEFT, 5);
			vbox[1]->AddSpacer(5);
		}
		parambox->Add(vbox[1], 0);
	}
}
