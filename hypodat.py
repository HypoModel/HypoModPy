
from hypobase import *



class PlotSet():
    def __init__(self):
        self.ptags = []
        self.pcodes = {}
        self.label = ""
        self.tag = ""
        self.modeflags = []           # Set of flags is used to control the selected, displayed graph 
        self.modeweights = {}
        self.single = True
        self.submenu = 0
        self.modesum = 0
        #self.subplot = []


    def AddPlot(self, ptag, pcode = -1): 
        self.ptags.append(ptag)
        self.pcodes[ptag] = pcode
        if len(self.ptags) > 1: self.single = False


    def AddFlag(self, flag, weight):
        self.modeflags.append(flag)
        self.modeweights.append(weight)


    def GetPlot(self, subplot, gflags):
        if self.single: return self.ptags[0]

        if self.submenu: 
            if subplot: return self.ptags[subplot]    
            else: return self.ptags[0]

        self.modesum = 0
        plottag = self.ptags[0]
        for modeflag in self.modeflags: self.modesum = self.modesum + gflags[modeflag] * self.modeweights[modeflag]
        for tag in self.ptags:
            if self.pcodes[tag] == self.modesum: plottag = self.ptag[tag]

        return plottag
        


class PlotDat():
    def __init__(self, data = np.zeros(0), xf = 0, xt = 500, yf = 0, yt = 1000, label = "", type = None, binsize = 1, colour = "red", xs = 1, xd = 0):

        self.xscale = xs
        self.xdis = xd
        self.spikedata = None

        self.xdata = None
        self.xcount = 0
        self.ycount = 0
        self.data = data

        self.type = type
        self.samprate = 1
        self.scattermode = 0
        self.linemode = 1
        self.scattersize = 2

        self.xfrom = xf
        self.xto = xt
        self.xmin = xf
        self.xmax = xt
        self.yfrom = yf
        self.yto = yt
        self.label = label
        self.colour = colour
        self.binsize = binsize

        self.Default()


    def Default(self):

        self.xtitle = "X"
        self.ytitle = "Y"

        self.xaxis = True
        self.yaxis = True

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

        self.scrollpos = 0
        self.xrel = 0

        self.negscale = 0   # check purpose
        self.synchx = 1     # toggle to allow x-axis synchronisation, typically used for common time axis

        self.strokecolour = wx.Colour(0, 0, 0)
        self.fillcolour = wx.Colour(255, 255, 255)


    def StoreDat(self, tag):
        if self.label != "": storetitle = self.label         # replace spaces with underscores for textfile storing
        else: storetitle = " "
        storetitle.replace(" ", "_")

        if self.xtitle != "": storextitle = self.xtitle
        else: storextitle = " "
        storextitle.replace(" ", "_")

        if self.ytitle != "": storeytitle = self.ytitle
        else: storeytitle = " "
        storeytitle.replace(" ", "_")
    
        strokecolourtext = self.strokecolour.GetAsString(wx.C2S_CSS_SYNTAX)
        fillcolourtext = self.fillcolour.GetAsString(wx.C2S_CSS_SYNTAX)
    
        DiagWrite("strokecolourtext: " + strokecolourtext)

        #gtext1.Printf("v12 index %d tag %s xf %.4f xt %.4f yf %.4f yt %.4f xl %d xs %.4f xm %d yl %d ys %.4f ym %d c %d srgb %s xs %.4f xu %.4f ps %.4f name %s xtag %s ytag %s xp %d yp %d pf %.4f cm %d type %d xd %.4f xsam %.4f bw %.4f bg %.4f yu %.4f ", 
        #gindex, tag, xfrom, xto, yfrom, yto, xlabels, xstep, xtickmode, ylabels, ystep, ytickmode, colour, strokecolourtext, xshift, xunitscale, plotstroke, storegname, storextag, storeytag, xplot, yplot, labelfontsize, clipmode, type, xunitdscale, xsample, barwidth, bargap, yunitscale);

        #gtext2.Printf("xl %d yl %d xm %d ym %d xs %d ys %d xa %d ya %d yd %.4f xg %.4f yg %.4f lf %d sc %.4f frgb %s xfm %d fs %d lm %d sm %d", 
        #xlabelplaces, ylabelplaces, xlabelmode, ylabelmode, xscalemode, yscalemode, xaxis, yaxis, yunitdscale, xlabelgap, ylabelgap, labelfont, scattersize, fillcolourtext, fillmode, fillstroke, linemode, scattermode);

        return gtext1 + gtext2



class PlotBase():
    def __init__(self, mainwin):
        self.plotstore = {}
        self.setstore = {}
        self.mainwin = mainwin


    def BaseStore(self, filepath):
        outfile = TextFile(filepath)
        outfile.Open('w')

        for plot in self.plotstore.values():
            outfile.WriteLine(plot.StoreDat())

        outfile.Close()
        DiagWrite("BaseStore {} graphs\n".format(len(self.plotstore)))


    def Add(self, newplot, plottag, pstag = ""):       # default settag = "", for no set use settag = "null"
        plotset = None
        diag = True

        if diag: DiagWrite("Plotbase Add {} to set {}, numgraphs {}\n".format(plottag, pstag, len(self.plotstore)))
    
        # colour setting is done here since GraphDat doesn't have access to mainwin colour chart
        newplot.strokecolour = self.mainwin.colourpen[newplot.colour]
        newplot.fillcolour = newplot.strokecolour
        newplot.plottag = plottag
    
        #mainwin->diagbox->Write(text.Format("GraphBase Add colour index %d string %s\n", newgraph.colour, ColourString(newgraph.strokecolour, 1)));

        # If single graph, create new single graph set, otherwise add to set 'settag'
        # single plot sets use the same tag as the plot
        if pstag != None:
            if pstag == "": plotset = self.NewSet(newplot.label, plottag)
            else: plotset = self.setstore[pstag]

            if plotset:   # extra check, should only fail if 'settag' is invalid
                plotset.AddPlot(plottag)
                newplot.pstag = pstag

        if diag: DiagWrite("GraphSet Add OK\n")

        # Add the new graph to graphbase
        self.plotstore[plottag] = newplot
        
        if diag: DiagWrite("GraphBase Add OK\n")


    def NewSet(self, label, tag): 
        self.setstore[tag] = PlotSet()
        self.setstore[tag].label = label
        self.setstore[tag].tag = tag
        return self.setstore[tag]


    def GetSet(self, tag):
        return self.setstore[tag]


    def GetPlot(self, tag):
        return self.plotstore[tag]

