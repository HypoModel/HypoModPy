

import wx
import random
import numpy as np

from HypoModPy.hypobase import *
from HypoModPy.hypodat import pdata
from HypoModPy.hypoparams import ParamSet
from HypoModPy.hypotools import DiagWrite, ToolBox, ParamBox, ToolPanel


class SpikeDataBox(ParamBox):
    def __init__(self, mod, tag, title, pos, size):      
        ParamBox.__init__(self, mod, title, pos, size, tag)

        self.mod = mod
        self.cellpanel = None
        self.notebook = wx.Notebook(self.panel, -1, wx.Point(-1,-1), wx.Size(-1, 400), wx.NB_TOP)

        self.cellpanel = SpikeDataPanel(self)
        self.modpanel = SpikeDataPanel(self)
        #cellpanel->cellmode = true;
        #cellpanel->ratetag = "cellspikes";
        self.notebook.AddPage(self.cellpanel, "Cell")
        self.notebook.AddPage(self.modpanel, "Model")
        self.mainbox.Add(self.notebook, 1, wx.EXPAND)


class SpikeSelect():
    def __init__(self, panel, index):
        self.index = index
        self.panel = panel
        self.mode = 1
        self.buttspace = 20

        self.con = wx.StaticBoxSizer(wx.HORIZONTAL, self.panel, f"Selection {index+1}")

        self.addbutton = panel.ToggleButton("Add", 40, self.con)
        self.addbutton.Bind(wx.EVT_TOGGLEBUTTON, self.OnAddToggle)
        self.con.AddSpacer(self.buttspace)

        self.subbutton = panel.ToggleButton("Sub", 40, self.con)
        self.subbutton.Bind(wx.EVT_TOGGLEBUTTON, self.OnSubToggle)
        self.con.AddSpacer(self.buttspace)

        self.clearbutton = panel.databox.AddButton(wx.ID_ANY, "Clear", 40, self.con)
        self.clearbutton.Bind(wx.EVT_BUTTON, self.OnClear)
        self.con.AddSpacer(self.buttspace)

        self.invertbutton = panel.databox.AddButton(wx.ID_ANY, "Invert", 40, self.con)
        self.invertbutton.Bind(wx.EVT_BUTTON, self.OnInvert)

        self.spikes = np.zeros(100000, dtype=int)

    def OnAddToggle(self, event):
        self.mode = 1
        self.panel.currselect = self.index
        self.panel.AddSubToggle()
        self.panel.SelectUpdate()

    def OnSubToggle(self, event):
        self.mode = 2
        self.panel.currselect = self.index
        self.panel.AddSubToggle()
        self.panel.SelectUpdate()

    def OnClear(self, event):
        self.spikes.fill(0)
        self.panel.currselect = self.index
        self.panel.AddSubToggle()
        self.panel.SelectUpdate()

    def OnInvert(self, event):
        self.spikes[:] = (self.index + 1) - self.spikes
        self.panel.currselect = self.index
        self.panel.AddSubToggle()
        self.panel.SelectUpdate()

    
        
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

        # Select switches and stores
        self.selectcount = 2
        self.currselect = 0

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
        
        if GetSystem() == "Mac":
            prevbtn = wx.Button(self, wx.ID_ANY, "<", wx.DefaultPosition, wx.Size(28, 24))
            nextbtn = wx.Button(self, wx.ID_ANY, ">", wx.DefaultPosition, wx.Size(28, 24))

            prevbtn.Bind(wx.EVT_BUTTON, self.OnPrev)
            nextbtn.Bind(wx.EVT_BUTTON, self.OnNext)

            datbox = wx.BoxSizer(wx.HORIZONTAL)
            datbox.Add(prevbtn, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL)
            datbox.AddSpacer(4)
            datbox.Add(nextbtn, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL)
            datbox.AddSpacer(5)
        else:
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


        # Spike selection
        self.fromcon = self.databox.paramset.AddNum("from", "From", 0, 0, 30)
        self.tocon = self.databox.paramset.AddNum("to", "To", 100, 0, 20)

        fromtobox = wx.BoxSizer(wx.HORIZONTAL)
        fromtobox.Add(self.fromcon, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.RIGHT|wx.LEFT, 5)
        fromtobox.Add(self.tocon, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.RIGHT|wx.LEFT, 5)

        self.select = []
        for i in range(self.selectcount): 
            self.select.append(SpikeSelect(self, i))

        self.select[self.currselect].addbutton.SetValue(True)

        selectconbox = wx.BoxSizer(wx.VERTICAL)
        selectconbox.Add(fromtobox, 0, wx.ALIGN_CENTRE_HORIZONTAL)
        selectconbox.AddSpacer(10)

        for i in range(self.selectcount):
            selectconbox.Add(self.select[i].con, 0)
            if i < self.selectcount - 1: selectconbox.AddSpacer(10)

        columnbox = wx.BoxSizer(wx.HORIZONTAL)
        columnbox.AddStretchSpacer()
        columnbox.Add(databox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL)
        columnbox.AddSpacer(20)
        columnbox.Add(selectconbox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL)

        mainbox.Add(columnbox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL)
        self.Layout()


    def AddSubToggle(self):
        for select in self.select:
            select.addbutton.SetValue(False)
            select.subbutton.SetValue(False)

        select = self.select[self.currselect]
        if select.mode == 1: select.addbutton.SetValue(True)
        if select.mode == 2: select.subbutton.SetValue(True)


    def SelectUpdate(self):
        currdata = self.databox.mod.cellspike
        if not currdata.spikecount: return    # use spikecount to check for spike data

        if currdata.selectdata is None: return
        
        currdata.selectdata.spikes = self.select[self.currselect].spikes
        if not currdata.colourdata: 
            currdata.ColourSwitch(2)
            #mainwin->scalebox->ratedata = 2;
            #mainwin->scalebox->databutton->SetLabel("Select");

        self.AnalyseSelection()
        # if(cellmode && neurobox->burstbox) neurobox->burstbox->ExpDataScan(currneuron);
        # mainwin->scalebox->GraphUpdate();


    def SelectAdd(self):
        currdata = self.databox.mod.cellspike
        sfrom = self.fromcon.GetValue() * 1000
        sto = self.tocon.GetValue() * 1000
        select = self.select[self.currselect]

        for i in range(currdata.spikecount):
            if currdata.times[i] > sfrom and currdata.times[i] < sto:
                select.spikes[i] = self.currselect + 1

        self.SelectUpdate()


    def SelectSub(self):
        currdata = self.databox.mod.cellspike
        sfrom = self.fromcon.GetValue() * 1000
        sto = self.tocon.GetValue() * 1000
        select = self.select[self.currselect]

        for i in range(currdata.spikecount):
            if currdata.times[i] > sfrom and currdata.times[i] < sto:
                select.spikes[i] = 0

        self.SelectUpdate()


    def SetSelectRange(self, fromtime, totime):
        self.fromcon.SetValue(fromtime)
        self.tocon.SetValue(totime)

        if self.select[self.currselect].mode == 1: self.SelectAdd()
        if self.select[self.currselect].mode == 2: self.SelectSub()


    def SetDataCount(self, count):
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
        self.datneuron.ChangeValue(numstring(self.cellindex))
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
        self.index = -1

    def SetSize(self, newsize):
        self.times.resize(newsize)
        self.maxspikes = newsize
        DiagWrite(f"NeuroDat setsize {newsize}\n")

    # 15/3/26 ChatGPT suggested safe resize with new pdata
    def SetSizeSafe(self, newsize):
        newtimes = pdata(newsize)
        copylen = min(len(self.times), newsize)
        newtimes[:copylen] = self.times[:copylen]
        newtimes.xmax = newsize
        newtimes.empty = self.times.empty if hasattr(self.times, "empty") else True
        self.times = newtimes
        self.maxspikes = newsize


