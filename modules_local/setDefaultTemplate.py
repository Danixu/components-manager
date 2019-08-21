# -*- coding: utf-8 -*-

'''
18 Aug 2019
@autor: Daniel Carrasco
'''

import logging
import wx


### Log Configuration ###
log = logging.getLogger("MainWindow")


class setDefaultTemplate(wx.Dialog):
###=== Exit Function ===###
    def close_dialog(self, event):
        self.closed = True
        self.Destroy()
        
        
    def _save(self, event):
        component = self.combo.GetClientData(self.combo.GetSelection())
        
        try:
            log.debug("Setting the category template to {}".format(component))
            self.database.query(
                "UPDATE Categories SET Template = ? WHERE ID = ?",
                (
                    component,
                    self.category_id
                )
            )
            self.database.conn.commit()
            
            dlg = wx.MessageDialog(
                None, 
                "Se ha cambiado la plantilla por defecto correctamente.",
                'Correcto',
                wx.OK | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()
            self.close_dialog(None)
            
        except Exception as e:
            log.error("There was an error updating category default template. {}".format(e))
            dlg = wx.MessageDialog(
                None, 
                "Ocurrió un error al guardar la plantilla por defecto de la categoría.",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            
    
    #----------------------------------------------------------------------
    def __init__(self, parent, database, component_db):
        wx.Dialog.__init__(
            self, 
            parent, 
            wx.ID_ANY, 
            "Plantilla por defecto", 
            size=(400, 170),
            style=wx.DEFAULT_DIALOG_STYLE
        )
        
        # Add a panel so it looks the correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)
        
        self.database = database
        
        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.close_dialog)
        
        # Variables
        self.inputs = {}
        self.component_db = component_db
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.AddSpacer(20)
        
        label = wx.StaticText(
            self.panel ,
            id=wx.ID_ANY,
            label="Seleccione la plantilla por defecto para la categoría",
            style=0,
        )
        vsizer.Add(label, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vsizer.AddSpacer(10)
        self.combo = wx.ComboBox(self.panel , choices = [], style=wx.CB_READONLY|wx.CB_SORT|wx.CB_DROPDOWN)
        self.combo.Append("_Sin plantilla por defecto", None)
        for name, data in self.component_db.items():
            self.combo.Append(data['name'], name)
        vsizer.Add(self.combo, 0, wx.EXPAND)
        vsizer.AddSpacer(20)
        
        # Buttons BoxSizer
        btn_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        btn_add = wx.Button(self.panel, label = "Guardar")
        btn_add.Bind(wx.EVT_BUTTON, self._save)
        btn_cancel = wx.Button(self.panel, label = "Cancelar")
        btn_cancel.Bind(wx.EVT_BUTTON, self.close_dialog)
        btn_sizer.AddSpacer(10)
        btn_sizer.Add(btn_add)
        btn_sizer.AddSpacer(40)
        btn_sizer.Add(btn_cancel)
        btn_sizer.AddSpacer(10)
        
        vsizer.Add(btn_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        hsizer.AddSpacer(20)
        hsizer.Add(vsizer, 1, wx.EXPAND)
        hsizer.AddSpacer(20)
        self.panel.SetSizer(hsizer)
        
        itemData = parent.tree.GetItemData(parent.tree.GetSelection())
        self.category_id = itemData['id']
        template = self.database.query("SELECT Template FROM Categories WHERE ID = ?;", (itemData['id'], ))
        
        located = None
        for comboid in range(0, self.combo.GetCount()):
            component = self.combo.GetClientData(comboid)
            if component == template[0][0]:
                located = comboid

        if located != None:
            self.combo.SetSelection(located)
        else:
            if self.combo.GetCount() > 0:
                self.combo.SetSelection(0)
                


                
            