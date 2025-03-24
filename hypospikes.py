

import wx
import random
import numpy as np

from HypoModPy.hypomods import *
from HypoModPy.hypoparams import *
from HypoModPy.hypodat import *
from HypoModPy.hypogrid import *




class SpikeDataBox(ParamBox):
    def __init__(self, mod, tag, title, pos, size):      
        ParamBox.__init__(self, mod, title, pos, size, tag)

        self.mod = mod
        self.cellpanel = None
        self.notebook = wx.Notebook(self.panel, -1, wx.Point(-1,-1), wx.Size(-1, 400), wx.NB_TOP)

        self.cellpanel = SpikeDataPanel(self)
        #cellpanel->cellmode = true;
        #cellpanel->ratetag = "cellspikes";
        self.notebook.AddPage(self.cellpanel, "Cell")
        self.mainbox.Add(self.notebook, 1, wx.EXPAND)


class SpikeDataPanel(ToolPanel):
    def __init__(self, parent):
        ToolPanel.__init__(self, parent.notebook, wx.DefaultPosition, wx.DefaultSize)
        self.databox = parent

        # Panel layout annd formatting
        self.SetFont(parent.boxfont)
        mainbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(mainbox)
        parent.activepanel = self
        parent.paramset.panel = self

        # Panel data
        self.cellcount = 10
        self.cellindex = 0

        # Neuron selection
        datwidth = 50
        labelwidth = 70
        self.label = parent.NumPanel(labelwidth, wx.ALIGN_CENTRE)
        self.spikes = parent.NumPanel(datwidth, wx.ALIGN_RIGHT)
        self.freq = parent.NumPanel(datwidth, wx.ALIGN_RIGHT)
        self.selectspikecount = parent.NumPanel(datwidth, wx.ALIGN_RIGHT)
        self.selectfreq = parent.NumPanel(datwidth, wx.ALIGN_RIGHT)

        datagrid = wx.GridSizer(2, 5, 5)
        datagrid.Add(wx.StaticText(self, wx.ID_STATIC, "Name"), 0, wx.ALIGN_CENTRE)
        datagrid.Add(self.label)
        datagrid.Add(wx.StaticText(self, wx.ID_STATIC, "Spikes"), 0, wx.ALIGN_CENTRE)
        datagrid.Add(self.spikes)
        datagrid.Add(wx.StaticText(self, wx.ID_STATIC, "Freq"), 0, wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE)
        datagrid.Add(self.freq)
        datagrid.Add(wx.StaticText(self, wx.ID_STATIC, "Select Spikes"), 0, wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE)
        datagrid.Add(self.selectspikecount)
        datagrid.Add(wx.StaticText(self, wx.ID_STATIC, "Select Freq"), 0, wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE)
        datagrid.Add(self.selectfreq)

        self.datneuron = wx.TextCtrl(self, wx.ID_ANY, "---", wx.DefaultPosition, wx.Size(50, -1), wx.ALIGN_LEFT|wx.BORDER_SUNKEN|wx.ST_NO_AUTORESIZE|wx.TE_PROCESS_ENTER)
        datspin = wx.SpinButton(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, -1), wx.SP_HORIZONTAL|wx.SP_ARROW_KEYS)
        datspin.SetRange(-1000000, 1000000)
        datspin.Bind(wx.EVT_SPIN_UP, self.OnNext)
        datspin.Bind(wx.EVT_SPIN_DOWN, self.OnPrev)

        datbox = wx.BoxSizer(wx.HORIZONTAL)
        datbox.Add(datspin, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL)
        datbox.AddSpacer(5)

        cellbox = wx.BoxSizer(wx.HORIZONTAL)
        cellbox.Add(wx.StaticText(self, wx.ID_ANY, "Neuron"), 1, wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE)
        cellbox.Add(self.datneuron, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5)

        databox = wx.StaticBoxSizer(wx.VERTICAL, self, "")
        databox.AddSpacer(2)
        databox.Add(cellbox, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL| wx.ALL, 5)
        databox.AddSpacer(5)
        databox.Add(datbox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL| wx.ALL, 0)
        databox.AddSpacer(5)
        databox.Add(datagrid, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5)

        mainbox.Add(databox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL)

        self.Layout()


    def SetCount(self, count):
       self.cellcount = count
       if self.cellindex > self.cellcount: self.cellindex = 0
       #neuropop.numneurons = count;


    def OnNext(self, event):
        if self.cellcount == 0: return
        if self.cellindex < self.cellcount - 1: self.cellindex += 1
        else: self.cellindex = 0
        self.CellData()


    def OnPrev(self, event):
        if self.cellcount == 0: return
        if self.cellindex > 0: self.cellindex -= 1
        else: self.cellindex = self.cellcount - 1
        self.CellData()


    def CellData(self):
        self.databox.mod.NeuroData()
        #self.PanelData()


    def PanelData(self, cellspike):
        self.datneuron.SetLabel(numstring(self.cellindex))
        self.label.SetLabel(cellspike.name)
        self.spikes.SetLabel(numstring(cellspike.spikecount))
        self.freq.SetLabel(numstring(cellspike.freq, 2))
    	#selectspikecount->SetLabel(snum.Format("%d", currneuron->selectdata->intraspikes));
	    #selectfreq->SetLabel(snum.Format("%.2f", currneuron->selectdata->freq));

        # Store rate X-axis position
        #graphwin = neurobox->mod->GetGraphWin(ratetag);
        #if(graphwin) currneuron->neurodata->xscrollpos = graphwin->xscrollpos;

        # Store select grids
        #for(int i=0; i<selectcount; i++) {
	    #currneuron->selectdata->spikes = selectspikes[i].data();
	#   currneuron->SelectScan(i);  // store current cell's select grid to NeuroDat
        
       
