
import wx
from hypoparams import *


class Model(wx.EvtHandler):
    def __init__(self, mainwin, tag):
        self.mainwin = mainwin
        self.tag = tag
        self.type = type

        self.modtools = {}


    def GetPath(self):
        if modpath == "": 
            if self.path != "": fullpath = self.path
            else: fullpath = self.mainwin.initpath
        else:
            if self.path != "": fullpath = modpath + "/" + self.path
            else: fullpath = modpath

        if os.path.exists(fullpath) == False: 
            os.mkdir(fullpath)

        return fullpath


    def ModStore(self):
        filepath = self.GetPath()
        
        # box store
        filename = self.tag + "-box.ini"
        outfile = TextFile(filepath + "/" + filename)
        outfile.Open('w')

        for box in self.toolset.boxset.values():
            outfile.WriteLine("{} {} {} {} {} {}".format(box.boxtag, box.mpos.x, box.mpos.y, box.boxsize.x, box.boxsize.y, box.IsShown()))

        outfile.Close()

        print("ModStore OK")

 
    def ModLoad(self):
        filepath = self.GetPath()

        # box load
        infile = TextFile(filepath)
        check = infile.Open('r')
        if check == False: return
        filetext = infile.ReadLines()

        for line in filetext:
            linedata = line.split(' ')
            boxtag = linedata[0]
            if boxtag in self.toolset.boxset:      
                pos = wx.Point(int(linedata[1]), int(linedata[2]))
                size = wx.Size(int(linedata[3]), int(linedata[4]))
                if linedata[5] == 'True\n': visible = True
                else: visible = False
                self.toolset.boxset[boxtag].visible = visible
                self.toolset.boxset[boxtag].mpos = pos
                self.toolset.boxset[boxtag].boxsize = size

        infile.Close()

        for box in self.toolset.boxset.values():
            box.SetSize(box.boxsize)
            box.SetPosition(self.GetPosition(), self.GetSize())
            box.Show(box.visible)


	

