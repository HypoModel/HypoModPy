
import wx
from hypocontrols import *


class ParamSet:
    def __init__(self):
        con = {}
        paramstore = {}
        # currlay = 0;

        # Default field widths
        self.num_labelwidth = 65
        self.num_numwidth = 40
        self.con_labelwidth = 60
        self.con_numwidth = 60
        self.text_labelwidth = 60
        self.text_textwidth = 150


    def SetMinMax(self, tag, min, max):
        self.con[tag].min = min
        self.con[tag].max = max


    def GetCon(tag):

        if(!tagstore.Check(tag)) {
            # panel->mainwin->diagbox->Write("ParamSet GetCon " + tag + " not found\n");
            return Non

        else return con[(int)ref[tag]];



class ParamBox(ToolBox):
    def __init__(self, mod, title, pos, size, tag, type = 0, storemode = 0):
        ToolBox.__init__(mod.mainwin, tag, title, pos, size, type)
        
        self.autorun = 0    # auto run model after parameter change
        self.redtag = ""    # store box overwrite warning tag
        self.histmode = 0
        self.storemode = storemode
        self.mod = mod   # parent model      
        self.boxtype = type   # 0 - basic panel, 1 - AUI panel
        self.status = None
        #defbutt = 0;
        #defstore = false;
        self.diagmode = 0   # diagnostic mode
        self.mainwin = mod.mainwin  # main window link
        self.column = 0     # column mode for parameter controls
        self.buttonwidth = 50
        # modmode = 0;

        # model->mainwin->diagbox->Write("ParamBox init\n");

        self.Init()


    def Init(self):
        modparams = {}
        modflags = {}
        conflags = {}


    def ParamLayout(self, columns = 1):                   # Currently for one or two columns, need to generalise
        colsize = 0;

        if columns == 1: colsize = self.paramset.numparams
	if(columns == 2) {
		if(!column) colsize = (paramset.numparams+1) / 2;
		else colsize = column; 
	}

	SetVBox(columns);

	for(i=0; i<colsize; i++) {
		vbox[0]->Add(paramset.con[i], 1, wxALIGN_CENTRE_HORIZONTAL|wxALIGN_CENTRE_VERTICAL|wxRIGHT|wxLEFT, 5);
		vbox[0]->AddSpacer(5);
	}
	parambox->Add(vbox[0], 0);

	if(columns == 2) {
		for(i=colsize; i<paramset.numparams; i++) {
			vbox[1]->Add(paramset.con[i], 1, wxALIGN_CENTRE_HORIZONTAL|wxALIGN_CENTRE_VERTICAL|wxRIGHT|wxLEFT, 5);
			vbox[1]->AddSpacer(5);
		}
		parambox->Add(vbox[1], 0);
	}
}