class SpikeDat():
    def __init__(self):

        self.maxspikes = 100000
        self.spikecount = 0
        self.times = pdata(self.maxspikes)
        self.isis = pdata(self.maxspikes)
        self.freq = 0

        # initialise arrays for spike interval analysis
        self.histsize = 20000
        #self.hist1 = pdata(self.histsize + 1)
        self.hist1 = pdata(self.histsize + 1)
        self.hist5 = pdata(self.histsize + 1)
        self.hist1norm = pdata(self.histsize + 1)
        self.hist5norm = pdata(self.histsize + 1)
        self.haz1 = pdata(self.histsize + 1)
        self.haz5 = pdata(self.histsize + 1)

        # IoD data
        self.IoDdata = pdata(100)
        self.IoDdataX = pdata(100)

        # Burst and select data
        self.selectdata = None
        self.burstdata = None

        # initialise arrays for spike rate
        self.srate1s = pdata(10000)

        self.normscale = 10000   # normalise and scale histogram to normscale spikecount 


    def Analysis(self, neurodata=None):
        maxtime = 100000

        DiagWrite("Analysis() call\n")

        # reset spike interval analysis stores
        self.hist1.reset()
        self.hist5.reset()
        self.haz1.reset()
        self.haz5.reset()
        self.hist1norm.reset()
        self.hist5norm.reset()

        self.hist1.xmax = 0
        self.hist5.xmax = 0
        self.hist1norm.xmax = 0
        self.hist5norm.xmax = 0
        self.haz1.xmax = 0
        self.haz5.xmax = 0

        # reset spike rate stores
        self.srate1s.reset()

        mean = 0
        variance = 0
        binsize = 5
        binmax1 = 20000
        binmax5 = 10000

        if neurodata is not None:
            self.spikecount = neurodata.spikecount
            self.maxspikes = neurodata.maxspikes
            #DiagWrite(f"SpikeDat Analysis() name {neurodata.name} spikecount {neurodata.spikecount}\n")

        if self.spikecount == 0: 
            DiagWrite("Analysis() No spikes found\n")
            return

        # ISIs, Histogram, Freq, Variance

        isicount = self.spikecount - 1
        if neurodata is not None: self.times[0] = neurodata.times[0]

        # 1ms ISI Histogram
        for i in range(isicount):                                   
            if i+1 >= self.maxspikes: break
            if neurodata is not None: self.times[i+1] = neurodata.times[i+1]
            self.isis[i] = self.times[i+1] - self.times[i]
            if self.isis[i] >= self.histsize: continue  # skip if spike interval is very large
            if self.hist1.xmax < int(self.isis[i]): self.hist1.xmax = int(self.isis[i])
            try:
                if self.isis[i] < self.histsize: self.hist1[int(self.isis[i])] += 1
            except Exception:
                DiagWrite(f"Analysis hist1 bad ISI bin index {i} bin {int(self.isis[i])}\n")
                DiagWrite(f"spiketime {self.times[i+1]} previous {self.times[i]}\n")
                return
            mean = mean + self.isis[i] / isicount
            variance = self.isis[i] * self.isis[i] / isicount + variance;

        # spike interval statistics
        isisd = sqrt(variance - mean * mean)
        self.freq = 1000 / mean
        if mean == 0: freq = 0
        meanisi = mean
        isivar = variance

        # 5ms ISI Histogram
        DiagWrite(f"Analysis hist5 size {self.hist5.size} hist1max {self.hist1.xmax}\n")
        for i in range(self.hist1.xmax + 1):
            bin = int(i / binsize)
            if bin > self.hist5.xmax: self.hist5.xmax =  bin
            try:
                if bin < self.histsize: self.hist5[bin] = self.hist5[bin] + self.hist1[i]
            except Exception:
                DiagWrite(f"Analysis hist5 bad bin {bin} size {self.histsize} index {i} hist1 {self.hist1[i]}\n")
                return

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
        self.IoDdata.reset()
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


    def dispcalc(self, binsize):
        maxbin = 10000
        spikerate = pdata(10000)
        dispersion = 0
        timeshift = 0

        # calculate spike rate for binsize
        spikerate.reset()
        for i in range(self.spikecount):
            if (self.times[i] - timeshift) / binsize < maxbin: spikerate[int(((self.times[i] - timeshift) + 0.5) / binsize)] += 1
           
        laststep = int((self.times[self.spikecount - 1] - timeshift) / binsize) - 4
        if laststep > maxbin: laststep = maxbin

        # calculate index of dispersion
        mean = 0
        variance = 0
        for i in range(laststep): mean = mean +  spikerate[i]    # mean
        mean = mean / laststep
        for i in range(laststep): variance += (mean - spikerate[i]) * (mean - spikerate[i]) 	# variance
        variance = variance / laststep
        dispersion = variance / mean        # dispersion

        return dispersion



