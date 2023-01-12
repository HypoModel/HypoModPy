import wx
import wx.lib.scrolledpanel as scrolled

########################################################################
class MyForm(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Tutorial", size=(200,500))
 
        # Add a panel so it looks the correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)
        
        # --------------------
        # Scrolled panel stuff
        self.scrolled_panel = scrolled.ScrolledPanel(self.panel, -1, 
                                 style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, name="panel1")
        self.scrolled_panel.SetAutoLayout(1)
        self.scrolled_panel.SetupScrolling()
        
        words = "A Quick Brown Insane Fox Jumped Over the Fence and Ziplined to Cover".split()
        self.spSizer = wx.BoxSizer(wx.VERTICAL)
        for word in words:
            text = wx.TextCtrl(self.scrolled_panel, value=word)
            self.spSizer.Add(text)
        self.scrolled_panel.SetSizer(self.spSizer)
        # --------------------
        
        btn = wx.Button(self.panel, label="Add Widget")
        btn.Bind(wx.EVT_BUTTON, self.onAdd)
        
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.AddSpacer(50)
        panelSizer.Add(self.scrolled_panel, 1, wx.EXPAND)
        panelSizer.Add(btn)
        self.panel.SetSizer(panelSizer)
        
    #----------------------------------------------------------------------
    def onAdd(self, event):
        print("in onAdd")
        new_text = wx.TextCtrl(self.scrolled_panel, value="New Text")
        self.spSizer.Add(new_text)
        self.scrolled_panel.Layout()
        self.scrolled_panel.SetupScrolling()
         
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm().Show()
    app.MainLoop()



# chatgpt grid copy paste 12/1/23

import wx
import wx.grid as gridlib

class MyGrid(gridlib.Grid):
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent)

        # Create a new data table
        self.table = MyTable()
        self.SetTable(self.table)

        # Enable copying to the clipboard
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def on_key_down(self, event):
        if event.ControlDown() and event.GetKeyCode() == ord('C'):
            self.copy()
        elif event.ControlDown() and event.GetKeyCode() == ord('V'):
            self.paste()
        else:
            event.Skip()

    def copy(self):
        """
        Copy the selected cells to the clipboard.
        """
        # Get the selected cells
        top_left = self.GetSelectionBlockTopLeft()[0]
        bottom_right = self.GetSelectionBlockBottomRight()[0]
        if top_left and bottom_right:
            rows = range(top_left[0], bottom_right[0]+1)
            cols = range(top_left[1], bottom_right[1]+1)
            data = [self.table.data[row][col] for row in rows for col in cols]
            # Set the data to the clipboard
            clipboard = wx.Clipboard()
            clipboard.Open()
            clipboard.SetData(wx.TextDataObject('\n'.join(data)))
            clipboard.Close()

    def paste(self):
        """
        Paste data from the clipboard to the selected cells.
        """
        clipboard = wx.Clipboard()
        if clipboard.Open():
            data = clipboard.GetData()
            if data.IsSupported(wx.DF_TEXT):
                data = data.GetText()
                data = data.split('\n')

                # Get the selected cells
                top_left = self.GetSelectionBlockTopLeft()[0]
                bottom_right = self.GetSelectionBlockBottomRight()[0]
                if top_left and bottom_right:
                    rows = range(top_left[0], bottom_right[0]+1)
                    cols = range(top_left[1], bottom_right[1]+1)
                    for i, row in enumerate(rows):
                        for j, col in enumerate(cols):
                            try:
                                value = data[i * len(cols) + j]
                                self.table.data[row][col] = value
                                self.table.ResetView(self)
                            except:
                                pass
            clipboard.Close()
            
class MyTable(gridlib.PyGridTableBase):
    def __init__(self):
        gridlib.PyGridTableBase.__init__(self)
        self.data = [['' for _ in range(5)] for _ in range(5)]

    # Required methods
    def GetNumberRows(self):
        return len(self.


# chatgpt wxgrid large virtual example

import wx
import wx.grid

class MyGridTable(wx.grid.GridTableBase):
    def __init__(self, rowCount, colCount):
        wx.grid.GridTableBase.__init__(self)
        self.rowCount = rowCount
        self.colCount = colCount
        self.data = {}

    def GetNumberRows(self):
        return self.rowCount

    def GetNumberCols(self):
        return self.colCount

    def IsEmptyCell(self, row, col):
        return self.data.get((row, col)) is None

    def GetValue(self, row, col):
        return self.data.get((row, col), '')

    def SetValue(self, row, col, value):
        self.data[(row, col)] = value
        
    def GetColLabelValue(self, col):
        return "Col %s" % col
    
    def GetRowLabelValue(self, row):
        return "Row %s" % row


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Large Virtual Grid")

        # Create the grid
        grid = wx.grid.Grid(self)
        grid.SetTable(MyGridTable(1000000, 100), True) # you can use any large number of rows and cols
        grid.AutoSizeColumns()

        # Set some grid options to improve performance
        grid.EnableEditing(False)
        grid.EnableGridLines(False)
        grid.EnableDragGridSize(False)
        grid.SetColLabelSize(0)
        grid.SetRowLabelSize(0)

app = wx.App()
frame = MyFrame()
frame.Show()
app.MainLoop()



# chapgpt virtual grid copy / paste


class MyGridTable(wx.grid.GridTableBase):
    def __init__(self, rowCount, colCount):
        # ... Your code 
        
    # ... Your code
    
    def Copy(self):
        """Copy selected cells to the clipboard"""
        grid = self.GetView()
        if grid.Selection:
            # Store selected cells in a string
            data = ''
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
                
    def Paste(self):
        """Paste data from the clipboard"""
        grid = self.GetView()
        if grid.Selection:
            topLeft, _ = grid.Selection[0]
            startRow, startCol = topLeft.GetRow(), topLeft.GetCol()
            
            # Get data from the clipboard
            data = None
            if wx.TheClipboard.Open():
                if wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
                    data = wx.TextDataObject()
                    wx.TheClipboard.GetData(data)
                wx.TheClipboard.Close()
                
            if data:
                # Process the data and insert it into the grid
                rows = data.GetText().split('\n')
                for i, row in enumerate(rows):
                    for j, value in enumerate(row.split('\t')):
                        if self.GetNumberRows() > startRow+i and self.GetNumberCols() > startCol+j:
                            self.SetValue(startRow + i, startCol + j, value)
                        else:
                            break
    #...Your code

class MyFrame(wx.Frame):
    def __init__(self):
        #...Your code
        # Create the grid
        grid = wx.grid.Grid(self)
        grid.SetTable(MyGridTable(1000000, 100), True)
        grid.AutoSizeColumns()
        
        # Bind copy and paste events
        grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CL
