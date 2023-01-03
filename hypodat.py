
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

        self.xlabels = 0
        self.ylabels = 0
        self.xstep = 0
        self.ystep = 0

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

        self.plotstroke = 0.5
        self.strokecolour = wx.Colour(0, 0, 0)
        self.fillcolour = wx.Colour(255, 255, 255)

        self.xplot = 500
        self.yplot = 200
        self.xsample = 1

        self.xlabelgap = 30  #40
        self.ylabelgap = 30  #20 #30
        self.labelfontsize = 10
        self.tickfontsize = 10
        self.clipmode = 0

        self.barshift = 0
        self.barwidth = 10
        self.bargap = 10

        self.labelfont = 0   #default Helvetica
        self.fillmode = 1
        self.fillstroke = 0


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
        DiagWrite("strokecolourtext: " + strokecolourtext + "\n")

        gtext = "v1"
        gtext += f" tag {tag} xf {self.xfrom} xt {self.xto} yf {self.yfrom} yt {self.yto} xl {self.xlabels} xs {self.xstep} xm {self.xtickmode}"
        gtext += f" yl {self.ylabels} ys {self.ystep} ym {self.ytickmode} c {self.colour} srgb {strokecolourtext} xs {self.xshift} xu {self.xunitscale}"
        gtext += f" ps {self.plotstroke} name {storetitle} xtag {storextitle} ytag {storeytitle} xp {self.xplot} yp {self.yplot} pf {self.labelfontsize}"
        gtext += f" cm {self.clipmode} type {self.type} xd {self.xunitdscale} xsam {self.xsample} bw {self.barwidth} bg {self.bargap} yu {self.yunitscale}" 
        gtext += f" xl {self.xlabelplaces} yl {self.ylabelplaces} xm {self.xlabelmode} ym {self.ylabelmode} xs {self.xscalemode} ys {self.yscalemode}"
        gtext += f" xa {self.xaxis} ya {self.yaxis} yd {self.yunitdscale} xg {self.xlabelgap} yg {self.ylabelgap} lf {self.labelfont} sc {self.scattersize}"
        gtext += f" frgb {fillcolourtext} xfm {self.fillmode} fs {self.fillstroke} lm {self.linemode} sm {self.scattermode}"

        return gtext



class PlotBase():
    def __init__(self, mainwin):
        self.plotstore = {}
        self.setstore = {}
        self.mainwin = mainwin


    def BaseStore(self, filepath):
        outfile = TextFile(filepath)
        outfile.Open('w')

        for plot in self.plotstore:
            outfile.WriteLine(self.plotstore[plot].StoreDat(plot))

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