class Burst:
	def __init__(self):
		self.start = 0
		self.end = 0
		self.count = 0
		self.time = 0
		self.numpulse = 0
		self.pmax = 0
		self.length = 0
		self.peak = 0



class BurstDat:
	def __init__(self, spikedata=None, select=False):
		self.spikedata = spikedata
		self.selectmode = select

		self.times = None
		self.spikes = None

		self.burstspikes = []
		self.bustore = []

		self.intraspikes = 0
		self.numbursts = 0

		self.intratime = 0
		self.meancount = 0
		self.meantime = 0
		self.meanlength = 0
		self.meansilence = 0
		self.sdlength = 0
		self.sdsilence = 0

		self.freq = 0
		self.meanisi = 0
		self.isivar = 0
		self.isisd = 0




class PanelCon:
    def __init__(self, label, tag, con):
        self.label = label
        self.tag = tag
        self.data = None
        self.con = con


class ConSet:
    def __init__(self):
        self.datcons = {}

    def Add(self, label, tag, con):
        self.datcons[tag] = PanelCon(label, tag, con)
        return self.datcons[tag]

    def GetCon(self, tag):
        return self.datcons.get(tag)

    def __iter__(self):
        return iter(self.datcons.values())


class BurstPanel:
    def __init__(self):
        self.spikedata = None
        self.intracons = ConSet()
        self.burstcons = ConSet()

      

