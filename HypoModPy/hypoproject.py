## hypoproject.py
##
## Duncan MacGregor
## started 20/3/26
##
## chatGPT colab


import os
import wx

from HypoModPy.hypotools import TextFile


class Project:
    def __init__(self, mainwin, tag="", basepath=""):
        self.mainwin = mainwin
        self.tag = tag
        self.basepath = basepath
        self.path = ""

        self.components = {}
        self.mainmod = None

        self.boxfile = ""
        self.prefsfile = ""
        self.tagfile = ""


    def Init(self, tag, mod=None):
        if mod is not None:
            self.mainmod = mod

        self.tag = tag

        if self.mainmod:
            self.path = os.path.join(self.mainmod.path, "Projects", self.tag)
        else:
            self.path = os.path.join(self.basepath, self.tag)

        self.boxfile = os.path.join(self.path, "boxes.ini")
        self.prefsfile = os.path.join(self.path, "prefs.ini")
        self.tagfile = os.path.join(self.path, "tags.ini")

        os.makedirs(self.path, exist_ok=True)


    def SetMainMod(self, mod):
        self.mainmod = mod
        self.AddComponent("mod", mod)


    def AddComponent(self, name, component):
        self.components[name] = component
        component.project = self


    def GetComponent(self, name):
        return self.components.get(name)


    def MakeTag(self, localtag):
        return self.tag + "-" + localtag


    def Store(self):
        if self.mainmod is None:
            return

        os.makedirs(self.path, exist_ok=True)

        self.StorePrefs()
        self.StoreBoxes()
        self.StoreTags()

        if hasattr(self.mainwin, "scalebox") and self.mainwin.scalebox:
            self.mainwin.scalebox.GStore()


    def Load(self):
        if self.mainmod is None:
            return

        self.LoadPrefs()
        self.LoadBoxes()
        self.LoadTags()

        if hasattr(self.mainwin, "scalebox") and self.mainwin.scalebox:
            self.mainwin.scalebox.GLoad()


    def StorePrefs(self):
        outfile = TextFile()
        outfile.New(self.prefsfile)

        self.mainmod.prefs["viewwidth"] = self.mainwin.GetSize().GetWidth()
        self.mainmod.prefs["viewheight"] = self.mainwin.GetSize().GetHeight()
        self.mainmod.prefs["numdraw"] = self.mainwin.numdraw

        for tag in self.mainmod.prefs:
            outfile.WriteLine("%s %s" % (tag, self.mainmod.prefs[tag]))

        outfile.Close()


    def LoadPrefs(self):
        infile = TextFile()
        check = infile.Open(self.prefsfile)
        if not check:
            return

        readline = infile.ReadLine()
        while readline != "":
            tag = readline.split(" ", 1)[0]
            valtext = readline.split(" ", 1)[1].strip()

            try:
                numval = int(float(valtext))
            except:
                try:
                    numval = float(valtext)
                except:
                    numval = valtext

            self.mainmod.prefs[tag] = numval
            readline = infile.ReadLine()

        infile.Close()

        if "viewwidth" in self.mainmod.prefs and "viewheight" in self.mainmod.prefs:
            self.mainwin.SetSize(int(self.mainmod.prefs["viewwidth"]), int(self.mainmod.prefs["viewheight"]))

        if "numdraw" in self.mainmod.prefs:
            self.mainwin.numdraw = int(self.mainmod.prefs["numdraw"])


    def StoreBoxes(self):
        outfile = TextFile()
        outfile.New(self.boxfile)

        for boxtag in self.mainwin.toolset.boxset:
            box = self.mainwin.toolset.boxset[boxtag]
            if not box:
                continue

            visible = 0
            if hasattr(box, "visible"):
                visible = int(bool(box.visible))
            elif hasattr(box, "IsShown"):
                visible = int(bool(box.IsShown()))

            pos = box.GetPosition()
            size = box.GetSize()

            outfile.WriteLine("%s %d %d %d %d %d" % (
                boxtag,
                pos.x, pos.y,
                size.GetWidth(), size.GetHeight(),
                visible
            ))

        outfile.Close()


    def LoadBoxes(self):
        infile = TextFile()
        check = infile.Open(self.boxfile)
        if not check:
            return

        readline = infile.ReadLine()
        while readline != "":
            parts = readline.split()
            if len(parts) >= 6:
                boxtag = parts[0]
                x = int(parts[1])
                y = int(parts[2])
                w = int(parts[3])
                h = int(parts[4])
                visible = bool(int(parts[5]))

                if boxtag in self.mainwin.toolset.boxset:
                    box = self.mainwin.toolset.boxset[boxtag]

                    if x >= -5000 and x < 5000 and y >= -5000 and y < 5000:
                        box.mpos = wx.Point(x, y)
                    if w >= 50 and w < 2000 and h >= 50 and h < 2000:
                        box.boxsize = wx.Size(w, h)

                    if hasattr(box, "servant") and box.servant:
                        box.visible = visible
                    else:
                        box.visible = True

            readline = infile.ReadLine()

        infile.Close()

        for boxtag in self.mainwin.toolset.boxset:
            box = self.mainwin.toolset.boxset[boxtag]
            if hasattr(box, "ReSize"):
                box.ReSize()
            if hasattr(box, "Show"):
                box.Show(box.visible)
            if hasattr(box, "SetPosition"):
                try:
                    box.SetPosition()
                except TypeError:
                    pass


    def StoreTags(self):
        outfile = TextFile()
        outfile.New(self.tagfile)

        for boxtag in self.mainwin.toolset.boxset:
            box = self.mainwin.toolset.boxset[boxtag]
            if hasattr(box, "storetag") and box.storetag:
                tag = box.storetag.tag
                filename = box.storetag.tagfilename
                outfile.WriteLine("%s %s" % (tag, filename))

        outfile.Close()


    def LoadTags(self):
        infile = TextFile()
        check = infile.Open(self.tagfile)
        if not check:
            return

        tagmap = {}
        for boxtag in self.mainwin.toolset.boxset:
            box = self.mainwin.toolset.boxset[boxtag]
            if hasattr(box, "storetag") and box.storetag:
                tagmap[box.storetag.tag] = box.storetag

        readline = infile.ReadLine()
        while readline != "":
            if " " in readline:
                tag = readline.split(" ", 1)[0]
                filename = readline.split(" ", 1)[1].strip()

                if tag in tagmap:
                    tagmap[tag].SetFile(filename)

            readline = infile.ReadLine()

        infile.Close()