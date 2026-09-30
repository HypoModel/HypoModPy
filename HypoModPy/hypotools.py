
import wx
import os
from HypoModPy.hypobase import *
from HypoModPy.hypoparams import ParamSet



class ToolPanel(wx.Panel):
    def __init__(self, parent, pos, size, style = wx.TAB_TRAVERSAL | wx.NO_BORDER):
        wx.Panel.__init__(self, parent, wx.ID_ANY, pos, size, style)

        self.parent = parent
        self.toolbox = None
        self.controlborder = 2

        self.blackpen = wx.Colour("#000000")
        self.redpen = wx.Colour("#dd0000")
        self.greenpen = wx.Colour("#009900")
        self.bluepen = wx.Colour("#0000dd")

        self.PanelInit()


    def PanelInit(self):
        if GetSystem() == 'Mac':
            self.buttonheight = 25
            self.boxfont = wx.Font(wx.FontInfo(12).FaceName("Tahoma"))
            self.confont = wx.Font(wx.FontInfo(11).FaceName("Tahoma"))
        else:
            self.buttonheight = 23
            self.boxfont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))
            self.confont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))

        self.Bind(wx.EVT_LEFT_UP, self.OnLeftClick)
        #self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        #self.Bind(wx.EVT_RIGHT_DCLICK, self.OnRightDClick)


    def OnLeftClick(self, event):
        if type(self.parent) is ToolBox:
            pos = self.parent.GetPosition()
            oldpos = self.parent.oldpos
            mpos = self.parent.mpos
            tag = self.parent.tag
            DiagWrite(f"{tag} pos {pos.x} {pos.y} old {oldpos.x} {oldpos.y} mpos {mpos.x} {mpos.y}\n")
            
        event.Skip()


    def ToggleButton(self, label, width, sizer):
        button = wx.ToggleButton(self, wx.ID_ANY, label, wx.DefaultPosition, wx.Size(width, self.buttonheight), 0)
        button.SetFont(self.confont)
        sizer.Add(button, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.TOP|wx.BOTTOM, 1)
        #if box: button.Bind(wx.EVT_TOGGLEBUTTON, box.OnToggle)
        #else: button.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggle)
        return button


    def OnToggle(self, event):
        event.Skip()



class ToolButton(wx.Button):
    def __init__(self, parent, id, label, pos, size):
        wx.Button.__init__(self, parent, id, label, pos, size)
        self.parent = parent
        self.ID = id
        self.linkID = 0

        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)


    def OnLeftUp(self, event):
        linkpress = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.linkID)
        
        if self.linkID != 0:
            linkpress.SetInt(1)
            self.AddPendingEvent(linkpress)
            #diagbox->Write("ToolButton linkpress\n");
        
        event.Skip()

    
    def Press(self):
        press = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.ID)
        self.AddPendingEvent(press)
    


# alt style = wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_TOOL_WINDOW | wx.CAPTION | wx.RESIZE_BORDER