# class BurstPanel:
#     intrarows = [("Spikes", "intraspikes"), 
#                  ("Freq", "intrafreq"), 
#                  ("Mean", "intraisimean"), 
#                  ("SD", "intraisisd")]

#     burstrows = [("Bursts", "numbursts"), 
#                  ("Mean Spikes", "meanspikes"), 
#                  ("Mean Length", "meanlength"), 
#                  ("Length SD", "sdlength"),
#                  ("Mean Silence", "meansilence"), 
#                  ("Silence SD", "sdsilence"), 
#                  ("Activity Q", "actQ"), 
#                  ("Mode Time", "modetime"),
#                  ("Mode Rate", "moderate"),
#                  ("Mean Peak", "meanpeak")]


#     def __init__(self):
#         self.spikedata = None
#         self.intradata = {}
#         self.burstdata = {}


#     def DataCons(self, datpanel):
#         numwidth = 50

#         for label, tag in datpanel.intrarows:
#             datpanel.intradata[tag] = self.NumPanel(numwidth)

#         for label, tag in datpanel.burstrows:
#             datpanel.burstdata[tag] = self.NumPanel(numwidth)

    

# class BurstPanel:
#     def __init__(self):
#         self.spikedata = None

#         self.intrabox = wx.BoxSizer(wx.VERTICAL)
#         self.burstbox = wx.BoxSizer(wx.VERTICAL)

#         self.numbursts = None
#         self.meanspikes = None
#         self.meanlength = None
#         self.meansilence = None
#         self.sdlength = None
#         self.sdsilence = None
#         self.actQ = None
#         self.modetime = None
#         self.moderate = None
#         self.meanpeak = None

#         self.intraspikes = None
#         self.intrafreq = None
#         self.intraisimean = None
#         self.intraisisd = None


# class BurstDataCon:
#     def __init__(self, label, con):
#         self.label = label
#         self.con = con


class BurstPanel:
    def __init__(self):
        self.spikedata = None
        self.intracons = ConSet()
        self.burstcons = ConSet()


