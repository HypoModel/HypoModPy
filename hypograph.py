
import wx
from hypocontrols import *



class GraphDat():
    def __init__(self):
        self.xaxis = True
        self.yaxis = True
        self.xfrom = 0
        self.xto = 500
        self.xscale = 1
        self.xdis = 0

        self.xtickmode = 1
        self.ytickmode = 1

        self.xshift = 0
        self.yshift  = 0

        self.xunitscale = 1
        self.yunitscale = 1
        self.xunitdscale = 1
        self.yunitdscale = 1

        self.xlabelmode = 1
        self.ylabelmode = 1
        self.xticklength = 5
        self.yticklength = 5
        self.xlabelplaces = -1
        self.ylabelplaces = -1
        self.xscalemode = 0 
        self.yscalemode = 0



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
        self.ostype = GetSystem()

        #wx.StaticText(self, label='GraphPanel')
        self.SetBackgroundColour(wx.WHITE)

        # Draw Parameters
        self.xbase = 40
        self.ybase = 10
        self.xplot = 500
        self.yplot = 200
        self.xstretch = parent.xstretch

        self.colourpen = parent.colourpen

        if self.ostype == 'Mac':
            self.textfont = wx.Font(wx.FontInfo(10).FaceName("Tahoma"))
            self.smallfont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))
        else:
            self.textfont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))
            self.smallfont = wx.Font(wx.FontInfo(6).FaceName("Tahoma"))

        #self.scrollbar = wx.ScrollBar(self, wx.ID_ANY, wx.Point(30, self.yplot + 35), wx.Size(self.xplot + 50, 15))
        #self.scrollbar.SetScrollbar(0, 40, self.xplot, 40)

        self.Bind(wx.EVT_PAINT, self.OnPaint)


    def ReSize(self, newxplot, newyplot):
        self.xplot = newxplot
        self.yplot = newyplot

        #self.scrollbar.SetSize(self.xplot + self.xstretch + 30, -1)
        #self.scrollbar.SetScrollbar(0, 40, self.xplot, 40)
        #self.scrollbar.Move(30, self.yplot + 35)

        #self.Layout()
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

        xlabels = 10
        ylabels = 5

        #for graphdisp in self.dispset:

        # temp test graph
        graph = GraphDat()

        # Graph Parameters
        xfrom = graph.xfrom * graph.xscale
        xto = graph.xto * graph.xscale
            
        #gc.SetPen(self.colourpen['black'])
        gc.SetPen(wx.BLACK_PEN)
        gc.SetFont(self.textfont, self.colourpen['black'])
        
        xaxislength = self.xplot
		#if(graph->axistrace && drawX != -1) xaxislength = drawX * binsize / (xto - xfrom) * xplot;
        #mod->diagbox->Write(text.Format("drawX %.0f xfrom %.0f xto %.0f xplot %d xaxislength %d\n", drawX, xfrom, xto, xplot, xaxislength));
        
        # Draw Axes
        if graph.xaxis: 
            gc.StrokeLine(self.xbase, self.ybase + self.yplot, self.xbase + xaxislength + self.xstretch, self.ybase + self.yplot)
        if graph.yaxis: 
            gc.StrokeLine(self.xbase, self.ybase, self.xbase, self.ybase + self.yplot)

        # Draw Axes Ticks and Labels

        # tickmode 0 - off | 1 - count | 2 - step
        # labelmode 0 - none | 1 - normal | 2 - only end labels

        # X-axis
        if graph.xtickmode == 2:
            xlabels = int((xto - xfrom) / (graph.xscale * graph.xstep))
            xplotstep = (self.xplot * graph.xstep) / (xto - xfrom)
            if xfrom != 0: xtickshift = xfrom
            xtickstart = abs(xtickshift) * xplotstep

        for i in range(0, xlabels):
            #Ticks
            xcoord = int(i * self.xplot / xlabels)
            if graph.xtickmode == 2: xcoord = (int(xplotstep * i) + xtickstart)
            if graph.xtickmode and xcoord <= xaxislength:
                 gc.StrokeLine(self.xbase + xcoord, self.ybase + self.yplot, self.xbase + xcoord, self.ybase + self.yplot + 5)

            # Labels
            if not graph.xlabelmode or xcoord > xaxislength or graph.xlabelmode == 2 and i > 0 and i < xlabels: continue
            if graph.xtickmode == 2:
                 xval = (xfrom + graph.xstep * i) * graph.xunitscale / graph.xunitdscale - graph.xshift - xtickshift
            else:
                xval = ((xto - xfrom) / xlabels * i + xfrom) / graph.xscale * graph.xunitscale / graph.xunitdscale - graph.xshift

            srangex = abs((xto - xfrom) / graph.xscale * graph.xunitscale / graph.xunitdscale)
            if graph.xlabelplaces == -1:
                if srangex < 0.1: snum = ":.3f".format(xval + graph.xdis)
                elif srangex < 1: snum = ":.2f".format(xval + graph.xdis)
                elif srangex < 10: snum = ":.1f".format(xval + graph.xdis)
                else: snum = ":.0f".format(xval + graph.xdis)	
            else: snum = f"{xval + graph.xdis:.{graph.xlabelplaces}f}"

            if GetSystem() == 'Mac':
                textsize = dc.GetTextExtent(snum)
                dc.DrawText(snum, self.xbase + xcoord - textsize.GetWidth() / 2, self.ybase + self.yplot + 10)
            else:
                textsize = gc.GetFullTextExtent(snum)
                gc.DrawText(snum, self.xbase + xcoord - textsize[0] / 2, self.ybase + self.yplot + 10)
         
        