class ToolBox(wx.Frame):
    def __init__(self, parent, tag, title, pos, size, type = 0, 
    style = wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_TOOL_WINDOW | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX):

        wx.Frame.__init__(self, parent, title = title, pos = pos, size = size, style = style)

        self.diagmode = False

        self.tag = tag
        self.boxtag = tag   # duplicate for backwards compatibility after rename
        self.mpos = pos - parent.GetPosition() 
        self.oldpos = pos
        self.size = size
        self.status = None
        self.canclose = False
        self.visible = True
        self.storetag = None
        self.parent = parent
        self.boxtype = type   # 0 - basic panel, 1 - AUI panel

        self.blackpen = wx.Colour("#000000")
        self.redpen = wx.Colour("#dd0000")
        self.greenpen = wx.Colour("#009900")
        self.bluepen = wx.Colour("#0000dd")

        self.mainbox = wx.BoxSizer(wx.VERTICAL)

        if GetSystem() == 'Mac':
            self.buttonheight = 25
            self.boxfont = wx.Font(wx.FontInfo(10).FaceName("Tahoma"))
            self.confont = wx.Font(wx.FontInfo(12).FaceName("Tahoma"))
            self.buttonfont = wx.Font(wx.FontInfo(10).FaceName("Tahoma").Bold())
        else:
            self.buttonheight = 23
            self.boxfont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))
            self.confont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))
            self.buttonfont = wx.Font(wx.FontInfo(8).FaceName("Tahoma").Bold())

        self.panel = ToolPanel(self, wx.DefaultPosition, wx.DefaultSize)
        self.panel.SetFont(self.boxfont)
        self.panel.SetSizer(self.mainbox)
        self.panel.toolbox = self

        self.selfstore = False
        self.activepanel = self.panel
        #self.paramset.panel = self.panel

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ICONIZE, self.OnIconize)

        self.SetPosition(parent.GetPosition(), parent.GetSize())

        # Param system - lifted from model specific ParamBox, allows parameter controls to be added to any ToolBox
        self.paramset = ParamSet(self.panel)
        self.params = {}
        if self.boxtype == 0: self.pconbox = wx.BoxSizer(wx.HORIZONTAL)


    def GetParams(self, pstore = None):
            if pstore is None: pstore = self.params
            for con in self.paramset.pcons.values():
                value = con.GetValue()
                if value < con.min:
                    value = con.oldvalue
                    con.SetValue(value)
                    if con.label is not None:
                        self.SetStatus("Parameter \'{}\' out of range".format(con.label.GetLabel()))
                        self.DiagWrite("Parameter \'{}\' out of range, min {:.2f} max {:.2f}\n".format(con.label.GetLabel(), con.min, con.max))
    
                if value > con.max:
                    value = con.oldvalue
                    con.SetValue(value)
                    if con.label is not None:
                        self.SetStatus("Parameter {} out of range".format(con.label.GetLabel()))
    
                pstore[con.tag] = value
                con.oldvalue = value
    
            return pstore


    def ParamLayout(self, numcols = 1):                  
            colsize = 0
            numparams = self.paramset.NumParams()
    
            if numcols == 1: colsize = numparams
            if(numcols >= 2):
                colsize = int((numparams + 1) / numcols) 
    
            pstart = 0
            for col in range(numcols):
                if col == numcols-1: pstop = numparams
                else: pstop = colsize * (col+1)
                vbox = wx.BoxSizer(wx.VERTICAL)
                vbox.AddSpacer(5)
                for p in range(pstart, pstop):
                    vbox.Add(list(self.paramset.pcons.values())[p], 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.RIGHT|wx.LEFT, 5)
                    vbox.AddSpacer(5)
                self.pconbox.Add(vbox, 0)
                pstart = pstop


    def VBox(self, num):
            for i in range(num):
                self.vbox[i] = wx.BoxSizer(wx.VERTICAL)
                self.vbox[i].AddSpacer(5)


    def BoxEnter(self, tag):
        if self.diagmode: self.DiagWrite("toolbox boxenter " + tag + "\n")


    def SpinClick(self, tag):
        if self.diagmode: self.DiagWrite("toolbox spinclick  " + tag + "\n")


    def StatusBar(self):
        textcon = wx.StaticText(self.activepanel, wx.ID_ANY, "", wx.DefaultPosition, wx.DefaultSize, 
        wx.ALIGN_CENTRE|wx.BORDER_DOUBLE|wx.ST_NO_AUTORESIZE)
        textcon.SetFont(self.confont)
        return textcon


    def TextLabel(self, label):
        textcon = wx.StaticText(self.activepanel, wx.ID_ANY, label)
        textcon.SetFont(self.confont)
        return textcon


    def TextInput(self, width=80, height=-1, label= "---"):
        textcon = wx.TextCtrl(self.activepanel, wx.ID_ANY, label, wx.DefaultPosition, wx.Size(width, height))
        textcon.SetFont(self.confont)
        return textcon


    def NumPanel(self, width=80, align=wx.ALIGN_RIGHT, label="0"):
        textcon = wx.StaticText(self.activepanel, wx.ID_ANY, label, wx.DefaultPosition, wx.Size(width, -1), 
        align|wx.BORDER_RAISED|wx.ST_NO_AUTORESIZE)
        textcon.SetFont(self.confont)
        return textcon


    def AddButton(self, id, label, width, sizer, pad=1, height=0, panel=None):
        if panel is None: panel = self.activepanel
        if height == 0: height = self.buttonheight
        button = ToolButton(panel, id, label, wx.DefaultPosition, wx.Size(width, height))
        button.SetFont(self.confont)
        sizer.Add(button, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.TOP | wx.BOTTOM, pad)
        return button


    def DiagWrite(self, text):
        pub.sendMessage("diagbox", message=text)


    def InitPosition(self, mpos):
        mainpos = self.parent.GetPosition()
        mainsize = self.parent.GetSize()
        self.Move(mainpos.x + mainsize.x + mpos.x, mainpos.y + mpos.y)   # + 5
        self.oldpos = self.GetPosition()
        self.mpos = mpos

        #snum = f"Box {self.tag} mpos x {self.mpos.x} y {self.mpos.y}"
        #DiagWrite(snum + "\n")


    def SetPosition(self, mainpos, mainsize):
        newpos = wx.Point(mainpos.x + mainsize.x + self.mpos.x, mainpos.y + self.mpos.y)

        if self.GetPosition() != newpos: self.Move(newpos)

        self.oldpos = self.GetPosition()
        return newpos
        
        #self.Move(mainpos.x + mainsize.x + self.mpos.x, mainpos.y + self.mpos.y)
        #self.oldpos = self.GetPosition()
        #return wx.Point(mainpos.x + mainsize.x + self.mpos.x, mainpos.y + self.mpos.y)


    def OnMove(self, event):
        if self.IsActive():
            newpos = self.GetPosition()
            #newsize = self.GetSize()
           
            shift = newpos - self.oldpos
        
            self.mpos.x = self.mpos.x + shift.x
            self.mpos.y = self.mpos.y + shift.y
            self.oldpos = newpos

            snum = f"Box {self.tag} mpos x {self.mpos.x} y {self.mpos.y} shift x {shift.x} y {shift.y}"
            pub.sendMessage("status_listener", message=snum)
            #DiagWrite(snum + "\n")


    def OnSize(self, event):
        event.Skip()
        newsize = self.GetSize()
        #pos = self.GetPosition()
        snum = "Box Size X {} Y {}".format(newsize.x, newsize.y)
        pub.sendMessage("status_listener", message=snum)
        self.size = newsize


    def OnClose(self, event):
        if self.canclose == False:
            self.Show(False)
        else:
            pub.sendMessage("toolclose_listener", message=self.boxtag)
            event.Skip()

    
    def OnIconize(self, event):
        DiagWrite("tool iconize call\n")
        event.Skip()

    

