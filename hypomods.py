
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

        print("path " + self.path)
        print("fullpath " + fullpath)

        if os.path.exists(fullpath) == False: 
            os.mkdir(fullpath)

        return fullpath


    def ModStore(self):
        #filepath = self.GetPath()
        filepath = self.path
        
        # box store
        filename = self.tag + "-box.ini"
        outfile = TextFile(filepath + "/" + filename)
        outfile.Open('w')

        for box in self.modtools.values():
            outfile.WriteLine("{} {} {} {} {} {}".format(box.boxtag, box.mpos.x, box.mpos.y, box.boxsize.x, box.boxsize.y, box.IsShown()))

        outfile.Close()

        print("ModStore OK")

 
    def ModLoad(self):
        #filepath = self.GetPath()
        filepath = self.path

        # box load
        filename = self.tag + "-box.ini"
        infile = TextFile(filepath + "/" + filename)
        check = infile.Open('r')
        if check == False: 
            print("ModLoad box file not found")
            return
        filetext = infile.ReadLines()

        for line in filetext:
            linedata = line.split(' ')
            boxtag = linedata[0]
            if boxtag in self.modtools.keys():      
                pos = wx.Point(int(linedata[1]), int(linedata[2]))
                size = wx.Size(int(linedata[3]), int(linedata[4]))
                if linedata[5] == 'True\n': visible = True
                else: visible = False
                self.modtools[boxtag].visible = visible
                self.modtools[boxtag].mpos = pos
                self.modtools[boxtag].boxsize = size

        infile.Close()

        for box in self.modtools.values():
            box.SetSize(box.boxsize)
            box.SetPosition(self.mainwin.GetPosition(), self.mainwin.GetSize())
            box.Show(box.visible)

        print("ModLoad OK")


	

