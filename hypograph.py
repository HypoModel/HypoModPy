
import wx
from hypocontrols import *



class GraphDat():
    def __init__(self):
        self.xaxis = True
        self.yaxis = True



class GraphDisp():
    def __init__(self):
        self.numplots = 0
        self.currentplot = 0



class GraphPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)
        self.numdisps = 0
        self.frontdisp = 0
        self.dispset = []

        #wx.StaticText(self, label='GraphPanel')
        self.SetBackgroundColour(wx.WHITE)

        # Draw Parameters
        self.xbase = 40
        self.ybase = 10
        self.xplot = 500
        self.yplot = 200
        self.xstretch = parent.xstretch

        self.colourpen = parent.colourpen

        self.Bind(wx.EVT_PAINT, self.OnPaint)


    def ReSize(self, newxplot, newyplot):
        self.xplot = newxplot
        self.yplot = newyplot

        #scrollbar->SetSize(xplot + xstretch + 30, -1)
        #scrollbar->SetScrollbar(0, 40, xplot, 40)
        #scrollbar->Move(30, yplot + 35)
        #Layout();
        #self.UpdateScroll()
        #overlay.Reset();
	
        self.Refresh()

    
    def FrontGraph(self, graphdisp):
        if len(self.dispset) == 0: 
            self.dispset.append(graphdisp)
        else:
            self.dispset[0] = graphdisp


    def PaintBackground(self, dc):
        backgroundColour = self.GetBackgroundColour()
        if backgroundColour.Ok() == False: backgroundColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)

        dc.SetBrush(wx.Brush(backgroundColour))
        dc.SetPen(wx.Pen(backgroundColour, 1))
        
        windowRect = wx.Rect(wx.Point(0, 0), self.GetClientSize())
        dc.DrawRectangle(windowRect)


    def OnPaint(self, event):

        dc = wx.PaintDC(self)
        #dc = wx.BufferedPaintDC(self)
        #self.PaintBackground(dc)
        gc = wx.GraphicsContext.Create(dc)
        #dc.DrawLine(50, 60, 190, 60)

        #for graphdisp in self.dispset:

        # temp test graph
        graph = GraphDat()
            
        #gc.SetPen(self.colourpen['black'])
        gc.SetPen(wx.BLACK_PEN)
        
        xaxislength = self.xplot
		#if(graph->axistrace && drawX != -1) xaxislength = drawX * binsize / (xto - xfrom) * xplot;
        #mod->diagbox->Write(text.Format("drawX %.0f xfrom %.0f xto %.0f xplot %d xaxislength %d\n", drawX, xfrom, xto, xplot, xaxislength));
        
        if graph.xaxis: 
            gc.StrokeLine(self.xbase, self.ybase + self.yplot, self.xbase + xaxislength + self.xstretch, self.ybase + self.yplot)
        if graph.yaxis: 
            gc.StrokeLine(self.xbase, self.ybase, self.xbase, self.ybase + self.yplot)
            
        

class ScaleBox(ToolPanel):
    def __init__(self, parent, size, numdraw):
        wx.Panel.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, size, wx.BORDER_SIMPLE)

        iconpath = parent.initpath
        self.numdraw = numdraw
        self.boxfont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))
        self.SetFont(self.boxfont)

        # Load Icons
        wx.Image.AddHandler(wx.PNGHandler())
        self.rightarrow = wx.Bitmap(iconpath + "/rightarrow.png", wx.BITMAP_TYPE_PNG)
        self.leftarrow = wx.Bitmap(iconpath + "/leftarrow.png", wx.BITMAP_TYPE_PNG)
        self.uparrow = wx.Bitmap(iconpath + "/uparrow.png", wx.BITMAP_TYPE_PNG)
        self.downarrow = wx.Bitmap(iconpath + "/downarrow.png", wx.BITMAP_TYPE_PNG)

        wx.StaticText(self, label='ScaleBox')