# mpos give the position relative to the main plot window

class ToolDat():
    def __init__(self, tag, mpos, size, visible, box=None):
        self.tag = tag
        self.mpos = mpos
        self.size = size
        self.box = box
        self.visible = visible


class ToolSet():
    def __init__(self):
        self.tools = {}


    def AddBox(self, newbox):
        if newbox.tag in self.tools:
            tool = self.GetTool(newbox.tag)
            tool.box = newbox
            newbox.oldpos = newbox.GetPosition()
            tool.box.SetSize(tool.size)
            tool.box.InitPosition(tool.mpos)
        else:
            self.tools[newbox.tag] = ToolDat(newbox.tag, newbox.GetPosition(), newbox.GetSize(), newbox.IsShown(), newbox)
            

    def AddTool(self, tag, pos, size, visible):
        self.tools[tag] = ToolDat(tag, pos, size, visible)


    def GetTool(self, tag):
        if(tag in self.tools):
            return self.tools[tag]
        return None


    def GetBox(self, tag):
        if(tag in self.tools):
             return self.tools[tag].box
        else:
             return False
             


class TextBox(wx.TextCtrl):
    def __init__(self, parent, id, value, pos, size, style):
        wx.TextCtrl.__init__(self, parent, id, value, pos, size, style)
        
    
    def GetNumValue(self):
        return float(self.GetValue())


    def SetNumValue(self, value, valrange=None):
        if valrange is None: valrange = value
        if valrange < 1:
            self.SetValue("{:.3f}".format(value))
        elif valrange < 10:
            self.SetValue("{:.2f}".format(value))
        elif valrange < 100:
            self.SetValue("{:.1f}".format(value))
        else:
            self.SetValue("{:.0f}".format(value))  


