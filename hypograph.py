
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
        ToolPanel.__init__(self, parent, wx.DefaultPosition, size, wx.BORDER_SIMPLE)

        iconpath = parent.initpath
        self.numdraw = numdraw
        self.SetFont(self.boxfont)

        # Load Icons
        wx.Image.AddHandler(wx.PNGHandler())
        self.rightarrow = wx.Bitmap(iconpath + "/rightarrow.png", wx.BITMAP_TYPE_PNG)
        self.leftarrow = wx.Bitmap(iconpath + "/leftarrow.png", wx.BITMAP_TYPE_PNG)
        self.uparrow = wx.Bitmap(iconpath + "/uparrow.png", wx.BITMAP_TYPE_PNG)
        self.downarrow = wx.Bitmap(iconpath + "/downarrow.png", wx.BITMAP_TYPE_PNG)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.AddSpacer(5)
        self.vconbox = wx.BoxSizer(wx.VERTICAL)

        for graphpanel in parent.panelset:
            self.AddGraphConsole(graphpanel)
		    #gsync[i] = NULL;
            
        vbox.Add(self.vconbox, 1)

        wx.StaticText(self, label='ScaleBox')


    def AddGraphConsole(self, graphpanel):
        psetbox = wx.BoxSizer(wx.VERTICAL)
        graphpanel.consolebox = wx.BoxSizer(wx.VERTICAL)
        zoombox = wx.BoxSizer(wx.HORIZONTAL)

        graphpanel.yf = self.AddScaleParam("YF", 0, psetbox, graphpanel.index)
        graphpanel.yt = self.AddScaleParam("YT", 10, psetbox, graphpanel.index)
        graphpanel.xf = self.AddScaleParam("XF", 0, psetbox, graphpanel.index)
        graphpanel.xt = self.AddScaleParam("XT", 500, psetbox, graphpanel.index)

        graphpanel.yzoomin = wx.BitmapButton(self, 1000 + graphpanel.index, self.downarrow, wx.DefaultPosition, wx.Size(20, 20))
        graphpanel.yzoomout = wx.BitmapButton(self, 1010 + graphpanel.index, self.uparrow, wx.DefaultPosition, wx.Size(20, 20))
        graphpanel.xzoomin = wx.BitmapButton(self, 1100 + graphpanel.index, self.leftarrow, wx.DefaultPosition, wx.Size(20, 20))
        graphpanel.xzoomout = wx.BitmapButton(self, 1110 + graphpanel.index, self.rightarrow, wx.DefaultPosition, wx.Size(20, 20))

        zoombox.Add(graphpanel.yzoomin, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        zoombox.Add(graphpanel.yzoomout, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        zoombox.AddSpacer(2)
        zoombox.Add(graphpanel.xzoomin, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        zoombox.Add(graphpanel.xzoomout, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)

        psetbox.Add(zoombox, 0, wx.ALIGN_CENTRE_HORIZONTAL)
        graphpanel.consolebox.Add(psetbox, 0, wx.ALIGN_CENTRE_HORIZONTAL)
        self.vconbox.Add(graphpanel.consolebox, 1, wx.ALIGN_CENTRE_HORIZONTAL, 0)


    def AddScaleParam(self, label, initval, psetbox, index):
        boxwidth = 45
        boxheight = -1
        boxgap = 2

        snum = "{}".format(initval)
        confont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))
        pbox = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, wx.ID_STATIC, label, wx.DefaultPosition, wx.Size(-1, -1), 0)

        numbox = TextBox(self, wx.ID_ANY, snum, wx.DefaultPosition, wx.Size(boxwidth, boxheight), wx.TE_PROCESS_ENTER)
        label.SetFont(confont)
        numbox.SetFont(confont)
        pbox.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        pbox.Add(numbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        psetbox.Add(pbox, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, boxgap)
        #numbox.Bind(wx.EVT_SET_FOCUS, self.OnConFocus, self)
        numbox.val = index
            
        return numbox