class BurstBox(ToolBox):
    def __init__(self, mainwin, tag, title, pos, size):
        ToolBox.__init__(self, mainwin, tag, title, pos, size)

        self.mainwin = mainwin

        self.selfstore = True
        self.toolpath = mainwin.toolpath

        # default burst scan parameters
        maxint = 1500;
        minspikes = 25;
        maxspikes = 0;
        startspike = 0;
        endspike = 0;

        # panel controls and layout sizers
        self.numwidth = 50
        parambox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        rightbox = wx.BoxSizer(wx.VERTICAL)

        # All spike data panel
        self.allspikes = self.NumPanel(self.numwidth)
        self.allfreq = self.NumPanel(self.numwidth)
        self.allisimean = self.NumPanel(self.numwidth)
        self.allisisd = self.NumPanel(self.numwidth)

        if GetSystem() == "Mac": gridwidth = 45
        else: gridwidth = 30

        datagrid = wx.FlexGridSizer(2, 3, 3)
        datagrid.Add(self.GridLabel(gridwidth, "Spikes"), 0, wx.ALIGN_CENTRE)
        datagrid.Add(self.allspikes)
        datagrid.Add(self.GridLabel(gridwidth, "Freq"), 0, wx.ALIGN_CENTRE)
        datagrid.Add(self.allfreq)
        datagrid.Add(self.GridLabel(gridwidth, "Mean"), 0, wx.ALIGN_CENTRE)
        datagrid.Add(self.allisimean)
        datagrid.Add(self.GridLabel(gridwidth, "SD"), 0, wx.ALIGN_CENTRE)
        datagrid.Add(self.allisisd)

        databox = wx.StaticBoxSizer(wx.VERTICAL, self.panel, "All Data")

        if GetSystem() == "Windows": databox.AddSpacer(5)
        databox.Add(datagrid, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 2)
        hbox2.Add(databox, 1, wx.ALIGN_CENTRE_VERTICAL)

        # Burst Scan and Analysis
        self.paramset.AddNum("maxint", "Max Interval", 1500, 0)
        self.paramset.AddNum("minspikes", "Min Spikes", 25, 0)
        self.paramset.AddNum("maxspikes", "Max Spikes", 0, 0)
        self.paramset.AddNum("startspike", "Start", 0, 0)
        self.paramset.AddNum("endspike", "End", 0, 0)

        self.ParamLayout()

        parambox.Add(self.pconbox, 0, wx.ALIGN_CENTRE_HORIZONTAL)
        parambox.AddSpacer(5)

        self.burstpanels = []
        self.datburst = self.AddBurstPanel()

        intragrid = wx.FlexGridSizer(len(self.burstpanels) + 1, 3, 3)
        for panelcon in self.datburst.intracons:
            intragrid.Add(self.GridLabel(gridwidth, panelcon.label), 0, wx.ALIGN_CENTRE)
            for burstpanel in self.burstpanels:
                intragrid.Add(burstpanel.intracons.GetCon(panelcon.tag).con, 0, wx.ALIGN_CENTRE)

        intrabox = wx.StaticBoxSizer(wx.VERTICAL, self.panel, "Intra Burst")
        if GetSystem() == "Windows": intrabox.AddSpacer(5)
        intrabox.Add(intragrid, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 2)

        burstgrid = wx.FlexGridSizer(len(self.burstpanels) + 1, 3, 5)
        if GetSystem() == "Mac": gridwidth = 80 
        else: gridwidth = 65
        for panelcon in self.datburst.burstcons:
            burstgrid.Add(self.GridLabel(gridwidth, panelcon.label), 0, wx.ALIGN_CENTRE)
            for burstpanel in self.burstpanels:
                burstgrid.Add(burstpanel.burstcons.GetCon(panelcon.tag).con, 0, wx.ALIGN_CENTRE)

        rightbox.Add(burstgrid, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5)
        hbox2.AddSpacer(20)
        hbox2.Add(intrabox, 1, wx.ALIGN_CENTRE_VERTICAL)

        if GetSystem() == "Mac":
            self.scanbutton = self.AddButton(wx.ID_ANY, "Burst Scan", 90, parambox)

        else:
            self.scanbutton = self.AddButton(wx.ID_ANY, "Burst Scan", 70, parambox)

        hbox.Add(parambox, 0, wx.ALL, 0)
        hbox.AddSpacer(10)
        hbox.Add(rightbox, 0, wx.ALL, 0)

        if GetSystem() == "Windows": self.mainbox.AddSpacer(3)

        self.mainbox.AddStretchSpacer()
        self.mainbox.Add(hbox, 1, wx.ALIGN_CENTRE_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 2)
        self.mainbox.AddStretchSpacer()
        self.mainbox.Add(hbox2, 1, wx.ALIGN_CENTRE_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 2)
        self.mainbox.AddSpacer(10)

        self.panel.SetSizer(self.mainbox)
        self.panel.Layout()

        self.scanbutton.Bind(wx.EVT_BUTTON, self.OnScan)


    def OnScan(self, event):
        print("Burst Scan")


    def BurstDataPanel(self, datpanel, numwidth=50):
        datpanel.intracons.Add("Spikes", "intraspikes", self.NumPanel(numwidth))
        datpanel.intracons.Add("Freq", "intrafreq", self.NumPanel(numwidth))
        datpanel.intracons.Add("Mean", "intraisimean", self.NumPanel(numwidth))
        datpanel.intracons.Add("SD", "intraisisd", self.NumPanel(numwidth))

        datpanel.burstcons.Add("Bursts", "numbursts", self.NumPanel(numwidth))
        datpanel.burstcons.Add("Mean Spikes", "meanspikes", self.NumPanel(numwidth))
        datpanel.burstcons.Add("Mean Length", "meanlength", self.NumPanel(numwidth))
        datpanel.burstcons.Add("Length SD", "sdlength", self.NumPanel(numwidth))
        datpanel.burstcons.Add("Mean Silence", "meansilence", self.NumPanel(numwidth))
        datpanel.burstcons.Add("Silence SD", "sdsilence", self.NumPanel(numwidth))
        datpanel.burstcons.Add("Activity Q", "actQ", self.NumPanel(numwidth))
        datpanel.burstcons.Add("Mode Time", "modetime", self.NumPanel(numwidth))
        datpanel.burstcons.Add("Mode Rate", "moderate", self.NumPanel(numwidth))
        datpanel.burstcons.Add("Mean Peak", "meanpeak", self.NumPanel(numwidth))


    def AddBurstPanel(self):
        datpanel = BurstPanel()
        self.BurstDataPanel(datpanel)
        self.burstpanels.append(datpanel)
        return datpanel  
    

    # def BurstDataGrid(self, rows, gridwidth, vgap):
    #     intragrid = wx.FlexGridSizer(len(rows), len(self.burstpanels) + 1, vgap, 3)

    #     for label, attr in rows:
    #         intragrid.Add(self.GridLabel(gridwidth, label), 0, wx.ALIGN_CENTRE)

    #     for datpanel in self.burstpanels:
    #         intragrid.Add(getattr(datpanel, attr), 0, wx.ALIGN_CENTRE)

    # return intragrid


    # def BurstDataPanel(self, datpanel):
    #     numwidth = 50
    
    #     datpanel.numbursts = self.NumPanel(50)
    #     datpanel.meanspikes = self.NumPanel(50)
    #     datpanel.meanlength = self.NumPanel(50)
    #     datpanel.meansilence = self.NumPanel(50)
    #     datpanel.sdlength = self.NumPanel(50)
    #     datpanel.sdsilence = self.NumPanel(50)
    #     datpanel.actQ = self.NumPanel(50)
    #     datpanel.modetime = self.NumPanel(50)
    #     datpanel.moderate = self.NumPanel(50)
    #     datpanel.meanpeak = self.NumPanel(50)
    
    #     datpanel.intraspikes = self.NumPanel(numwidth)
    #     datpanel.intrafreq = self.NumPanel(numwidth)
    #     datpanel.intraisimean = self.NumPanel(numwidth)
    #     datpanel.intraisisd = self.NumPanel(numwidth)   


    # def AddBurstPanel(self):
    #     datpanel = BurstPanel()
    #     self.BurstDataPanel(datpanel)
    #     self.burstpanels.append(datpanel)
    #     return datpanel         