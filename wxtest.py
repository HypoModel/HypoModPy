

import wx


app = wx.App()
window = wx.Frame(None)
window.Title = "character list"
pnl = wx.Panel(window)
window.Show()
window.Raise()
app.MainLoop()