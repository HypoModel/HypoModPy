
from hashlib import new
from math import log, pow
from xxlimited import new
from HypoModPy.hypobase import TextFile, numstring
from HypoModPy.hypotools import DiagWrite


class GraphEPS:
	def __init__(self, mainwin=None):
		self.mainwin = mainwin

	def WriteEPS(self):
		pass


class GraphEPS:

	def EPSColour(self, colour):
		if hasattr(colour, "Red"):
			r = colour.Red() / 255
			g = colour.Green() / 255
			b = colour.Blue() / 255
			return f"{r:.4f} {g:.4f} {b:.4f}"
		if type(colour) is str:
			if colour in self.colourpen:
				c = self.colourpen[colour]
				return f"{c.Red() / 255:.4f} {c.Green() / 255:.4f} {c.Blue() / 255:.4f}"
		return "0 0 0"


	def EPSNum(self, x, places=-1):
		if places != -1: return numstring(x, places)
		ax = abs(x)
		if ax < 0.1: return f"{x:.3f}"
		if ax < 1: return f"{x:.2f}"
		if ax < 10: return f"{x:.1f}"
		return f"{x:.0f}"


	def EPSHeader(self, out):
		out.WriteLine("%!PS-Adobe-3.0 EPSF-3.0")
		out.WriteLine("%%BoundingBox: 0 0 1000 500")
		out.WriteLine("/pu {1 mul} def")	# pu = plot units, set scaling to points
		out.WriteLine("0 0 0 setrgbcolor")
		out.WriteLine("1 setlinecap")
		out.WriteLine("1 setlinejoin")
		out.WriteLine("")


	def WriteEPS(self, xb=-1, yb=-1, ofp=None):

		mod = self.mod
		mainwin = self.mainwin

		DiagWrite(f"Graph EPS {self.index}\n")

		if xb < 0: xbase = 100
		else: xbase = xb
		if yb < 0: ybase = 100
		else: ybase = yb

		xplot = 500  #self.xplot
		yplot = 200  #self.yplot
		xstretch = self.xstretch
		axisstroke = 0.75
		yoffset = 0

		frontplot = self.dispset[0].plots[0]
		filepath = mainwin.outpath
		filetag = mod.modbox.storetag.GetValue()
		filename = filepath + "/" + filetag + "-" + frontplot.label + ".eps"

		if ofp is None:
			out = TextFile()
			out.Open(filename, 'w')
			self.EPSHeader(out)
		else: out = ofp

		xlogbase = 2.71828182845904523536028747135266250
		ylogbase = 2.71828182845904523536028747135266250


		for graphdisp in self.dispset:
			for plot in graphdisp.plots:

				# Get Plot parameters
				xfrom = plot.xfrom * plot.xscale
				xto = plot.xto * plot.xscale
				yfrom = plot.yfrom * plot.yscale
				yto = plot.yto * plot.yscale

				xplot = plot.xplot
				yplot = plot.yplot
				xlabels = plot.xlabels
				ylabels = plot.ylabels
				xscale = plot.xscale
				yscale = plot.yscale
				xdis = plot.xdis
				xsample = plot.xsample

				if plot.xscalemode == 1 and xfrom > 0: xlogmax = log(xto / xfrom) / log(xlogbase)
				else: xlogmax = 0
				if plot.yscalemode == 1 and yfrom > 0: ylogmax = log(yto / yfrom) / log(ylogbase)
				else: ylogmax = 0

				out.WriteLine(f"{self.EPSColour(plot.strokecolour)} setrgbcolor")

				# Set drawing scales
				xtoAxis = xto
				xfromAxis = xfrom
				xto = xto / plot.binsize
				xfrom = xfrom / plot.binsize

				yrange = yplot / (yto - yfrom)
				xrange = xplot / (xto - xfrom)
				xnum = (xto - xfrom) / xplot

				xticklength = 5;
				yticklength = 5;
				# Auto tick length 
				if xplot < 200: yticklength = 3
				if yplot < 100: xticklength = 3

				out.WriteLine("gsave")

				if plot.clipmode:
					out.WriteLine("newpath")
					out.MoveTo(xbase, ybase)
					out.LineTo(xbase, ybase + yplot)
					out.LineTo(xbase + xplot, ybase + yplot)
					out.LineTo(xbase + xplot, ybase)
					out.WriteLine("closepath")
					out.WriteLine("clip")

				# Draw graph data
				out.WriteLine(f"{plot.plotstroke:.2f} setlinewidth")

				if hasattr(plot.data, "empty") and plot.data.empty:
					out.WriteLine("grestore")
					continue

				if plot.type == "line":
					xoffset = 0;
					out.WriteLine("newpath")
					out.WriteLine(f"{self.EPSColour(plot.strokecolour)} setrgbcolor")

					yval = plot.data[int(plot.xfrom)]
					oldx = xbase
					oldy = ybase + yrange * (yval - yfrom)      # TODO proper start coordinates

					for i in range(1, int((xto - xfrom) / xsample)):
						xindex = int(i * xsample + xfrom)
						if xindex >= len(plot.data): break

						xpos = (xindex - xfrom) * xrange
						yval = plot.data[xindex]

						if plot.yscalemode == 1 and yfrom > 0:
							ypos = (int)(yplot * (log(yval / yfrom) / log(ylogbase)) / ylogmax)  # log scaled y-axis  March 2018
							if yval < yfrom: ypos = -yfrom * yrange     # set below range values to xfrom
						else: ypos = yrange * (yval - yfrom)

						out.DrawLine(oldx, oldy, xpos + xbase + xoffset, ybase + ypos)
						oldx = xpos + xbase + xoffset
						oldy = ybase + ypos

					out.WriteLine("stroke")

				out.WriteLine("grestore")

		




		DiagWrite(f"Font index {plot.labelfont} name {mainwin.fontset.GetName(plot.labelfont)}\n")

		out.WriteLine(f"/{mainwin.fontset.GetName(plot.labelfont)} findfont {plot.labelfontsize:.2f} scalefont setfont")


		xto = xtoAxis
		xfrom = xfromAxis
		ybase = ybase - yoffset
		xaxislength = xplot

		#if(graph->axistrace && graph->drawX != -1) xaxislength = graph->drawX * binsize / (xto - xfrom) * xplot;

		out.WriteLine(f"{self.EPSColour(self.colourpen['black'])} setrgbcolor")
		out.WriteLine(f"{axisstroke:.2f} setlinewidth")
		out.WriteLine("newpath")
		if plot.yaxis: out.DrawLine(xbase, ybase, xbase, ybase + yplot)
		if plot.xaxis: out.DrawLine(xbase, ybase, xbase + xaxislength + xstretch, ybase)
		out.WriteLine("")
		out.WriteLine("")

		# Draw Ticks

		# new tickmode 0 = off, 1 = count, 2 = step

		# Coding Note: ticks and labels in separate loops, unlike hypograph.cpp

		xplotstep = 0
		yplotstep = 0
		xtickstart = 0
		xtickshift = 0
		if xfrom != 0: xtickshift = xfrom

		if plot.xtickmode == 2:
			xlabels = int((xto - xfrom) / (plot.xscale * plot.xstep))
			xplotstep = (xplot * plot.xstep) / (xto - xfrom)
			xtickstart = abs(xtickshift) * xplotstep

		if plot.ytickmode == 2 and plot.ystep > 0:
			ylabels = int((yto - yfrom) / (yscale * plot.ystep))
			yplotstep = (yplot * plot.ystep) / (yto - yfrom)

		if plot.ytickmode == 2 and plot.yscalemode == 1:
			ylogrange = log(yto - yfrom) / log(ylogbase)
			ylabels = int(ylogrange / plot.ystep)
			yplotstep = (yplot * plot.ystep) / ylogrange

		for i in range(0, xlabels + 1):
			if plot.xtickmode == 2: xcoord = xplotstep * i + xtickstart
			else: xcoord = i * xplot / xlabels if xlabels else 0
			if plot.xtickmode and xcoord <= xaxislength: out.DrawLine(xbase + xcoord, ybase, xbase + xcoord, ybase - plot.xticklength)

		for i in range(0, ylabels + 1):
			ycoord = i * yplot / ylabels if ylabels else 0
			if plot.ytickmode == 2: ycoord = yplotstep * i
			if plot.ytickmode: out.DrawLine(xbase, ybase + ycoord, xbase - plot.yticklength, ybase + ycoord)

		out.WriteLine("stroke")

		# Draw Tick Labels
		for i in range(0, xlabels + 1):
			if plot.xlabelmode == 0: break

			if plot.xtickmode == 2: xcoord = xplotstep * i + xtickstart
			else: xcoord = i * xplot / xlabels if xlabels else 0

			if not plot.xlabelmode or xcoord > xaxislength or plot.xlabelmode == 2 and i > 0 and i < xlabels: continue

			if plot.xtickmode == 2: xval = (xfrom + plot.xstep * i) * plot.xunitscale / plot.xunitdscale - plot.xshift - xtickshift
			else: xval = ((xto - xfrom) / xlabels * i + xfrom) / plot.xscale * plot.xunitscale / plot.xunitdscale - plot.xshift if xlabels else xfrom

			if plot.xscalemode == 1 and xfrom > 0: xval = xfrom * pow(xlogbase, xlogmax * xval / xto)

			srangex = abs((xto - xfrom) / plot.xscale * plot.xunitscale / plot.xunitdscale)
			if plot.xlabelplaces == -1:
				if srangex < 0.1: snum = f"{xval + xdis:.3f}"
				elif srangex < 1: snum = f"{xval + xdis:.2f}"
				elif srangex < 10: snum = f"{xval + xdis:.1f}"
				else: snum = f"{xval + xdis:.0f}"
			else: snum = numstring(xval + xdis, plot.xlabelplaces)

			out.WriteLine("newpath")
			out.MoveTo(xbase + xcoord, ybase - 15)
			out.WriteLine(f"({snum}) dup stringwidth pop 2 div neg 0 rmoveto show")
			out.WriteLine("stroke")

		xylab = 8

		for i in range(0, ylabels + 1):
			if plot.ylabelmode == 0: break
			if plot.ylabelmode == 2 and i > 0 and i < ylabels: continue

			ycoord = i * yplot / ylabels if ylabels else 0
			if plot.ytickmode == 2: ycoord = yplotstep * i

			if plot.ytickmode == 1: yval = (((yto - yfrom) / ylabels * i + yfrom) / yscale) * plot.yunitscale / plot.yunitdscale - plot.yshift if ylabels else yfrom
			elif plot.ytickmode == 2: yval = (yfrom + plot.ystep * i) * plot.yunitscale / plot.yunitdscale - plot.yshift
			else: yval = (((yto - yfrom) / ylabels * i + yfrom) / yscale) * plot.yunitscale / plot.yunitdscale - plot.yshift if ylabels else yfrom

			if plot.yscalemode == 1 and yfrom > 0:
				if plot.ytickmode == 1: yval = pow(ylogbase, plot.ystep * i)
				if plot.ytickmode == 0: yval = yfrom * pow(ylogbase, ylogmax * yval / yto)

			srangey = abs((yto - yfrom) / yscale * plot.yunitscale / plot.yunitdscale)
			if plot.ylabelplaces == -1:
				if srangey < 0.1: snum = f"{yval:.3f}"
				elif srangey < 1: snum = f"{yval:.2f}"
				elif srangey < 10: snum = f"{yval:.1f}"
				else: snum = f"{yval:.0f}"
			else: snum = numstring(yval, plot.ylabelplaces)

			out.MoveTo(xbase - xylab - plot.yticklength, ybase + ycoord - 2.75)
			out.WriteLine(f"({snum}) dup stringwidth pop neg 0 rmoveto show")


		# Draw Axis Labels

		if plot.xtitle != "":
			out.MoveTo(xbase + xplot / 2, ybase - plot.xlabelgap)
			out.WriteLine(f"({plot.xtitle}) dup stringwidth pop 2 div neg 0 rmoveto show")

		if plot.ytitle != "":
			out.MoveTo(xbase - plot.ylabelgap, ybase + yplot / 2)
			out.WriteLine("90 rotate")
			out.WriteLine(f"({plot.ytitle}) dup stringwidth pop 2 div neg 0 rmoveto show")
			out.WriteLine("270 rotate")

		if plot.gtitle and plot.label != "":
			out.MoveTo(xbase + xplot, ybase + yplot - 30)
			out.WriteLine(f"({plot.label}) dup stringwidth pop neg 0 rmoveto show")

		DiagWrite("EPS Written OK\n")

		if ofp is None: out.Close()



	def MultiCell(self):

		mod = self.mod
		mainwin = self.mainwin

		ypos = 800
		xpos = 100

		mod.diagbox.Write("MultiCell\n")

		textgrid = mod.gridbox.currgrid

		cellcount = int(textgrid.ReadDouble(0, 1))
		if not cellcount:
			mod.diagbox.Write("ERROR parameters zero cellcount\n")
			return

		cellstart = int(textgrid.ReadDouble(1, 1))
		if cellstart < 0: cellstart = 0

		numcols = int(textgrid.ReadDouble(2, 1))
		if numcols <= 0: numcols = 1

		xgap = textgrid.ReadDouble(3, 1)
		if xgap <= 0: xgap = 100

		ygap = textgrid.ReadDouble(4, 1)
		if ygap <= 0: ygap = 100

		ypos = textgrid.ReadDouble(5, 1)
		if ypos < 0: ypos = 100

		mod.diagbox.Write("MultiCell parameters read\n")

		filepath = mainwin.outpath
		filetag = mod.modbox.paramstoretag.GetValue()
		filename = filepath + "/" + filetag + "-" + "multicell" + ".eps"

		out = TextFile()
		out.New(filename)
		self.EPSHeader(out)

		col = 0
		row = 0

		oldindex = mod.GetCellIndex()
		plot = self.dispset[0].plots[0]

		for i in range(cellcount):
			mod.SetCell(i + cellstart, plot)
			self.PrintEPS(xpos + xgap * col, ypos - ygap * row, out)
			col += 1
			if col == numcols:
				col = 0
				row += 1

		mod.SetCell(oldindex, plot)
		out.Close()


	def MultiEPS(self):

		mod = self.mod
		mainwin = self.mainwin

		textgrid = mod.gridbox.layoutgrid

		panelcount = int(textgrid.ReadDouble(0, 0))
		if not panelcount:
			mod.diagbox.Write("MultiEPS no panel count found\n")
			return

		panelcomm = [""] * panelcount
		paneldex = [0] * panelcount
		xb = [0] * panelcount
		yb = [0] * panelcount

		for i in range(panelcount):
			celltext = textgrid.GetCell(i + 1, 0).strip()
			try:
				celldata = float(celltext)
				paneldex[i] = int(celldata)
				xb[i] = textgrid.ReadDouble(i + 1, 1)
				yb[i] = textgrid.ReadDouble(i + 1, 2)
				panelcomm[i] = ""
			except:
				panelcomm[i] = celltext

		filepath = mainwin.outpath
		filetag = mod.modbox.paramstoretag.GetValue()
		filename = filepath + "/" + filetag + "-" + "multi" + ".eps"

		out = TextFile()
		out.New(filename)
		self.EPSHeader(out)

		for i in range(panelcount):
			if panelcomm[i] == "":
				gwin = mainwin.graphwin[paneldex[i]]
				gwin.PrintEPS(xb[i], yb[i], out)
			if panelcomm[i] == "hh": mainwin.scalebox.GraphCommand(ID_histhaz1)
			if panelcomm[i] == "norm": mainwin.scalebox.GraphCommand(ID_norm)
			if panelcomm[i] == "net": mainwin.scalebox.GraphCommand(ID_net)

		out.Close()


	def PrintEPS(self, xb=-1, yb=-1, ofp=None):

		mod = self.mod
		mainwin = self.mainwin

		if mod.diagbox: mod.diagbox.textbox.AppendText(f"Graph EPS {self.graphindex}\n")

		if xb < 0: xbase = 100
		else: xbase = xb
		if yb < 0: ybase = 100
		else: ybase = yb

		xplot = self.xplot
		yplot = self.yplot
		xstretch = self.xstretch
		axisstroke = 0.75
		yoffset = 0

		frontplot = self.dispset[0].plots[0]
		filepath = mainwin.outpath
		filetag = mod.modbox.paramstoretag.GetValue()
		filename = filepath + "/" + filetag + "-" + frontplot.label + ".eps"

		if ofp is None:
			out = TextFile()
			out.New(filename)
			self.EPSHeader(out)
		else: out = ofp

		xlogbase = 2.71828182845904523536028747135266250
		ylogbase = 2.71828182845904523536028747135266250

		lastplot = None
		lastxfrom = 0
		lastxto = 0
		lastyfrom = 0
		lastyto = 0
		lastxplot = xplot
		lastyplot = yplot
		lastxlabels = 10
		lastylabels = 5
		lastxscale = 1
		lastyscale = 1
		lastxdis = 0
		lastxlogmax = 0
		lastylogmax = 0

		for graphdisp in self.dispset:
			for plot in graphdisp.plots:

				xfrom = plot.xfrom * plot.xscale
				xto = plot.xto * plot.xscale
				yfrom = plot.yfrom * plot.yscale
				yto = plot.yto * plot.yscale

				xplot = plot.xplot
				yplot = plot.yplot
				xlabels = plot.xlabels
				ylabels = plot.ylabels
				xscale = plot.xscale
				yscale = plot.yscale
				xdis = plot.xdis

				if plot.xscalemode == 1 and xfrom > 0: xlogmax = log(xto / xfrom) / log(xlogbase)
				else: xlogmax = 0
				if plot.yscalemode == 1 and yfrom > 0: ylogmax = log(yto / yfrom) / log(ylogbase)
				else: ylogmax = 0

				out.WriteLine(f"{self.EPSColour(plot.strokecolour)} setrgbcolor")

				xtoAxis = xto
				xfromAxis = xfrom
				xto = xto / plot.binsize
				xfrom = xfrom / plot.binsize

				yrange = yplot / (yto - yfrom)
				xrange = xplot / (xto - xfrom)
				xnum = (xto - xfrom) / xplot

				out.WriteLine("gsave")

				if plot.clipmode:
					out.WriteLine("newpath")
					out.MoveTo(xbase, ybase)
					out.LineTo(xbase, ybase + yplot)
					out.LineTo(xbase + xplot, ybase + yplot)
					out.LineTo(xbase + xplot, ybase)
					out.WriteLine("closepath")
					out.WriteLine("clip")

				out.WriteLine(f"{plot.plotstroke:.2f} setlinewidth")

				if hasattr(plot.data, "empty") and plot.data.empty:
					out.WriteLine("grestore")
					continue

				if plot.type == "line":
					xoffset = 1
					dir = 1
					pdir = 0

					xindex = int(plot.xfrom)
					maxdex = plot.data.size - 1
					if xindex > maxdex:
						out.WriteLine("grestore")
						continue

					preval = plot.data[xindex]
					oldx = xbase + xoffset
					oldy = yplot + ybase - yrange * (preval - yfrom)

					out.WriteLine("newpath")
					out.MoveTo(oldx, oldy)

					if xrange < 1: xcount = int(xplot)
					else:
						xcount = int(xplot / xrange)
						if xcount < 1: xcount = 1

					for i in range(xcount):

						if xrange < 1:
							xindex = int((i * xnum) + xfrom)
							if maxdex and maxdex < xindex: break
							mpoint = plot.data[xindex]

							if mpoint > preval: dir = 1
							if mpoint < preval: dir = -1

							if pdir == 0: pdir = dir
							if dir != pdir:
								xpos = i
								ypos = yplot + ybase - yrange * (preval - yfrom)
								out.LineTo(xpos + xbase + xoffset, ypos)
								pdir = dir

							preval = mpoint
							xpos = i
							ypos = yplot + ybase - yrange * (mpoint - yfrom)
							oldx = xpos + xbase + xoffset
							oldy = ypos

						else:
							xindex = int(i + xfrom)
							if maxdex and maxdex < xindex: break
							mpoint = plot.data[xindex]
							xpos = i * xrange
							ypos = yplot + ybase - yrange * (mpoint - yfrom)
							out.LineTo(xpos + xbase + xoffset, ypos)
							oldx = xpos + xbase + xoffset
							oldy = ypos

					if xrange < 1: out.LineTo(oldx, oldy)
					out.WriteLine("stroke")

				out.WriteLine("grestore")

				lastplot = plot
				lastxfrom = xfromAxis
				lastxto = xtoAxis
				lastyfrom = yfrom
				lastyto = yto
				lastxplot = xplot
				lastyplot = yplot
				lastxlabels = xlabels
				lastylabels = ylabels
				lastxscale = xscale
				lastyscale = yscale
				lastxdis = xdis
				lastxlogmax = xlogmax
				lastylogmax = ylogmax

		if lastplot is None:
			if ofp is None: out.Close()
			return

		plot = lastplot
		xfrom = lastxfrom
		xto = lastxto
		yfrom = lastyfrom
		yto = lastyto
		xplot = lastxplot
		yplot = lastyplot
		xlabels = lastxlabels
		ylabels = lastylabels
		xscale = lastxscale
		yscale = lastyscale
		xdis = lastxdis
		xlogmax = lastxlogmax
		ylogmax = lastylogmax

		if mod.diagbox: mod.diagbox.Write(f"Font index {plot.labelfont} name {mainwin.fontset.GetName(plot.labelfont)}\n")

		out.WriteLine(f"/{mainwin.fontset.GetName(plot.labelfont)} findfont {plot.labelfontsize:.2f} scalefont setfont")

		ybase = ybase - yoffset
		xaxislength = xplot

		out.WriteLine(f"{self.EPSColour(self.colourpen['black'])} setrgbcolor")
		out.WriteLine(f"{axisstroke:.2f} setlinewidth")
		out.WriteLine("newpath")
		if plot.yaxis: out.DrawLine(xbase, ybase, xbase, ybase + yplot)
		if plot.xaxis: out.DrawLine(xbase, ybase + yplot, xbase + xaxislength + xstretch, ybase + yplot)
		out.WriteLine("")
		out.WriteLine("")

		xplotstep = 0
		yplotstep = 0
		xtickstart = 0
		xtickshift = 0
		if xfrom != 0: xtickshift = xfrom

		if plot.xtickmode == 2:
			xlabels = int((xto - xfrom) / (plot.xscale * plot.xstep))
			xplotstep = (xplot * plot.xstep) / (xto - xfrom)
			xtickstart = abs(xtickshift) * xplotstep

		if plot.ytickmode == 2 and plot.ystep > 0:
			ylabels = int((yto - yfrom) / (yscale * plot.ystep))
			yplotstep = (yplot * plot.ystep) / (yto - yfrom)

		if plot.ytickmode == 2 and plot.yscalemode == 1:
			ylogrange = log(yto - yfrom) / log(ylogbase)
			ylabels = int(ylogrange / plot.ystep)
			yplotstep = (yplot * plot.ystep) / ylogrange

		for i in range(0, xlabels + 1):
			if plot.xtickmode == 2: xcoord = xplotstep * i + xtickstart
			else: xcoord = i * xplot / xlabels if xlabels else 0
			if plot.xtickmode and xcoord <= xaxislength: out.DrawLine(xbase + xcoord, ybase + yplot, xbase + xcoord, ybase + yplot + plot.xticklength)

		for i in range(0, ylabels + 1):
			ycoord = i * yplot / ylabels if ylabels else 0
			if plot.ytickmode == 2: ycoord = yplotstep * i
			if plot.ytickmode: out.DrawLine(xbase, ybase + yplot - ycoord, xbase - plot.yticklength, ybase + yplot - ycoord)

		out.WriteLine("stroke")

		for i in range(0, xlabels + 1):
			if plot.xlabelmode == 0: break

			if plot.xtickmode == 2: xcoord = xplotstep * i + xtickstart
			else: xcoord = i * xplot / xlabels if xlabels else 0

			if not plot.xlabelmode or xcoord > xaxislength or plot.xlabelmode == 2 and i > 0 and i < xlabels: continue

			if plot.xtickmode == 2: xval = (xfrom + plot.xstep * i) * plot.xunitscale / plot.xunitdscale - plot.xshift - xtickshift
			else: xval = ((xto - xfrom) / xlabels * i + xfrom) / plot.xscale * plot.xunitscale / plot.xunitdscale - plot.xshift if xlabels else xfrom

			if plot.xscalemode == 1 and xfrom > 0: xval = xfrom * pow(xlogbase, xlogmax * xval / xto)

			srangex = abs((xto - xfrom) / plot.xscale * plot.xunitscale / plot.xunitdscale)
			if plot.xlabelplaces == -1:
				if srangex < 0.1: snum = f"{xval + xdis:.3f}"
				elif srangex < 1: snum = f"{xval + xdis:.2f}"
				elif srangex < 10: snum = f"{xval + xdis:.1f}"
				else: snum = f"{xval + xdis:.0f}"
			else: snum = numstring(xval + xdis, plot.xlabelplaces)

			out.WriteLine("newpath")
			out.MoveTo(xbase + xcoord, ybase + yplot + 15)
			out.WriteLine(f"({snum}) dup stringwidth pop 2 div neg 0 rmoveto show")
			out.WriteLine("stroke")

		xylab = 8

		for i in range(0, ylabels + 1):
			if plot.ylabelmode == 0: break
			if plot.ylabelmode == 2 and i > 0 and i < ylabels: continue

			ycoord = i * yplot / ylabels if ylabels else 0
			if plot.ytickmode == 2: ycoord = yplotstep * i

			if plot.ytickmode == 1: yval = (((yto - yfrom) / ylabels * i + yfrom) / yscale) * plot.yunitscale / plot.yunitdscale - plot.yshift if ylabels else yfrom
			elif plot.ytickmode == 2: yval = (yfrom + plot.ystep * i) * plot.yunitscale / plot.yunitdscale - plot.yshift
			else: yval = (((yto - yfrom) / ylabels * i + yfrom) / yscale) * plot.yunitscale / plot.yunitdscale - plot.yshift if ylabels else yfrom

			if plot.yscalemode == 1 and yfrom > 0:
				if plot.ytickmode == 1: yval = pow(ylogbase, plot.ystep * i)
				if plot.ytickmode == 0: yval = yfrom * pow(ylogbase, ylogmax * yval / yto)

			srangey = abs((yto - yfrom) / yscale * plot.yunitscale / plot.yunitdscale)
			if plot.ylabelplaces == -1:
				if srangey < 0.1: snum = f"{yval:.3f}"
				elif srangey < 1: snum = f"{yval:.2f}"
				elif srangey < 10: snum = f"{yval:.1f}"
				else: snum = f"{yval:.0f}"
			else: snum = numstring(yval, plot.ylabelplaces)

			out.MoveTo(xbase - xylab - plot.yticklength, ybase + yplot - ycoord - 2.75)
			out.WriteLine(f"({snum}) dup stringwidth pop neg 0 rmoveto show")

		if plot.xtitle != "":
			out.MoveTo(xbase + xplot / 2, ybase + yplot + plot.xlabelgap)
			out.WriteLine(f"({plot.xtitle}) dup stringwidth pop 2 div neg 0 rmoveto show")

		if plot.ytitle != "":
			out.MoveTo(xbase - plot.ylabelgap, ybase + yplot / 2)
			out.WriteLine("90 rotate")
			out.WriteLine(f"({plot.ytitle}) dup stringwidth pop 2 div neg 0 rmoveto show")
			out.WriteLine("270 rotate")

		if plot.label != "":
			out.MoveTo(xbase + xplot, ybase - 30)
			out.WriteLine(f"({plot.label}) dup stringwidth pop neg 0 rmoveto show")

		if mod.diagbox: mod.diagbox.textbox.AppendText("EPS Written OK\n")

		if ofp is None: out.Close()
