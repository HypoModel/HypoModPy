
import wx.grid
from hypobase import *
from hypoparams import *



class TextGrid(wx.Grid):
    def __init__(self, parent, size):
        wx.grid.Grid.__init__(self, parent, wx.ID_ANY)

        self.ostype = GetSystem()

        self.CreateGrid(size.x, size.y)
        self.SetRowLabelSize(35)
        self.SetColLabelSize(25)
        self.SetRowLabelAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        self.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)    
        self.SetLabelFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.undogrid = self.GridStringTable(size.x, size.y)
        self.vdu = None
        self.gridbox = None
        self.mod = None
        self.selectcol = 0
        self.selectrow = 0

        self.rightmenu = wx.Menu()
        self.rightmenu.Append(ID_SelectAll, "Select All", "Grid Select", wx.ITEM_NORMAL)
        self.rightmenu.Append(ID_Copy, "Copy", "Copy Selection", wx.ITEM_NORMAL)
        self.rightmenu.Append(ID_Paste, "Paste", "Paste Clipboard", wx.ITEM_NORMAL)
        self.rightmenu.Append(ID_PasteTranspose, "Paste Transpose", "Paste Clipboard", wx.ITEM_NORMAL)
        self.rightmenu.Append(ID_Undo, "Undo", "Undo", wx.ITEM_NORMAL)
        self.rightmenu.Append(ID_Insert, "Insert Col", "Insert Column", wx.ITEM_NORMAL)

        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnRightClick)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnLeftClick)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelClick)
        self.Bind(ID_SelectAll, wx.EVT_MENU, self.OnSelectAll)
        self.Bind(ID_Cut, wx.EVT_MENU, self.OnCut)
        self.Bind(ID_Copy, wx.EVT_MENU, self.OnCopy)
        self.Bind(ID_Paste, wx.EVT_MENU, self.OnPaste)
        self.Bind(ID_PasteTranspose, wx.EVT_MENU, self.OnPaste)
        self.Bind(ID_Undo, wx.EVT_MENU, self.OnUndo)
        self.Bind(ID_Bold, wx.EVT_MENU, self.OnBold)
        self.Bind(wx.ID_ANY, wx.EVT_KEY_DOWN, self.OnKey)
        self.Bind(wx.ID_ANY, wx.EVT_CHAR, self.OnTypeKey) 
        self.Bind(ID_Insert, wx.EVT_MENU, self.OnInsertColumn)


    def OnRightClick(self, event):
        pos = event.GetPosition()
        self.PopupMenu(self.rightmenu, pos.x - 20, pos.y)



class GridBox(ParamBox):
    def __init__GridBox(self, mod, title, pos, size, rows=100, cols=20, bookmode=True, vdumode=True):      
        ParamBox.__init__(self, mod, title, pos, size, "gridbox", 0, 1)
            
        self.mod = mod
        self.numgrids = 0
        self.textgrid = []
    
        self.undomode = True
        #self.redtag = ""
        self.gridrows = rows
        self.gridcols = cols
        self.bookmode = bookmode
        self.vdumode = vdumode

        #self.startshift = False   # True
        self.notebook = None
        self.vdu = None
        self.gauge = None
        self.plotbox = None

        #textdata.resize(1000);
        #textdatagrid.grow = 10;

        #numdata.resize(10000);
        #numdatagrid.grow = 100;

        self.datagrid = None
        self.outputgrid = None
        self.paramgrid = None
        self.layoutgrid = None

        vdubox = wx.BoxSizer(wx.VERTICAL)

        if vdumode:
            self.vdu = wx.TextCtrl(self.panel, wx.ID_ANY, "", wx.DefaultPosition, wx.Size(-1, -1), wx.BORDER_RAISED|wx.TE_MULTILINE)
            self.vdu.SetFont(self.confont)
            self.vdu.SetForegroundColour(wx.Colour(0,255,0)) # set text color
            self.vdu.SetBackgroundColour(wx.Colour(0,0,0)) # set text back color
            self.gauge = wx.Gauge(self.panel, wx.ID_ANY, 10)
            vdubox.Add(self.vdu, 1, wx.EXPAND)

        if bookmode:
            self.notebook = wx.Notebook(self.panel, -1, wx.Point(-1,-1), wx.Size(-1, 400), wx.NB_TOP)
            self.datagrid = self.AddGrid("Data", wx.Size(self.gridrows, self.gridcols))
            self.outputgrid = self.AddGrid("Output", wx.Size(self.gridrows, self.gridcols))
            self.paramgrid = self.AddGrid("Params", wx.Size(20, 20))
            self.layoutgrid = self.AddGrid("Layout", wx.Size(20, 20))
        else: self.AddGrid("", wx.Size(self.gridrows, self.gridcols))

        self.currgrid = 0

        controlbox = wx.BoxSizer(wx.HORIZONTAL)
        storebox = self.StoreBox()

        buttonbox = wx.BoxSizer(wx.HORIZONTAL)
        buttonbox.Add(storebox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL)
        self.AddButton(ID_Undo, "Undo", 40, buttonbox)

        leftbox = wx.BoxSizer(wx.VERTICAL)
        leftbox.Add(buttonbox, 0) 
        if vdumode: leftbox.Add(self.gauge, 0, wx.EXPAND)

        controlbox.AddSpacer(10)
        controlbox.Add(leftbox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL)
        controlbox.AddSpacer(10)
        if vdumode: controlbox.Add(vdubox, 100, wx.EXPAND)
        controlbox.AddSpacer(10)

        if bookmode: self.mainbox.Add(self.notebook, 1, wx.EXPAND)
        else: self.mainbox.Add(self.textgrid[0], 1, wx.EXPAND)
        self.mainbox.Add(controlbox, 0)
        self.mainbox.AddSpacer(2)

        self.panel.Layout()

        self.Bind(ID_Undo, wx.EVT_BUTTON, self.OnUndo)
        self.Bind(ID_Copy, wx.EVT_BUTTON, self.OnCopy)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnCellChange)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnGridSelect)


    def OnGridSelect(self, event):
        newpage = event.GetSelection()
        #diagbox->Write(text.Format("OnGridSelect %d\n", newpage));
        self.currgrid = newpage


    # AddGrid() in (now default) notebook mode adds a new TextGrid and wxNotebook page
    # initialises grid and links to output controls

    def AddGrid(self, label, size):
        # Initialise
        if self.notebook: 
            newgrid = TextGrid(self.notebook, size)
            self.notebook.AddPage(newgrid, label)
            #self.gridindex.Add(label);
        else: newgrid = TextGrid(self.panel, size)
          
        # Set Links
        newgrid.vdu = self.vdu
        newgrid.gauge = self.gauge
        newgrid.gridbox = self

        # Format
        newgrid.SetDefaultRowSize(20, True)
        newgrid.SetDefaultColSize(60, True)
        newgrid.SetRowLabelSize(50) 

        self.textgrid.append(newgrid)
        return newgrid


