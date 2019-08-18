# -*- coding: utf-8 -*-

'''
27 May 2019
@autor: Daniel Carrasco
'''

import logging
import wx

### Log Configuration ###
log = logging.getLogger("MainWindow")

########################################################################
class CTreeCtrl( wx.TreeCtrl ):
    def __init__( self, parent ):
        super( CTreeCtrl, self ).__init__(
            parent,
            1, 
            wx.DefaultPosition, 
            wx.DefaultSize, 
            wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT|wx.RAISED_BORDER
        )

    def OnCompareItems( self, item1, item2 ):
        d1 = self.GetItemData( item1 )
        d2 = self.GetItemData( item2 )
        
        if d1.get('cat', False) and not d2.get('cat', False):
            return -1
        elif d2.get('cat', False) and not d1.get('cat', False):
            return 1
        else:
            items_name = [
                self.GetItemText( item1 ).lower(),
                self.GetItemText( item2 ).lower()
            ]
            if items_name[0] == items_name[1]:
                return 0
            else:
                items_name_sorted = sorted(items_name)
                if self.GetItemText( item1 ).lower() == items_name_sorted[0]:
                    return -1
                else:
                    return 1