diagbox_target = None

def SetDiagBoxTarget(target):
    global diagbox_target
    diagbox_target = target

def DiagWrite(text):
    if diagbox_target is None:
        return
    diagbox_target.DiagWrite(text)


class DiagBox(ToolBox):
    def __init__(self, parent, title, pos, size):

        ToolBox.__init__(self, parent, "DiagBox", title, pos, size)

        self.textbox = wx.TextCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE)
        self.mainbox.Add(self.textbox, 1, wx.EXPAND)
        self.Bind(EVT_DIAG, self.OnDiagEvent)

    def Write(self, text):
        try:
            self.textbox.AppendText(text)
            return True
        except ValueError:
            return False

    def DiagWrite(self, text):
        evt = DiagEvent(text)
        wx.QueueEvent(self, evt)

    def OnDiagEvent(self, event):
        self.textbox.AppendText(event.text)      



class TagBox(wx.ComboBox):
    def __init__(self, parent, label, size, boxtag, path):
        wx.ComboBox.__init__(self, parent, wx.ID_ANY, label, wx.DefaultPosition, size)

        self.boxtag = boxtag
        self.boxpath = path
        self.redtag = ""
        self.diag = False

        self.PathUpdate()

        #if(diagnostic) mainwin->diagbox->Write(text.Format("TagBox tagpath %s boxpath %s\n", tagpath, boxpath));
        if self.diag: print("TagBox " + path)

        if os.path.exists(self.tagpath) == False: 
            os.mkdir(self.tagpath)

        if self.diag: print("tagpath " + self.tagpath)

        # Read fixed location option file, directs to selectable tagfile location
        opfilepath = self.tagpath + "/" + boxtag + "-op.ini"
        opfile = TextFile(opfilepath)
        check = opfile.Open('r')
        if check == False:
            pub.sendMessage("diagbox", message = "TagBox opfile " + opfilepath + "\n")
            pub.sendMessage("diagbox", message = "TagBox " + boxtag + " No tagpath found, setting default\n")
            self.tagfilename = boxtag + "tags.ini"
        else:
            readline = opfile.ReadLine()
            if readline == "": self.tagfilename = boxtag + "tags.ini"
            else: self.tagfilename = readline.strip()
            opfile.Close()

        #mainwin->diagbox->Write("\nTagBox init " + name + "\n");
        self.HistLoad()

        #Connect(wxEVT_RIGHT_UP, wxMouseEventHandler(TagBox::OnRClick));


    def PathUpdate(self):
        #if self.boxpath == "": 
        #    if projectpath == "": self.tagpath = "Tags"
        #    else: self.tagpath = projectpath + "/Tags"
        #else:
        #    if projectpath == "": self.tagpath = self.boxpath + "/Tags"
        #    else: self.tagpath = projectpath + "/" + self.boxpath + "/Tags"

        
        if self.boxpath == "": self.tagpath = "Tags"
        else: self.tagpath = self.boxpath + "/Tags"

        if os.path.exists(self.tagpath) == False: 
            os.mkdir(self.tagpath)

        if self.diag:
            pub.sendMessage("diagbox", message="TagBox PathUpdate() tagpath {}\n".format(self.tagpath))


    def HistStore(self):
        # Tag history
        if self.tagfilename == "": return
        filepath = self.tagpath + "/" + self.tagfilename
        tagfile = TextFile(filepath)
        tagfile.Open('w')
        if self.GetCount() > 0:
            #print("HistStore count {}".format(self.GetCount()))
            for i in range(0, self.GetCount()):
                #print("HistStore i {}".format(self.GetCount() - i - 1))
                outline = "tag {}".format(self.GetString(self.GetCount() - i - 1))
                tagfile.WriteLine(outline)
        tagfile.Close()

        # Fixed location option file, directs to selectable tagfile location
        opfile = TextFile(self.tagpath + "/" + self.boxtag + "-op.ini")
        opfile.Open('w')
        opfile.WriteLine(self.tagfilename)
        opfile.Close()

        if self.diag: print("HistStore tagfile " + filepath)


    def HistLoad(self):
        diag = False

        tag = ""
        if self.tagpath == "":
            DiagWrite("Tag file not set\n")
            return

        filepath = self.tagpath + "/" + self.tagfilename
        tagfile = TextFile(filepath)
        check = tagfile.Open('r')
        if check == False:
            DiagWrite("No tag history\n")
            return

        if diag: 
            DiagWrite("HistLoad ")
            DiagWrite("Reading tag history " + self.tagfilename + "\n")
        
        filetext = tagfile.ReadLines()
        for readline in filetext:
            readdata = readline.split(' ')
            tag = readdata[1].strip()
            # diagbox->Write("Readline " + readline + "\n");
            self.Insert(tag, 0)
            # diagbox->Write("Insert " + tag + "\n");

        tagfile.Close()	
        self.SetLabel(tag)
        if diag: DiagWrite(self.boxtag + " " + tag + "\n")
        if tag != "": self.labelset = True



