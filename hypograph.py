
import wx
from hypocontrols import *



class PlotDat():
    def __init__(self):
        self.xaxis = True
        self.yaxis = True
        self.xfrom = 0
        self.xto = 500
        self.xscale = 1
        self.xdis = 0

        self.xmin = 0
        self.xmax = 1000

        self.yfrom = 0
        self.yto = 10000
        self.yscale = 1

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

        self.xticklength = 5
        self.yticklength = 5

        self.data = None
        self.xdata = None
        self.binsize = 1
        self.scrollpos = 0
        self.xrel = 0

        self.negscale = 0   # check purpose
        self.synchx = 1     # toggle to allow x-axis synchronisation, typically used for common time axis



class GraphDisp():
    def __init__(self):
        self.numplots = 0
        self.currentplot = 0
        self.plots = []

    def GetFront(self):
        return self.plots[0]

    def Add(self, plot):
        self.plots.append(plot)

    # XYSynch() - Synchronise X and Y axes for all plots
    def XYSynch(self, plotzero=None):  
        if plotzero == None: plotzero = self.plots[0]
        
        for plot in self.plots:
            plot.yfrom = plotzero.yfrom
            plot.yto = plotzero.yto
            plot.xfrom = plotzero.xfrom
            plot.xto = plotzero.xto
	


class GraphPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)
        self.numdisps = 0
        self.frontdisp = 0
        self.dispset = []
        self.ostype = GetSystem()
        self.gsynch = 0

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

        self.scrollbar = wx.ScrollBar(self, wx.ID_ANY, wx.Point(self.xbase, self.yplot + 35), wx.Size(self.xplot + 50, -1))
        self.scrollbar.SetScrollbar(0, 40, self.xplot + 40, 50)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SCROLL, self.OnScroll)


    def XYSynch(self):
        for graphdisp in self.dispset: 
            graphdisp.XYSynch()


    def ScrollUpdate(self):
        plot = self.GetFront()
        if not plot: return
        if not plot.data:
            #mod->diagbox->Write("plot " + graph->gname + " no data\n")
            #return
            max = 1000
        else: plot.xmax = plot.data.max / plot.xscale
        if plot.xdata: plot.xmax = plot.gdatax.max

        xdiff = plot.xto - plot.xfrom
        plot.xrel = plot.xfrom - plot.scrollpos     # relative adjustment for non-zero xfrom set from scale panel
        if plot.xrel < plot.xmin: plot.xrel = plot.xmin

        scrollxto = int((plot.xmax - plot.xrel) * plot.binsize)
        section = int(xdiff)
        if section > scrollxto:
            plot.scrollpos = 0

        self.scrollbar.SetScrollbar(plot.scrollpos, section, scrollxto, section)

        #self.Refresh()
        #overlay.Reset()


    def OnScroll(self, event):
        xscrollpos = event.GetPosition()
        self.ScrollX(xscrollpos)


    def ScrollX(self, xpos):
        self.xscrollpos = xpos

        for graphdisp in self.dispset:
            plot = graphdisp.GetFront()
            xfrom = plot.xfrom
            xdiff = plot.xto - plot.xfrom
            plot.xfrom = xpos + plot.xrel
            plot.xto = xpos + xdiff + plot.xrel
            self.xf.SetNumValue(plot.xfrom, xdiff)
            self.xt.SetNumValue(plot.xto, xdiff)
            plot.scrollpos = xpos

        text = "scroll xpos {} xfrom {} xrel {}".format(xpos, xfrom, plot.xrel)
        pub.sendMessage("status_listener", message=text)

        #if self.gsynch: pub.sendMessage("scroll_listener", graphdisp.index, xpos)
        #else: self.Refresh()
        pub.sendMessage("scroll_listener", index=self.index, pos=xpos)


    def ReSize(self, newxplot, newyplot):
        self.xplot = newxplot
        self.yplot = newyplot

        self.scrollbar.SetSize(self.xplot, -1)
        self.scrollbar.Move(self.xbase, int(self.yplot + 35))
        
        #overlay.Reset();
        self.Refresh()


    def GetFront(self):
        return self.dispset[0].plots[0]

    
    def SetFront(self, graphdisp):
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
        xylab = 2

        for graphdisp in self.dispset:
            for plot in graphdisp.plots:

                # temp test graph
                # plot = PlotDat()

                # Graph Parameters
                xfrom = plot.xfrom * plot.xscale
                xto = plot.xto * plot.xscale
                yfrom = plot.yfrom * plot.yscale
                yto = plot.yto * plot.yscale
                    
                gc.SetPen(wx.BLACK_PEN)
                gc.SetFont(self.textfont, self.colourpen['black'])
                
                xaxislength = self.xplot
                #if(graph->axistrace && drawX != -1) xaxislength = drawX * binsize / (xto - xfrom) * xplot;
                #mod->diagbox->Write(text.Format("drawX %.0f xfrom %.0f xto %.0f xplot %d xaxislength %d\n", drawX, xfrom, xto, xplot, xaxislength));
                
                # Draw Axes
                if plot.xaxis: 
                    gc.StrokeLine(self.xbase, self.ybase + self.yplot, self.xbase + xaxislength + self.xstretch, self.ybase + self.yplot)
                if plot.yaxis: 
                    gc.StrokeLine(self.xbase, self.ybase, self.xbase, self.ybase + self.yplot)

                # Draw Axes Ticks and Labels

                # tickmode 0 - off | 1 - count | 2 - step
                # labelmode 0 - none | 1 - normal | 2 - only end labels

                # X-axis
                if plot.xtickmode == 2:
                    xlabels = int((xto - xfrom) / (plot.xscale * plot.xstep))
                    xplotstep = (self.xplot * plot.xstep) / (xto - xfrom)
                    if xfrom != 0: xtickshift = xfrom
                    xtickstart = abs(xtickshift) * xplotstep

                for i in range(0, xlabels+1):

                    #Ticks
                    if plot.xtickmode == 2: xcoord = (int(xplotstep * i) + xtickstart)
                    else: xcoord = int(i * self.xplot / xlabels)
                    if plot.xtickmode and xcoord <= xaxislength:
                        gc.StrokeLine(self.xbase + xcoord, self.ybase + self.yplot, self.xbase + xcoord, self.ybase + self.yplot + plot.xticklength)

                    # Labels
                    if not plot.xlabelmode or xcoord > xaxislength or plot.xlabelmode == 2 and i > 0 and i < xlabels: continue
                    if plot.xtickmode == 2:
                        xval = (xfrom + plot.xstep * i) * plot.xunitscale / plot.xunitdscale - plot.xshift - xtickshift
                    else:
                        xval = ((xto - xfrom) / xlabels * i + xfrom) / plot.xscale * plot.xunitscale / plot.xunitdscale - plot.xshift

                    srangex = abs((xto - xfrom) / plot.xscale * plot.xunitscale / plot.xunitdscale)
                    if plot.xlabelplaces == -1:
                        if srangex < 0.1: snum = "{:.3f}".format(xval + plot.xdis)
                        elif srangex < 1: snum = "{:.2f}".format(xval + plot.xdis)
                        elif srangex < 10: snum = "{:.1f}".format(xval + plot.xdis)
                        else: snum = "{:.0f}".format(xval + plot.xdis)	
                    else: snum = f"{xval + plot.xdis:.{plot.xlabelplaces}f}"

                    if GetSystem() == 'Mac':
                        textsize = gc.GetFullTextExtent(snum)
                        gc.DrawText(snum, self.xbase + xcoord - textsize[0] / 2, self.ybase + self.yplot + 8)
                    else:
                        textsize = gc.GetFullTextExtent(snum)
                        gc.DrawText(snum, self.xbase + xcoord - textsize[0] / 2, self.ybase + self.yplot + 10)


                # Y-axis
                if plot.ytickmode == 2:
                    ylabels = int((yto - yfrom) / (plot.yscale * plot.ystep))
                    yplotstep = (self.xplot * plot.xstep) / (yto - yfrom)

                for i in range(0, ylabels+1):

                    #Ticks
                    if plot.ytickmode == 2: ycoord = int(yplotstep * i)
                    else: ycoord = int(i * self.yplot / ylabels)
                    if plot.ytickmode:
                        gc.StrokeLine(self.xbase, self.ybase + self.yplot - ycoord, self.xbase - plot.yticklength, self.ybase + self.yplot - ycoord)

                    # Labels
                    if not plot.ylabelmode or plot.ylabelmode == 2 and i > 0 and i < ylabels: continue
                    if plot.ytickmode == 2:
                        yval = (yfrom + plot.ystep * i) * plot.yunitscale / plot.yunitdscale - plot.yshift
                    else:
                        yval = ((yto - yfrom) / ylabels * i + yfrom) / plot.yscale * plot.yunitscale / plot.yunitdscale - plot.yshift

                    srangey = abs((yto - yfrom) / plot.yscale * plot.yunitscale / plot.yunitdscale)
                    if plot.ylabelplaces == -1:
                        if srangey < 0.1: snum = "{:.3f}".format(yval)
                        elif srangey < 1: snum = "{:.2f}".format(yval)
                        elif srangey < 10: snum = "{:.1f}".format(yval)
                        else: snum = "{:.0f}".format(yval)	
                    else: snum = f"{yval + plot.ydis:.{plot.ylabelplaces}f}"

                    if GetSystem() == 'Mac':
                        textsize = gc.GetFullTextExtent(snum)
                        gc.DrawText(snum, self.xbase - xylab - plot.yticklength - textsize[0], self.ybase + self.yplot - ycoord - textsize[1] / 2)
                    else:
                        textsize = gc.GetFullTextExtent(snum)
                        gc.DrawText(snum, self.xbase - xylab - textsize[0], self.ybase + self.yplot - ycoord - 7)
                        
         