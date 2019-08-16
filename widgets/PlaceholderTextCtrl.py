# -*- coding: utf-8 -*-
import wx


class PlaceholderTextCtrl(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        self.default_text = kwargs.pop("placeholder", "")
        wx.TextCtrl.__init__(self, *args, **kwargs)
        self.OnKillFocus(None)
        self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

    def OnFocus(self, evt):
        self.SetForegroundColour(wx.BLACK)
        if self.GetValue() == self.default_text:
            self.SetValue("")
        evt.Skip()

    def OnKillFocus(self, evt):
        if self.GetValue().strip() == "":
            self.SetValue(self.default_text)
            self.SetForegroundColour(wx.LIGHT_GREY)
        if evt:
            evt.Skip()
            
    def GetRealValue(self):
        if self.GetValue() == self.default_text:
            return ""
        else:
            return self.GetValue()