class ScaleBox(ToolPanel):
    def __init__(self, parent, size, numdraw):
        #ToolPanel.__init__(self, parent, wx.DefaultPosition, size, wx.BORDER_SIMPLE)
        ToolPanel.__init__(self, parent, wx.DefaultPosition, size)

        iconpath = parent.initpath
        ostype = GetSystem()
        self.numdraw = numdraw
        self.SetFont(self.boxfont)
        if ostype == 'Mac': self.buttonheight = 20
        else: self.buttonheight = 23

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

        buttonbox = wx.BoxSizer(wx.HORIZONTAL)
        if ostype == 'Mac':
            self.ScaleButton(wx.ID_OK, "OK", 43, buttonbox)
            buttonbox.AddSpacer(2)
            self.ScaleButton(ID_Sync, "Sync", 43, buttonbox)
        else:
            self.ScaleButton(wx.ID_OK, "OK", 35, buttonbox)
            buttonbox.AddSpacer(2)
            syncbutton = self.ToggleButton(ID_Sync, "Sync", 35, buttonbox)

        vbox.Add(buttonbox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL)
        vbox.AddSpacer(3)
        storebox = self.StoreBox()
        vbox.Add(storebox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)	

        self.SetSizer(vbox)

        #wx.StaticText(self, label='ScaleBox')


    def StoreBox(self):
        label = 'gtest1'

        filebox = wx.BoxSizer(wx.VERTICAL)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        
        storetag = TagBox(self, label, wx.Size(80, 23), "scalebox", projectpath)
        storetag.SetFont(self.confont)

        if GetSystem() == 'Mac':
            self.AddButton(ID_Store, "Store", 43, buttons)
            buttons.AddSpacer(2)
            self.AddButton(ID_Load, "Load", 43, buttons)
        else:
            self.AddButton(ID_Store, "Store", 38, buttons)
            buttons.AddSpacer(2)
            self.AddButton(ID_Load, "Load", 38, buttons)

        filebox.Add(storetag, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 2)
        filebox.Add(buttons, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 2)
        return filebox
        

    def AddButton(self, id, label, width, box, pad = 1, height = 0):
        if height == 0: height = self.buttonheight
        button = ToolButton(self, id, label, wx.DefaultPosition, wx.Size(width, height))
        button.SetFont(self.confont)
        box.Add(button, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.TOP|wx.BOTTOM, pad)
        return button


    def ScaleButton(self, id, label, width, box):
        button = ToolButton(self, id, label, wx.DefaultPosition, wx.Size(width, self.buttonheight))
        button.SetFont(self.confont)
        box.Add(button, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.TOP|wx.BOTTOM, 1)
        return button

    
    def ToggleButton(self, id, label, width, box):
        button = wx.ToggleButton(self, id, label, wx.DefaultPosition, wx.Size(width, self.buttonheight))
        button.SetFont(self.confont)
        box.Add(button, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.TOP|wx.BOTTOM, 1)
        return button


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

        confont = wx.Font(wx.FontInfo(8).FaceName("Tahoma"))
        pbox = wx.BoxSizer(wx.HORIZONTAL)
        labeltext = wx.StaticText(self, wx.ID_STATIC, label, wx.DefaultPosition, wx.Size(-1, -1), 0)

        snum = "{}".format(initval)
        numbox = TextBox(self, wx.ID_ANY, snum, wx.DefaultPosition, wx.Size(boxwidth, boxheight), wx.TE_PROCESS_ENTER)
        labeltext.SetFont(confont)
        numbox.SetFont(confont)
        pbox.Add(labeltext, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        pbox.Add(numbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        psetbox.Add(pbox, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, boxgap)
        #numbox.Bind(wx.EVT_SET_FOCUS, self.OnConFocus, self)
        numbox.val = index
            
        return numbox