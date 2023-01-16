


from hypobase import *
from hypobase import *
from hypotools import *
from hypograph import *
from hyposcale import *
from hypoparams import *
from osmomod import *



class MainFrame(wx.Frame):
    def __init__(self, title, pos, size, rpath, mpath):
        super(MainFrame, self).__init__(None, wx.ID_ANY, title, pos, size)
        self.ostype = GetSystem()
        self.statusbar = self.CreateStatusBar()
        #self.SetBackgroundColour(wx.WHITE)
        #errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)

        # Initialise ToolBoxes
        self.diagbox = DiagBox(self, "Diagnostic", wx.Point(0, 0), wx.Size(400, 500))
        self.diagbox.Write('Diagnostic Box OK\n')
        self.gridbox = None

        respath = rpath;  # defaults to "" for Windows, bundle resource path for OSX
        self.diagbox.Write("MainFrame respath " + respath + "\n")
        #self.mainpath = mpath
        self.mainpath = os.getcwd()
        self.modpath = ""

        # Set up store paths and folders
        if self.mainpath == "": self.initpath = "Init"
        else: self.initpath = self.mainpath + "/Init"

        if self.mainpath == "": self.toolpath = "Tools"
        else: self.toolpath = self.mainpath + "/Tools"

        if os.path.exists(self.initpath) == False: 
            os.mkdir(self.initpath)

        if os.path.exists(self.toolpath) == False: 
            os.mkdir(self.toolpath)
        
        self.colourpen = {}
        self.colourpen["black"] = wx.Colour("#000000")
        self.colourpen["red"] = wx.Colour("#F50000")
        self.colourpen["green"] = wx.Colour("#000000")
        self.colourpen["blue"] = wx.Colour("#0000F5")
        self.colourpen["yellow"] = wx.Colour("#F5F500")
        self.colourpen["purple"] = wx.Colour("#F500F5")
        self.colourpen["lightred"] = wx.Colour("#FF8080")
        self.colourpen["lightgreen"] = wx.Colour("#80FF80")
        self.colourpen["lightblue"] = wx.Colour("#8080FF")
        self.colourpen["custom"] = wx.Colour("#000000")

        self.fontset = ['Helvetica', 'Arial', 'Myriad', 'Times', 'Courier', 'Calibri']
        
        self.toolset = ToolSet()
        self.toolset.AddBox(self.diagbox)     

        pub.subscribe(self.status_listener, "status_listener")
        pub.subscribe(self.toolclose_listener, "toolclose_listener")
        pub.subscribe(self.diag_listener, "diagbox")

        self.Bind(wx.EVT_LEFT_UP, self.OnLeftClick)
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.ToolLoad()    # main window tool configuration


    def diag_listener(self, message, arg2=None):
        self.diagbox.Write(message)


    def status_listener(self, message, arg2=None):
        self.SetStatusText(message)


    def toolclose_listener(self, boxtag, arg2=None):
        del self.toolset.boxset[boxtag]


    def ToolStore(self):
        outfile = TextFile(self.initpath + "/maintools.ini")
        outfile.Open('w')
        
        for box in self.toolset.boxset.values():
            outfile.WriteLine("{} {} {} {} {} {}".format(box.boxtag, box.mpos.x, box.mpos.y, box.boxsize.x, box.boxsize.y, box.IsShown()))
        
        outfile.Close()
        print('ToolStore OK')


    def ToolLoad(self):
        filepath = self.initpath + "/maintools.ini"
        infile = TextFile(filepath)
        check = infile.Open('r')
        if check == False: return
        filetext = infile.ReadLines()

        for line in filetext:
            linedata = line.split(' ')
            boxtag = linedata[0]
            if boxtag in self.toolset.boxset:
                #print('boxtag OK')
                #print('tag' + ' ' + boxtag + ' ' + 'data1' + ' ' + linedata[1])          
                pos = wx.Point(int(linedata[1]), int(linedata[2]))
                size = wx.Size(int(linedata[3]), int(linedata[4]))
                if linedata[5] == 'True\n': visible = True
                else: visible = False
                self.toolset.boxset[boxtag].visible = visible
                self.toolset.boxset[boxtag].mpos = pos
                self.toolset.boxset[boxtag].boxsize = size

        infile.Close()

        for box in self.toolset.boxset.values():
            box.SetSize(box.boxsize)
            box.SetPosition(self.GetPosition(), self.GetSize())
            box.Show(box.visible)
            

    def OnLeftClick(self, event):
        for box in self.toolset.boxset.values():
            if box.IsShown(): box.Show(False)
            else: box.Show(True)


    def OnMove(self, event):
        for box in self.toolset.boxset.values():
            box.SetPosition(self.GetPosition(), self.GetSize())

        event.Skip()


    def OnSize(self, event):
        newsize = self.GetSize()
        for box in self.toolset.boxset.values():
            box.SetPosition(self.GetPosition(), newsize)

        self.prefs["viewwidth"] = newsize.x
        self.prefs["viewheight"] = newsize.y
        snum = "Main Size X {} Y {}".format(newsize.x, newsize.y)
        #self.SetStatusText(snum)

        event.Skip()