class NeuroDat():
    def __init__(self):
        self.maxspikes = 100000
        self.times = pdata(self.maxspikes)
        self.spikecount = 0
        self.name = ""
        self.timeform = "s"   # "s" or "ms" for seconds or milliseconds


class SpikeDat():
    def __init__(self):

        self.maxspikes = 100000
        self.spikecount = 0
        self.times = pdata(self.maxspikes)
        self.isis = pdata(self.maxspikes)
        self.freq = 0

        # initialise arrays for spike interval analysis
        self.histsize = 50000
        #self.hist1 = pdata(self.histsize + 1)
        self.hist1 = datarray(self.histsize + 1)
        self.hist5 = pdata(self.histsize + 1)
        self.hist1norm = pdata(self.histsize + 1)
        self.hist5norm = pdata(self.histsize + 1)
        self.haz1 = pdata(self.histsize + 1)
        self.haz5 = pdata(self.histsize + 1)

        # IoD data
        self.IoDdata = datarray(100)
        self.IoDdataX = datarray(100)

        # initialise arrays for spike rate
        self.srate1s = datarray(10000)

        self.normscale = 10000   # normalise and scale histogram to normscale spikecount 


    def Analysis(self, neurodata=None):
        maxtime = 100000

        DiagWrite("Analysis() call\n")

        # reset spike interval analysis stores
        self.hist1.clear()
        self.hist5.clear()
        self.haz1.clear()
        self.haz5.clear()
        self.hist1norm.clear()
        self.hist5norm.clear()

        self.hist1.xmax = 0
        self.hist5.xmax = 0
        self.hist1norm.xmax = 0
        self.hist5norm.xmax = 0
        self.haz1.xmax = 0
        self.haz5.xmax = 0

        # reset spike rate stores
        self.srate1s.clear()

        mean = 0
        variance = 0
        binsize = 5

        if neurodata != None:
            self.spikecount = neurodata.spikecount
            self.maxspikes = neurodata.maxspikes
            #DiagWrite(f"SpikeDat Analysis() name {neurodata.name} spikecount {neurodata.spikecount}\n")

        if self.spikecount == 0: 
            DiagWrite("Analysis() No spikes found\n")
            return

        # ISIs, Histogram, Freq, Variance

        isicount = self.spikecount - 1
        if neurodata != None: self.times[0] = neurodata.times[0]

        # DiagWrite(f"SpikeDat Analysis() times[0] {neurodata.times[0]}\n")
        # DiagWrite(f"SpikeDat Analysis() times[1] {neurodata.times[1]}\n")
        # DiagWrite(f"SpikeDat Analysis() times[2] {neurodata.times[2]}\n")

        # 1ms ISI Histogram
        for i in range(isicount):                                   
            if i > self.maxspikes: break
            if neurodata != None: self.times[i+1] = neurodata.times[i+1]
            self.isis[i] = self.times[i+1] - self.times[i]
            if self.hist1.xmax < int(self.isis[i]): self.hist1.xmax = int(self.isis[i])
            #if self.hist1.size < self.hist1.xmax + 1: self.hist1.resize(self.hist1.xmax + 1)
            np.resize(self.hist1, 20000)
            if self.hist1.size < self.hist1.xmax + 1: np.resize(self.hist1, 20000)
            self.hist1[int(self.isis[i])] += 1
            mean = mean + self.isis[i] / isicount
            variance = self.isis[i] * self.isis[i] / isicount + variance;

        # spike interval statistics
        isisd = sqrt(variance - mean * mean)
        self.freq = 1000 / mean
        if mean == 0: freq = 0
        meanisi = mean
        isivar = variance

        # 5ms ISI Histogram
        for i in range(self.hist1.xmax + 1):
            if i/binsize > self.hist5.xmax: self.hist5.xmax =  i/binsize
            self.hist5[int(i/binsize)] = self.hist5[int(i/binsize)] + self.hist1[i]

        # Normalise histograms
        for i in range(self.hist1.xmax + 1):
            self.hist1norm[i] = self.normscale * self.hist1[i] / isicount
            self.hist5norm[i] = self.normscale * self.hist5[i] / isicount

        self.hist1norm.xmax = self.hist1.xmax
        self.hist5norm.xmax = self.hist5.xmax
        
        # Hazards
        hazcount = 0
        self.haz1.xmax = self.hist1.xmax
        self.haz5.xmax = self.hist5.xmax

        # 1ms Hazard
        for i in range(self.hist1.xmax + 1):
            self.haz1[i] = self.hist1[i] / (self.spikecount - hazcount)
            hazcount = hazcount + self.hist1[i]

        # 5ms Hazard 
        for i in range(self.hist1.xmax + 1):                                                
            self.haz5[int(i/binsize)] = self.haz5[int(i/binsize)] + self.haz1[i]


        # Rate Count (1s)
        spikestep = 0
        self.srate1s.xmax = int((self.times[self.spikecount - 1] / 1000 + 0.5))
        #self.srate1s.maxindex = srate1s.max;
        for i in range(int(self.times[self.spikecount - 1] / 1000)):     # spike rate count (1s)
            if spikestep > self.spikecount: break
            while self.times[spikestep] / 1000 < i+1:
                if i < maxtime: self.srate1s[i] += 1
                spikestep += 1
                if spikestep >= self.spikecount: break


        # Index of Dispersion Range
        self.IoDdata.clear()
        self.IoDdata[0] = self.dispcalc(500)
        self.IoDdata[1] = self.dispcalc(1000)
        self.IoDdata[2] = self.dispcalc(2000)
        self.IoDdata[3] = self.dispcalc(4000)
        self.IoDdata[4] = self.dispcalc(6000)
        self.IoDdata[5] = self.dispcalc(8000)
        self.IoDdata[6] = self.dispcalc(10000)             

        self.IoDdataX[0] = 5
        self.IoDdataX[1] = 15
        self.IoDdataX[2] = 25
        self.IoDdataX[3] = 35
        self.IoDdataX[4] = 45
        self.IoDdataX[5] = 55
        self.IoDdataX[6] = 65

        DiagWrite(f"SpikeDat Analysis() freq {self.freq:.2f}\n")

        #for i in range(1, 50):
        #    DiagWrite(f"hist5 bin {i} {self.hist5[i]}\n")

    def dispcalc(self, binsize):
        maxbin = 10000
        spikerate = datarray(10000)
        dispersion = 0
        timeshift = 0

        # calculate spike rate for binsize
        spikerate.clear()
        for i in range(self.spikecount):
            if (self.times[i] - timeshift) / binsize < maxbin: spikerate[int(((self.times[i] - timeshift) + 0.5) / binsize)] += 1
           
        laststep = int((self.times[self.spikecount - 1] - timeshift) / binsize) - 4
        if laststep > maxbin: laststep = maxbin

        # calculate index of dispersion
        mean = 0;
        variance = 0;
        for i in range(laststep): mean = mean +  spikerate[i]    # mean
        mean = mean / laststep;
        for i in range(laststep): variance += (mean - spikerate[i]) * (mean - spikerate[i]);	# variance
        variance = variance / laststep;
        dispersion = variance / mean        # dispersion

        return dispersion