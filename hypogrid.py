
import wx.grid
from hypobase import *
from hypoparams import *



class TextGrid(wx.grid.Grid):
    def __init__(self, parent, size):
        wx.grid.Grid.__init__(self, parent, wx.ID_ANY)

        self.ostype = GetSystem()

        self.CreateGrid(size.x, size.y)
        self.SetRowLabelSize(35)
        self.SetColLabelSize(25)
        self.SetRowLabelAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        self.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)    
        self.SetLabelFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.undogrid = wx.grid.GridStringTable(size.x, size.y)
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

        self.Bind(wx.EVT_MENU, self.OnSelectAll, ID_SelectAll)
        self.Bind(wx.EVT_MENU, self.OnCut, ID_Cut)
        self.Bind(wx.EVT_MENU, self.OnCopy, ID_Copy)
        self.Bind(wx.EVT_MENU, self.OnPaste, ID_Paste)
        self.Bind(wx.EVT_MENU, self.OnPaste, ID_PasteTranspose)
        self.Bind(wx.EVT_MENU, self.OnUndo, ID_Undo)
        self.Bind(wx.EVT_MENU, self.OnBold, ID_Bold)
        self.Bind(wx.EVT_MENU, self.OnInsertColumn, ID_Insert)

        self.Bind(wx.EVT_KEY_DOWN, self.OnKey)
       


    def OnRightClick(self, event):
        pos = event.GetPosition()
        self.PopupMenu(self.rightmenu, pos.x - 20, pos.y)


    def CopyColumn(self, source, dest):
        numrows = self.GetNumberRows()

        for i in range(numrows):
            celltext = self.GetCellValue(i, source)
            self.SetCellValue(i, dest, celltext)


    def InsertColumn(self, col):
        self.InsertCols(col)


    def ReadFloat(self, row, col):
        celltext = self.GetCell(row, col)
        celltext = celltext.strip()
        if not celltext == "": celldata = float(celltext)
        else: return 0
        return celldata

    
    def GetCell(self, row, col):
        numrows = self.GetNumberRows()
        numcols = self.GetNumberCols()

        if row >= numrows or col >= numcols: return "" 
        else: return self.GetCellValue(row, col)


    def SetCell(self, row, col, data):
        numrows = self.GetNumberRows()
        numcols = self.GetNumberCols()

        if row >= numrows: self.AppendRows(row - numrows + 10)
        if col >= numcols: self.AppendCols(col - numcols + 10)

        #if(row == 0) diagbox->Write(text.Format("SetCell row %d col %d data %s\n", row, col, data));
        self.SetCellValue(row, col, data)


    def OnKey(self, event):
        if event.GetUnicodeKey() == 'C' and event.ControlDown() == True: self.Copy()

        elif event.GetUnicodeKey() == 'V' and event.ControlDown() == True: self.Paste()

        elif event.GetUnicodeKey() == 'T' and event.ControlDown() == True: self.Paste(1)

        elif event.GetUnicodeKey() == 'X' and event.ControlDown() == True: self.Cut()

        elif event.GetUnicodeKey() == 'Z' and event.ControlDown() == True: self.Undo()

        elif event.GetUnicodeKey() == 'A' and event.ControlDown() == True: self.SelectAll()

        elif event.GetKeyCode() == wx.WXK_DELETE:
            self.Delete()
            return

        event.Skip()


    def ClearCol(self, col):
        for i in range(self.GetNumberRows()):
            self.SetCellValue(i, col, "")


    def SetBold(self):
        self.CopyUndo()

        for i in range(self.GetNumberRows()):     
            for j in range(self.GetNumberCols()): 
                if self.IsInSelection(i, j): self.SetCellFont(i, j, wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.Refresh()


    def OnSelectAll(self, event):
        self.SelectAll()


    def OnInsertColumn(self, event):
        col = self.GetGridCursorCol()
        self.InsertColumn(col)


    def OnCut(self, event):
        self.Cut()

    
    def OnCopy(self, event):
        self.Copy()


    def OnPaste(self, event):
        if event.GetId() == ID_PasteTranspose: self.Paste(1)
        else: self.Paste(0)


    def OnBold(self, event):
        self.SetBold()


    def Delete(self):
        self.CopyUndo()
        self.SetCellValue(self.GetGridCursorRow(), self.GetGridCursorCol(), "")
        for i in range(self.GetNumberRows()):     
            for j in range(self.GetNumberCols()): 
                if self.IsInSelection(i, j): self.SetCellValue(i, j, "")


    def Cut(self):
        self.Copy()
        self.Delete()


    def Copy(self):
        # Get selected cells
        top_left = self.GetSelectionBlockTopLeft()[0]
        bottom_right = self.GetSelectionBlockBottomRight()[0]

        # Prepare data for clipboard
        data = ""
        for row in range(top_left[0], bottom_right[0] + 1):
            for col in range(top_left[1], bottom_right[1] + 1):
                data += str(self.GetCellValue(row, col)) + '\t'
            data = data[:-1] + '\n'
        data = data[:-1]

        # Copy data to clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(data))
            wx.TheClipboard.Close()


    def Paste(self, mode = 0):
	    # grid paste code from wxwidgets forum

        self.CopyUndo()

        if self.vdu and mode == 1: self.vdu.AppendText("Transpose Pasting...\n")
        if self.vdu: self.vdu.AppendText("Copy clipboard...")

        wx.TheClipboard.Open()
        data = ""
        wx.TheClipboard.GetData(data)
        #copy_data = data.GetText()
        wx.TheClipboard.Close()


    def OnUndo(self, event):
        self.Undo()


    def OnLabelClick(self, event):
        if self.vdu: self.vdu.AppendText("Label Click\n")
        c = event.GetCol()
        r = event.GetRow()

        if self.gridbox and c >= 0: 
            self.gridbox.ColumnSelect(c)
            self.selectcol = c

        if self.gridbox and r >= 0: 
            self.gridbox.RowSelect(r)
            self.selectrow = r

        event.Skip()


    def OnLeftClick(self, event):
        pos = event.GetPosition()
        row = event.GetRow()
        col = event.GetCol()

        self.selectrow = row
        self.selectcol = col

        #if(diagbox) diagbox->Write(text.Format("grid click row %d col %d\n", row, col));
        event.Skip()


    def OnRightClick(self, event):
        pos = event.GetPosition()
        self.PopupMenu(self.rightmenu, pos.x - 20, pos.y)


    def CopyUndo(self):
        if self.GetNumberRows() > self.undogrid.GetNumberRows(): self.undogrid.AppendRows(self.GetNumberRows() - self.undogrid.GetNumberRows())
        if self.GetNumberCols() > self.undogrid.GetNumberCols(): self.undogrid.AppendCols(self.GetNumberCols() - self.undogrid.GetNumberCols())

        for x in range(self.GetNumberCols()):
            for y in range(self.GetNumberRows()):
                data = self.GetCellValue(y, x)
                self.undogrid.SetValue(y, x, data)


    def Undo(self):
        if self.GetNumberRows() > self.undogrid.GetNumberRows(): self.undogrid.AppendRows(self.GetNumberRows() - self.undogrid.GetNumberRows())
        if self.GetNumberCols() > self.undogrid.GetNumberCols(): self.undogrid.AppendCols(self.GetNumberCols() - self.undogrid.GetNumberCols())

        for x in range(self.GetNumberCols()):
            for y in range(self.GetNumberRows()):
                data = self.undogrid.GetValue(y, x)
                self.SetCellValue(y, x, data)
	


"""
    def Copy(self):
        # Copy selected cells to the clipboard
        
        if self.Selection:
            # Store selected cells in a string
            data = ""
            for topLeft, bottomRight in grid.Selection:
                for row in range(topLeft.GetRow(), bottomRight.GetRow()+1):
                    for col in range(topLeft.GetCol(), bottomRight.GetCol()+1):
                        value = self.GetValue(row, col)
                        data += str(value) + '\t'
                    data = data[:-1] + '\n'
            data = data[:-1]
            
            # Put the string on the clipboard
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(data))
                wx.TheClipboard.Close()



    ""
    def Copy(self):
        if self.IsSelection():
            data = ""
            for block in self.GetSelectedBlocks():
                for row in range(block.T)
"""



class GridBox(ParamBox):
    def __init__(self, mod, title, pos, size, rows=100, cols=20, bookmode=True, vdumode=True):      
        ParamBox.__init__(self, mod, title, pos, size, "gridbox", 0, 1)
            
        self.mod = mod
        self.numgrids = 0
        #self.textgrid = []
    
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

        self.grids = {}
        self.grids["Data"] = None
        self.grids["Output"] = None
        self.grids["Params"] = None
        self.grids["Layout"] = None

        self.gridtags = []

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
            self.AddGrid("Data", wx.Size(self.gridrows, self.gridcols))
            self.AddGrid("Output", wx.Size(self.gridrows, self.gridcols))
            #self.AddGrid("Params", wx.Size(20, 20))
            #self.AddGrid("Layout", wx.Size(20, 20))
        else: self.AddGrid("", wx.Size(self.gridrows, self.gridcols))

        self.currgrid = "Data"

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

        self.Bind(wx.EVT_BUTTON, self.OnUndo, ID_Undo)
        self.Bind(wx.EVT_BUTTON, self.OnCopy, ID_Copy)
        #self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        #self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnCellChange)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnGridSelect)


    def OnGridSelect(self, event):
        newpageindex = event.GetSelection()
        self.currgrid = self.gridtags[newpageindex]
        DiagWrite(f"OnGridSelect {newpageindex} {self.currgrid}\n")



    # AddGrid() in (now default) notebook mode adds a new TextGrid and wxNotebook page
    # initialises grid and links to output controls

    def AddGrid(self, label, size):
        # Initialise
        if self.notebook: 
            newgrid = TextGrid(self.notebook, size)
            self.notebook.AddPage(newgrid, label)
        else: newgrid = TextGrid(self.panel, size)

        self.grids[label] = newgrid
        self.gridtags.append(label)     # store grid tags by page index, for page selection
        newgrid.tag = label
          
        # Set Links
        newgrid.vdu = self.vdu
        newgrid.gauge = self.gauge
        newgrid.gridbox = self

        # Format
        newgrid.SetDefaultRowSize(20, True)
        newgrid.SetDefaultColSize(60, True)
        newgrid.SetRowLabelSize(50) 

        #self.textgrid.append(newgrid)
        


    def OnUndo(self, event):
        self.grids[self.currgrid].Undo()


    def OnCopy(self, event):
        self.grids[self.currgrid].Copy()