class HypoMain(MainFrame):
    def __init__(self, title, pos, size, respath, mainpath):
        super(HypoMain, self).__init__(title, pos, size, respath, mainpath)

        # Default Prefs
        self.prefs = {}
        self.prefs["numdraw"] = 3
        self.prefs["numgraphs"] = 8
        self.prefs["startmod"] = 0
        self.prefs["viewwidth"] = 400
        self.prefs["viewheight"] = 600

        # Load Prefs
        self.HypoLoad()
        self.SetSize(self.prefs["viewwidth"], self.prefs["viewheight"])

        # Layout
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.graphsizer = wx.BoxSizer(wx.VERTICAL)
        self.xstretch = 0
        self.numdraw = self.prefs["numdraw"]
        self.numgraphs = self.prefs["numgraphs"]
        self.scalewidth = -1
        
        # Menu Bar
        self.UserMenu()
        self.SetTitle("HypoMod")

        # Graph Disps
        self.dispset = []
        for i in range(self.numgraphs):
            self.dispset.append(GraphDisp())
            self.dispset[i].Add(PlotDat())   # Test Plot
            
         # Graph Panels
        self.panelset = []
        for graph in range(self.numdraw):
            graphdisp = self.dispset[graph]
            graphpanel = GraphPanel(self, graph)
            graphpanel.SetFront(graphdisp)
            self.panelset.append(graphpanel)
            self.graphsizer.Add(graphpanel, 1, wx.EXPAND)

        # Mod Init
        self.mod = OsmoMod(self, "osmomod")
        self.mod.DefaultPlots()
        
        # Scale Box
        self.scalebox = ScaleBox(self, wx.Size(self.scalewidth, -1), self.numdraw)
        if self.mod.graphload: self.scalebox.GLoad()
        
        # Sizers
        mainsizer.Add(self.scalebox, 0, wx.EXPAND)
        mainsizer.Add(self.graphsizer, 1, wx.EXPAND)
        self.SetSizer(mainsizer)
        self.Layout()

        # Initial Plots
        self.scalebox.GraphSwitch(self.mod.plotbase)

        # Event Binds
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SIZE, self.OnHypoSize)


    def OnHypoSize(self, event):
        super(HypoMain, self).OnSize(event)
        self.SizeUpdate()

    
    def SizeUpdate(self):
        newsize = self.GetSize()
        graphsize = self.graphsizer.GetSize()

        snum = f"newsizeX {newsize.x} graphsizeX {graphsize.x} newsizeY {newsize.y} graphsizeY {graphsize.y}"
        self.SetStatusText(snum)
        #DiagWrite(snum + '\n')

        gspacex = graphsize.x
        xplot = gspacex - 55
        
        gspacey = graphsize.y - self.numdraw * 55 - 5
        yplot = gspacey / self.numdraw

        for graphpanel in self.panelset:
            graphpanel.ReSize(xplot, yplot)
	

    def UserMenu(self):
        menuFile = wx.Menu()
        menuAnalysis = wx.Menu()
        menuTools = wx.Menu()
        menuSystem = wx.Menu()
        
        itemAbout = menuFile.Append(wx.ID_ABOUT, "&About...")
        menuFile.AppendSeparator()
        itemQuit = menuFile.Append(wx.ID_EXIT, "E&xit")
        
        #SetMenuFlag(ID_XYPos, "xypos", "XY Pos", 1, menuAnalysis)
        #SetMenuFlag(ID_Zoom, "zoom", "Graph Zoom", 0, menuAnalysis) 

        itemDiag = menuTools.Append(wx.ID_ANY, "Diagnostic Box")
        itemGrid = menuTools.Append(wx.ID_ANY, "Data Grid")
        itemAddGraph = menuTools.Append(wx.ID_ANY, "Add Graph")
        #menuTools.Append(ID_Neuro, "Neuro Box")
        #menuTools.Append(ID_Plot, "Plot Box")
        #menuTools.Append(ID_Sound, "Sound Box")
        #menuTools.Append(ID_Mod, "Mod Box")
        #menuTools.Append(ID_Burst, "Burst Box")

        menuSystem.Append(wx.ID_ANY, "Options")
        
        menuBar = wx.MenuBar()
        menuBar.Append(menuFile, "&File")
        #menuBar.Append(menuAnalysis, "Analysis")
        menuBar.Append(menuTools, "Tools")
        #menuBar.Append(menuSystem, "System")
        
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnQuit, itemQuit)
        self.Bind(wx.EVT_MENU, self.OnAbout, itemAbout)
        self.Bind(wx.EVT_MENU, self.OnGridBox, itemGrid)
        self.Bind(wx.EVT_MENU, self.OnDiagBox, itemDiag)
        self.Bind(wx.EVT_MENU, self.OnGraphAdd, itemAddGraph)


    def AddGraph(self):
        newindex = self.numdraw
        newdisp = GraphDisp()
        newdisp.Add(PlotDat())
        self.dispset.append(newdisp)
        newpanel = GraphPanel(self, newindex)
        newpanel.SetFront(newdisp)
        self.panelset.append(newpanel)
        self.graphsizer.Add(newpanel, 1, wx.EXPAND)
        self.scalebox.AddGraphConsole(newpanel)
        self.scalebox.Refresh()
        self.numdraw += 1

        self.graphsizer.Layout()
        self.SizeUpdate()
        self.Refresh()


    def RemoveGraph(self, oldpanel):
        self.SetStatusText("Remove Graph")
        self.graphsizer.Detach(oldpanel)
        self.numdraw -= 1
        self.scalebox.RemoveGraphConsole(oldpanel)
        oldpanel.Hide()
        self.panelset.remove(oldpanel)
        self.graphsizer.Layout()
        self.SizeUpdate()
        self.Refresh()


    def OnGraphAdd(self, event):
        self.SetStatusText("Add Graph")
        self.AddGraph()


    def OnQuit(self, event):
        print("Closing")
        self.model.ModStore()
        self.Close()


    def OnAbout(self, event):
        message = "HypoMod Modelling Toolkit\n\nDuncan MacGregor 2010-2022\n\nSystem: {}".format(wx.GetOsDescription())
        wx.MessageBox(message, "About HypoMod", wx.OK | wx.ICON_INFORMATION, self)

        
    def OnDiagBox(self, event):
        if(self.diagbox): self.diagbox.Show()   


    def OnGridBox(self, event):
        if(self.gridbox): self.gridbox.Show()  
        else: self.SetStatusText('No Data Grid available')  


    def OnClose(self, event):
        self.prefs["numdraw"] = self.numdraw
        self.HypoStore()
        MainFrame.ToolStore(self)
        self.scalebox.storetag.HistStore()
        #if(project.mod): 
        #    project.Store()
        if(self.mod != None):
        #    mod.Close()
            self.mod.ModStore()
        event.Skip()


    def HypoStore(self):
        outfile = TextFile(self.initpath + "/hypoprefs.ini")
        outfile.Open('w')

        for preftag in self.prefs:
            outfile.WriteLine("{} {}".format(preftag, self.prefs[preftag]))

        outfile.Close()
        print('HypoPrefs OK')


    def HypoLoad(self):
        infile = TextFile(self.initpath + "/hypoprefs.ini")
        check = infile.Open('r')
        if check == False: return
        filetext = infile.ReadLines()

        for line in filetext:
            linedata = line.split(' ')
            tag = linedata[0]
            if tag in self.prefs:
                self.prefs[tag] = int(linedata[1]) 

        infile.Close()