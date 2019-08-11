'''
17 June 2018
@autor: Daniel Carrasco
'''
import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
  def __init__(self, parent):
    wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER,
              size=wx.Size(410, 485), pos=wx.Point(10, 10))
    CheckListCtrlMixin.__init__(self)
    ListCtrlAutoWidthMixin.__init__(self)