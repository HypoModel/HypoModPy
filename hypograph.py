
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

        self.scrollbar = wx.ScrollBar(self, wx.ID_ANY, wx.Point(30, self.yplot + 35), wx.Size(self.xplot + 50, 15))
        self.scrollbar.SetScrollbar(0, 40, self.xplot, 40)

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

        xlabels = 10
        ylabels = 5

        #for graphdisp in self.dispset:

        # temp test graph
        graph = GraphDat()

        # Graph Parameters
        xfrom = graph.xfrom * graph.xscale
        xto = graph.xto * graph.xscale
            
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

        for i in range(0, xlabels+1):
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
                if srangex < 0.1: snum = "{:.3f}".format(xval + graph.xdis)
                elif srangex < 1: snum = "{:.2f}".format(xval + graph.xdis)
                elif srangex < 10: snum = "{:.1f}".format(xval + graph.xdis)
                else: snum = "{:.0f}".format(xval + graph.xdis)	
            else: snum = f"{xval + graph.xdis:.{graph.xlabelplaces}f}"

            if GetSystem() == 'Mac':
                textsize = gc.GetFullTextExtent(snum)
                gc.DrawText(snum, self.xbase + xcoord - textsize[0] / 2, self.ybase + self.yplot + 8)
            else:
                textsize = gc.GetFullTextExtent(snum)
                gc.DrawText(snum, self.xbase + xcoord - textsize[0] / 2, self.ybase + self.yplot + 10)
         