class ParamBox(ToolBox):
    def __init__(self, model, title, pos, size, tag, type = 0, storemode = 0):
        ToolBox.__init__(self, model.mainwin, tag, title, pos, size, type)
        diag = False

        self.autorun = 0    # auto run model after parameter change
        self.redtag = ""    # store box overwrite warning tag
        self.histmode = 0
        self.storemode = storemode
        self.mod = model   # parent model      
        self.status = None
        #defbutt = 0;
        #defstore = false;
        self.diag = 0   # diagnostic mode
        self.mainwin = model.mainwin  # main window link
        self.ostype = GetSystem()

        # modmode = 0;
        
        self.activepanel = self.panel
        
        if diag: self.DiagWrite("ParamBox " + self.boxtag + " init\n")

        # Initialise Layout
        self.column = 0     # column mode for parameter controls
        self.buttonwidth = 50
        self.vbox = []
        self.buttonbox = wx.BoxSizer(wx.HORIZONTAL)
        self.panelbuttoncount = 0
        self.defbutt = False

        # Initialise Stores
        self.modflags = {}
        self.conflags = {}
        self.checktags = {}
        self.checkboxes = {}
        self.flagtags = {}
        self.flagIDs = {}
        self.panelrefs = {}
        
        print("ParamBox " + self.mod.path)

        # Store Tag
        self.storetag = None
        if self.storemode:
            if diag: self.DiagWrite("Store Box initialise " + self.tag + "\n")
            self.storetag = TagBox(self.activepanel, "", wx.Size(120, 20), self.tag, self.mod.path)
            self.storetag.Show(False)
            self.storetag.SetFont(self.confont)

        self.Bind(wx.EVT_MENU, self.OnAutoRun, ID_AutoRun)
        self.Bind(wx.EVT_BUTTON, self.OnRun, ID_Run)
        self.Bind(wx.EVT_BUTTON, self.OnDefault, ID_Default)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnRun)
        self.Bind(wx.EVT_SPIN, self.OnSpin)

        #self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)


    # string formatting examples
    #
    # Box mpos x {} y {} shift x {} y {}".format(self.mpos.x, self.mpos.y, shift.x, shift.y)
    # "{:.0f}".format(xval + plot.xdis)


    def ParamStore(self, filetag = ""):
        newtag = False
        if filetag == "": newtag = True
        parampath = self.mod.path + "/Params"
        if os.path.exists(parampath) == False: 
            os.mkdir(parampath)

        if self.storetag is not None:
            if filetag == "": filetag = self.storetag.GetValue()
            else: self.storetag.SetValue(filetag)

        # Param data file
        filepath = parampath + "/" + filetag + "-" + self.boxtag + "param.dat";

        # Param file history
        if self.storetag is not None and filetag != "default": 
            tagpos = self.storetag.FindString(filetag)
            if tagpos != wx.NOT_FOUND: self.storetag.Delete(tagpos)
            self.storetag.Insert(filetag, 0)
            print("tag inserted " + filetag)

        # Overwrite Warning
        paramfile = TextFile(filepath)
        if paramfile.Exists() and newtag and self.redtag != filetag: 
            if self.storetag is not None:
                self.storetag.SetForegroundColour(self.redpen)
                self.storetag.SetValue("")
                self.storetag.SetValue(filetag)
            self.redtag = filetag
            return

        # Clear Overwrite Warning
        self.redtag = ""
        if self.storetag is not None:
            self.storetag.SetForegroundColour(self.blackpen)
            self.storetag.SetValue("")
            self.storetag.SetValue(filetag)

        # Open File
        paramfile.Open('w')

        # Write Parameter Values
        for con in self.paramset.pcons.values():
            if con.type != "textcon":
                outline = "{:.8f}".format(con.GetValue())
            else: outline = con.GetString()
            paramfile.WriteLine(con.tag + " " + outline)

        # Write Flag Values
        paramfile.WriteLine("")
        for flagtag in self.flagtags.values():
            outline = f"{self.modflags[flagtag]}"
            paramfile.WriteLine(flagtag + " " + outline)

        # Write Check Values
        paramfile.WriteLine("")
        for checktag in self.checktags.values():
            outline = f"{self.modflags[checktag]}"
            paramfile.WriteLine(checktag + " " + outline)
  
        # Close File
        paramfile.Close()
        self.DiagWrite("Param File OK\n")


    def ParamLoad(self, filetag = "", compmode = False):
        diagmode = False
        if diagmode: DiagWrite("param load {}\n".format(self.boxtag))

        oldparams = self.GetParams()
        parampath = self.mod.path + "/Params"

        # Param data file
        if self.storetag is not None:
            if filetag == "": filetag = self.storetag.GetValue()
            elif filetag != "default": self.storetag.SetValue(filetag)

        filepath = parampath + "/" + filetag + "-" + self.tag + "param.dat"
        if diagmode: DiagWrite("paramload " + filepath + "\n")
        paramfile = TextFile(filepath)

        if not paramfile.Exists():
            if self.storetag: self.storetag.SetValue("Not found")
            return

        # Param file history
        if self.storetag is not None and filetag != "default": 
            tagpos = self.storetag.FindString(filetag)
            if tagpos != wx.NOT_FOUND: self.storetag.Delete(tagpos)
            self.storetag.Insert(filetag, 0)
            print("tag inserted " + filetag)

        # Clear Overwrite Warning
        self.redtag = ""
        if self.storetag is not None:
            self.storetag.SetForegroundColour(self.blackpen)
            self.storetag.SetValue("")
            self.storetag.SetValue(filetag)

        # Open File
        paramfile.Open('r')

        # Read Parameter Values
        mode = "param"
        filetext = paramfile.ReadLines()
        
        for readline in filetext:

            # parse line
            readline = readline.strip()
            if readline == "":
                if mode == "param": mode = "flag"
                elif mode == "flag": mode = "check"
                continue
            readdata = readline.split(' ')
            tag = readdata[0]
            data = readdata[1]

            # read parameter
            if mode == "param":
                if self.paramset.Check(tag):
                    paramcon = self.paramset.pcons[tag]
                    if paramcon.type != "textcon":
                        datval = float(data)
                        paramcon.SetPen(self.blackpen)
                        if compmode and datval != oldparams[tag]:
                            paramcon.SetPen(self.greenpen)
                            DiagWrite(tag + " param change\n")
                        paramcon.Clear()
                        paramcon.SetValue(datval)
                    else: paramcon.SetValue(data)
                    if diagmode: DiagWrite("Model Param Tag {}, Value {:.4f}\n".format(tag, datval)) 

            # read flag
            if mode == "flag":
                if tag in self.flagIDs:
                    flagval = int(data)
                    self.modflags[tag] = flagval
                    id = self.flagIDs[tag]
                    self.menuModel.Check(id, flagval)
                    if diagmode: DiagWrite("Model flag ID {}, Tag {}, Set %d\n".format(id, tag, flagval)) 

            # read check
            if mode == "check":
                if tag in self.checkIDs:
                    checkval = int(data)
                    self.modflags[tag] = checkval
                    checkbox = self.checkboxes[tag]
                    checkbox.SetValue(checkval)
                    if diagmode: DiagWrite("Model check Tag {}, Set {}\n".format(tag, flagval)) 

        paramfile.Close()


    def RunBox(self):
        runbox = wx.BoxSizer(wx.HORIZONTAL)
        self.runcount = self.NumPanel(50, wx.ALIGN_CENTRE, "---")
        if GetSystem() == "Mac": self.AddButton(ID_Run, "RUN", 50, runbox)
        else: self.AddButton(ID_Run, "RUN", 70, runbox)
        runbox.AddSpacer(5)
        runbox.Add(self.runcount, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL)

        if self.defbutt:
            runbox.AddSpacer(5)
            if GetSystem() == "Mac": self.AddButton(ID_Default, "RESET", 50, runbox)
            else: self.AddButton(ID_Default, "RESET", 70, runbox)
	
        return runbox
    

    def SetCount(self, value):
        if self.runcount is not None:
            self.runcount.SetLabel(f"{value} %")
            #DiagWrite(f"Set count, value {value}\n\n")


    def InitMenu(self, type = "menu_model"):
        if type == "menu_model":
            self.menuControls = wx.Menu()
            self.menuControls.Append(ID_AutoRun, "Auto Run", "Toggle Autorun", wx.ITEM_CHECK)
            self.menuControls.Check(ID_AutoRun, self.autorun)
            self.menuModel = wx.Menu()
            menuBar = wx.MenuBar()
            menuBar.Append(self.menuControls, "Controls")
            menuBar.Append(self.menuModel, "Model")

        if type == "menu_gridbox":
            self.menuMode = wx.Menu()
            menuBar = wx.MenuBar()
            menuBar.Append(self.menuMode, "Mode")

        self.SetMenuBar(menuBar)
       

    def AddPanelButton(self, id, label, toolbox):
        if self.panelbuttoncount > 0:
            self.buttonbox.AddSpacer(5)
            self.buttonbox.AddStretchSpacer()
        self.panelrefs[id] = toolbox
        button = self.AddButton(id, label, self.buttonwidth, self.buttonbox)
        button.Bind(wx.EVT_BUTTON, self.OnPanel)
        self.panelbuttoncount += 1
       

    def OnPanel(self, event):
        id = event.GetId()
        toolbox = self.panelrefs[id]
        if toolbox.IsShown(): toolbox.Show(False)
        else: toolbox.Show(True)


    """ def AddFlag(self, id, flagtag, flagtext, state = False, menu = None):
        if menu is None: menu = self.menuModel
        self.modflags[flagtag] = state
        self.flagtags[id] = flagtag
        self.flagIDs[flagtag] = id
        menu.Append(id, flagtext, "Toggle " + flagtext, wx.ITEM_CHECK)
        menu.Check(id, state)
        self.Bind(wx.EVT_MENU, self.OnFlag, id) """


    """ def AddFlag(self, flagtag, flagtext, state=False, menu=None):
        if menu is None: menu = self.menuModel
        item = menu.AppendCheckItem(wx.ID_ANY, flagtext, "Toggle " + flagtext)
        item.Check(bool(state))
        self.modflags[flagtag] = bool(state)
        item.flagtag = flagtag
        self.Bind(wx.EVT_MENU, self.OnFlag, item)
        return item """
    

    """ def AddFlag(self, flagtag, flagtext, state=False, menu=None):
        if menu is None: menu = self.menuModel
        item = menu.AppendCheckItem(wx.ID_ANY, flagtext, "Toggle " + flagtext)
        item.Check(bool(state))
        self.modflags[flagtag] = bool(state)
        self.Bind(wx.EVT_MENU, lambda evt, tag=flagtag: self.OnFlag(evt, tag), source=item)
        return item """
    

    def AddFlag(self, flagtag, flagtext, state=False, menu=None):
        if menu is None: menu = self.menuModel
        item = menu.AppendCheckItem(wx.ID_ANY, flagtext, "Toggle " + flagtext)
        item.Check(bool(state))
        id = item.GetId()
        self.modflags[flagtag] = bool(state)
        self.flagtags[id] = flagtag
        self.Bind(wx.EVT_MENU, self.OnFlag, id=id)
        return item


    def AddCheck(self, id, checktag, checktext, state):
        self.modflags[checktag] = state
        self.checktags[id] = checktag
        newcheck = wx.CheckBox(self.activepanel, id, checktext)
        newcheck.SetFont(self.confont)
        newcheck.SetValue(state)
        newcheck.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.checkboxes[checktag] = newcheck
        return newcheck


    """ def OnFlag(self, event):
        id = event.GetId()
        flagtag = self.flagtags[id]
        if self.modflags[flagtag] == 0: self.modflags[flagtag] = 1
        else: self.modflags[flagtag] = 0
        if self.autorun: self.OnRun(event)


    def OnFlag(self, event):
        item = event.GetEventObject()
        flagtag = getattr(item, "flagtag", None)

        if flagtag is None:
            event.Skip()
            return

        self.modflags[flagtag] = item.IsChecked() 
        
        
    def OnFlag(self, event, flagtag):
	    item = event.GetEventObject()
	    self.modflags[flagtag] = item.IsChecked()
        
        """


 
    def OnFlag(self, event):
        id = event.GetId()
        flagtag = self.flagtags[id]
        item = self.menuModel.FindItemById(id)
        self.modflags[flagtag] = item.IsChecked()
        

    def OnCheck(self, event):
        id = event.GetId()
        checktag = self.checktags[id]
        if self.modflags[checktag] == 0: self.modflags[checktag] = 1
        else: self.modflags[checktag] = 0
    

    def OnDefault(self, event):
        self.ParamLoad("default")
        if self.autorun: self.OnRun(event)


    def OnSpin(self, event):
        #self.DiagWrite("ParamBox on spin\n") 
        if self.autorun: self.OnRun(event)


    def OnRun(self, event):
        self.countmark = 0
        #self.GetParams()
        self.mod.RunModel()


    def OnAutoRun(self, event):
        self.autorun = 1 - self.autorun
        print(f"AutoRun {self.autorun}")


    def SetStatus(self, text):
        if self.status is not None: self.status.SetLabel(text)


    def WriteVDU(self, text):
        if self.vdu is not None: self.vdu.AppendText(text)


    def StoreBoxSync(self, label="", storepanel=None):
        self.synccheck = wx.CheckBox(self.panel, wx.ID_ANY, "Sync")
        self.synccheck.SetValue(True)
        storebox = self.StoreBox(label, storepanel)
        storebox.Add(self.synccheck, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 2)
        return storebox


    def StoreBox(self, label="", storepanel=None):
        if self.storetag is None: return
        paramfilebox = wx.BoxSizer(wx.HORIZONTAL)
        parambuttons = wx.BoxSizer(wx.HORIZONTAL)

        if storepanel is None: storepanel = self.panel
        if self.activepanel != self.panel: self.storetag.Reparent(self.activepanel)

        if label != "": self.storetag.SetLabel(label)
        self.storetag.Show(True)

        self.AddButton(wx.ID_ANY, "Store", 38, parambuttons).Bind(wx.EVT_BUTTON, self.OnStore)
        parambuttons.AddSpacer(2)
        self.AddButton(wx.ID_ANY, "Load", 38, parambuttons).Bind(wx.EVT_BUTTON, self.OnLoad)
        
        paramfilebox.Add(self.storetag, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 2)
        paramfilebox.Add(parambuttons, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 2)
        return paramfilebox

    
    def OnStore(self, event):
        self.ParamStore()


    def OnLoad(self, event):
        self.ParamLoad()

    