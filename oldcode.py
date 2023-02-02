
import wx


def Copy(self):
        """
        DiagWrite("Grid Copy\n")
        topleft = self.GetSelectionBlockTopLeft()
        bottomright = self.GetSelectionBlockBottomRight()

        if list(topleft) == []:
            selectcell = self.GetGridCursorCoords()
            DiagWrite(f"single cell row {selectcell.Row} col {selectcell.Col}\n")
        else:
            selectcell = None
            DiagWrite(f"top_left {topleft} bottom_right {bottomright}\n")
        """


def PasteOld(self, mode = 0):
        # grid paste code from wxwidgets forum

        self.CopyUndo()

        if mode == 1 and self.vdu: self.vdu.AppendText("Transpose Pasting...\n")
        if self.vdu: self.vdu.AppendText("Copy clipboard...")

        if not wx.TheClipboard.Open():
            wx.MessageBox("Can't open the clipboard", "Warning")
            return False

        clipboard = wx.TextDataObject()
        wx.TheClipboard.GetData(clipboard)
        wx.TheClipboard.Close()
        data = clipboard.GetText()
   
        datasize = len(data)
        self.WriteVDU(f"OK, size {datasize}\nWriting cells...")

        i = self.GetGridCursorRow()
        j = self.GetGridCursorCol()
        if mode == 1: k = i
        else: k = j
        prog = 0.1

        print(repr(data))

        while not data == "":
            cur_line = data[:data.index('\n')]
            #if(vdu) vdu->AppendText(text.Format("\nRow %d", i));    
            while not cur_line == "":
                cur_field = cur_line[:cur_line.index('\t')]
                cur_field = cur_field.strip()
                if not cur_field == "": self.SetCell(i, j, cur_field)
                if mode == 1: i += 1  # transpose
                else: j += 1
                cur_line  = cur_line[cur_line.index('\t')+1:]
        
            if mode == 1:   # transpose
                j += 1 
                i = k
            else:           # normal
                i += 1
                j = k
            data = data[data.index('\n')+1:]
            if len(data) < datasize * (1 - prog): 
                self.WriteVDU(f"{prog * 100}%%")
                prog = prog + 0.1
        

        self.WriteVDU("OK\n")