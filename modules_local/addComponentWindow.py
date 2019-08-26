# -*- coding: utf-8 -*-

'''
22 Aug 2019
@autor: Daniel Carrasco
'''

import logging
import os
import sys
import wx
import wx.lib.scrolledpanel as scrolled
from widgets import PlaceholderTextCtrl
from modules import strToValue
#from threading import Timer


### Log Configuration ###
log = logging.getLogger("MainWindow")


class addComponentWindow(wx.Dialog):
###=== Exit Function ===###
    def close_dialog(self, event):
        self.closed = True
        self.Destroy()
    
    #----------------------------------------------------------------------
    def __init__(self, database, components_db, values_db, parent = None, component_id = None, default_template = None):
        wx.Dialog.__init__(
            self, 
            parent, 
            wx.ID_ANY, 
            "{} componente".format("Editar" if component_id else "Añadir"), 
            size=(500,500),
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
        )
        
        self.left_collumn_size = 100
        self.padding = 10
        self.items_spacing = 5
        self.database = database
        
        # Add a panel so it looks the correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)
        
        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.close_dialog)
        
        # Variables
        self.inputs = {}
        self.parent = parent
        self.component_id = component_id
        self.components_db = components_db
        self.values_db = values_db
        self.default_template = default_template
        
        # Si se está editando, se sacan los datos
        try:
          del(self.edit_component)
         
        except:
          pass
          
        self.edit_component = {}
        if self.component_id:
          component = self.database.query("SELECT * FROM Components WHERE id = ?;", (self.component_id, ))
          component_data = self.database.query("SELECT * FROM Components_data WHERE Component = ?;", (self.component_id, ))
          self.edit_component = {
              "name": component[0][2],
              "new_amount": str(component[0][3]),
              "recycled_amount": str(component[0][4]),
              "template": component[0][5]
          }
          for item in component_data:
            self.edit_component.update({ item[2]: item[3] })
        
        # --------------------
        # Scrolled panel stuff
        self.scrolled_panel = scrolled.ScrolledPanel(
          self.panel, 
          -1, 
          style = wx.TAB_TRAVERSAL|wx.BORDER_THEME, 
          name="panel"
        )
        #self.scrolled_panel.SetAutoLayout(True)
        #self.scrolled_panel.SetupScrolling()
        self.spSizer = wx.BoxSizer(wx.VERTICAL)
        self.spSizer.AddSpacer(self.padding)
        self.scrolled_panel.SetSizer(self.spSizer)
        # --------------------

        # Buttons BoxSizer
        btn_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        btn_add = wx.Button(self.panel,
            label="Añadir" if not component_id else "Guardar"
        )
        if self.component_id:
            btn_add.Bind(wx.EVT_BUTTON, self.update_component)
        else:
            btn_add.Bind(wx.EVT_BUTTON, self.add_component)
        btn_cancel = wx.Button(self.panel, label="Cancelar")
        btn_cancel.Bind(wx.EVT_BUTTON, self.close_dialog)
        btn_sizer.AddSpacer(10)
        btn_sizer.Add(btn_add)
        btn_sizer.AddSpacer(40)
        btn_sizer.Add(btn_cancel)
        btn_sizer.AddSpacer(10)
        
        # Combobox Component kind selector
        comboSizer = wx.BoxSizer(wx.HORIZONTAL)
        comboSizer.AddSpacer(self.padding)
        self.combo = wx.ComboBox(self.panel, choices = [], style=wx.CB_READONLY|wx.CB_SORT|wx.CB_DROPDOWN)
        for name, data in self.components_db.items():
            self.combo.Append(data['name'], name)
        self.combo.Bind(wx.EVT_COMBOBOX, self.onComponentSelection)
        
        if self.component_id:
            located = None
            for comboid in range(0, self.combo.GetCount()):
                component = self.combo.GetClientData(comboid)
                if component == self.edit_component.get("template", ""):
                    located = comboid

            if located != None:
                self.combo.SetSelection(located)
                self.onComponentSelection(None)
                self.combo.Enable(False)
            else:
                dlg = wx.MessageDialog(
                    None, 
                    "No se ha encontrado la plantilla del componente. No podrá editarlo hasta que corrija el problema.",
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()
                self.close_dialog(None)
        elif self.default_template:
            located = None
            for comboid in range(0, self.combo.GetCount()):
                component = self.combo.GetClientData(comboid)
                if component == self.default_template:
                    located = comboid

            if located != None:
                self.combo.SetSelection(located)
                self.onComponentSelection(None)
            else:
                self.combo.SetSelection(0)
                self.onComponentSelection(None)
        elif self.combo.GetCount() > 0:
            self.combo.SetSelection(0)
            self.onComponentSelection(None)
        
        comboSizer.Add(self.combo, 1, wx.EXPAND)
        comboSizer.AddSpacer(self.padding)

        # Final BoxSizer
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.AddSpacer(self.padding)
        panelSizer.Add(comboSizer, 0, wx.EXPAND)
        panelSizer.AddSpacer(self.padding)
        panelSizer.Add(self.scrolled_panel, 1, wx.EXPAND)
        panelSizer.AddSpacer(20)
        panelSizer.Add(btn_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
        panelSizer.AddSpacer(20)
        self.panel.SetSizer(panelSizer)
    

    def _getComponentControl(self, item, data, value = None):
        control = None
        from_values = None
        if data.get('from_values', False):
            from_values = self.values_db.get(data.get('from_values'), None)
        
        if data.get('type', "").lower() == "input":
            control = PlaceholderTextCtrl.PlaceholderTextCtrl(
                self.scrolled_panel, 
                value = value or data.get('default', ""),
                placeholder = data.get('placeholder', "")
            )
                
        elif data.get('type', "").lower() == "combobox":
            if data.get('size', None):
                style = wx.CB_READONLY|wx.CB_SORT|wx.CB_DROPDOWN
                if not data.get('sort', False):
                    style = wx.CB_READONLY|wx.CB_DROPDOWN
                control = wx.ComboBox(
                    self.scrolled_panel, 
                    choices = from_values or data.get('choices', []),
                    size=(data.get('size'), 25),
                    style=style
                )
            else:
                style = wx.CB_READONLY|wx.CB_SORT|wx.CB_DROPDOWN
                if not data.get('sort', False):
                    style = wx.CB_READONLY|wx.CB_DROPDOWN
                control = wx.ComboBox(
                    self.scrolled_panel, 
                    choices = from_values or data.get('choices', []),
                    style=style
                )
            
            if value or data.get('default', False):
                located = control.FindString(value or data.get('default'))
                if located != wx.NOT_FOUND:
                    control.SetSelection(located)
                else:
                    control.SetSelection(0)
            
            elif control.GetCount() > 0:
                control.SetSelection(0)
            
        elif data.get('type', "").lower() == "checkbox":
            control = wx.CheckBox(self.scrolled_panel, id=wx.ID_ANY)
            control.SetValue(
                strToValue.strToValue(
                    value or data.get('default', False),
                    "bool"
                )
            )
 
        else:
            log.warning("The component input tipe is not correct {}".format(item))
            
        return control
            
        
    def onComponentSelection(self, event):
        # Freezing the panel to speed up the change
        # Also avoid the bad looking of the process
        self.scrolled_panel.Freeze()
        self.spSizer.Clear(True)
        try:
            del self.inputs
        except:
            pass
        
        self.inputs = {}
        
        component = self.combo.GetClientData(self.combo.GetSelection())
        self.inputs["component"] = component
        
        self.spSizer.AddSpacer(self.items_spacing)
        iDataBox = wx.BoxSizer(wx.HORIZONTAL)
        iDataBox.AddSpacer(self.padding)
        label = wx.StaticText(
            self.scrolled_panel,
            id=wx.ID_ANY,
            label="Nombre",
            size=(self.left_collumn_size, 15),
            style=0,
        )
        iDataBox.Add(label, 0, wx.TOP, 5)
        
        value = ""
        if self.component_id:
            value = self.edit_component.get("name")
        elif self.components_db[component].get('default_name', False):
            value = self.components_db[component].get('default_name')
        
        self.inputs["name"] = PlaceholderTextCtrl.PlaceholderTextCtrl(
            self.scrolled_panel, 
            value = value
        )
        iDataBox.Add(self.inputs["name"], 1, wx.EXPAND)
        iDataBox.AddSpacer(self.padding)
        self.spSizer.Add(iDataBox, 0, wx.EXPAND)

        self.spSizer.AddSpacer(self.items_spacing)
        iDataBox = wx.BoxSizer(wx.HORIZONTAL)
        iDataBox.AddSpacer(self.padding)
        label = wx.StaticText(
            self.scrolled_panel,
            id=wx.ID_ANY,
            label="Cantidad Nuevo",
            size=(self.left_collumn_size, 15),
            style=0,
        )
        iDataBox.Add(label, 0, wx.TOP, 5)
        
        value = "0"
        if self.component_id:
            value = self.edit_component.get("new_amount", "0")
        
        self.inputs["new_amount"] = PlaceholderTextCtrl.PlaceholderTextCtrl(
            self.scrolled_panel, 
            value = value
        )
        iDataBox.Add(self.inputs["new_amount"], 1, wx.EXPAND)
        iDataBox.AddSpacer(30)
        label = wx.StaticText(
            self.scrolled_panel,
            id=wx.ID_ANY,
            label="Reciclado",
            size=(55, 15),
            style=0|wx.ALIGN_CENTRE_VERTICAL ,
        )
        iDataBox.Add(label, 0, wx.TOP, 5)
        
        value = "0"
        if self.component_id:
            value = self.edit_component.get("recycled_amount", "0")
        
        self.inputs["recycled_amount"] = PlaceholderTextCtrl.PlaceholderTextCtrl(
            self.scrolled_panel, 
            value = value
        )
        iDataBox.Add(self.inputs["recycled_amount"], 1, wx.EXPAND)
        iDataBox.AddSpacer(self.padding)
        self.spSizer.Add(iDataBox, 0, wx.EXPAND)
        
        for item, data in self.components_db[component].get('data', {}).items():
            self.spSizer.AddSpacer(self.items_spacing)
            iDataBox = wx.BoxSizer(wx.HORIZONTAL)
            iDataBox.AddSpacer(self.padding)
            label = wx.StaticText(
                self.scrolled_panel,
                id=wx.ID_ANY,
                label=data["text"],
                size=(self.left_collumn_size, 15),
                style=0,
            )
            iDataBox.Add(label, 0, wx.TOP, 5)
            
            for cont, cont_data in data.get('controls', {}).items():
                control_name = "{}_{}".format(item, cont)
                self.inputs[control_name] = self._getComponentControl(
                    control_name, 
                    cont_data,
                    self.edit_component.get(control_name, None)
                )
                if not self.inputs.get(control_name, False):
                    log.error("There was an error creating the control {}".format(control_name))
                    continue
                else:
                    if cont_data.get('label', False):
                        label = wx.StaticText(
                            self.scrolled_panel,
                            id=wx.ID_ANY,
                            label=cont_data.get('label'),
                            size=(cont_data.get('label_size', -1), 15),
                            style=0,
                        )
                        iDataBox.AddSpacer(10)
                        iDataBox.Add(label, 0, wx.TOP, 5)
                        iDataBox.AddSpacer(5)
                        
                 
                    if not cont_data.get('size', None):
                        iDataBox.Add(self.inputs[control_name], 1)
                    else:
                        iDataBox.Add(self.inputs[control_name], 0, wx.EXPAND)
            
            iDataBox.AddSpacer(self.padding)
            self.spSizer.Add(iDataBox, 0, wx.EXPAND)
        
        # Draw the Layout, Unfreeze and setup the scroll
        self.scrolled_panel.Layout()
        self.scrolled_panel.Thaw()
        self.scrolled_panel.SetupScrolling()
        
        
    def add_component(self, event):
        categoryData = self.parent.tree.GetItemData(self.parent.tree.GetSelection())
        
        componentName = self.inputs["name"].GetValue()
        if componentName == "":
          dlg = wx.MessageDialog(
              None, 
              "No ha indicado ningún nombre para el componente.",
              'Error',
              wx.OK | wx.ICON_ERROR
          )
          dlg.ShowModal()
          dlg.Destroy()
          return False
        
        newAmount = strToValue.strToValue(self.inputs["new_amount"].GetValue(), "int")
        recycledAmount = strToValue.strToValue(self.inputs["recycled_amount"].GetValue(), "int")
        
        component = {
            "new_amount": newAmount,
            "recycled_amount": recycledAmount
        }
        component_data = {}
        for item, data in self.components_db[self.inputs["component"]].get('data', {}).items():
            for cont, cont_data in data.get('controls', {}).items():
                control_name = "{}_{}".format(item, cont)
                item_data = None
                if cont_data['type'].lower() == "input":
                    item_data = self.inputs[control_name].GetRealValue()
                elif cont_data['type'].lower() == "combobox":
                    item_data = self.inputs[control_name].GetStringSelection()
                elif cont_data['type'].lower() == "checkbox":
                    item_data = str(self.inputs[control_name].GetValue())
                else:
                    log.warning("The component input tipe is not correct {}".format(control_name))
                
                
                if cont_data.get('required', False) and item_data == "":
                    dlg = wx.MessageDialog(
                        None, 
                        "El campo '{}' es obligatorio.".format(data['text']),
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                else:
                    component_data.update({control_name: item_data})

        component.update(
            {
                "template": self.inputs["component"],
                "component_data": component_data,
            }
        )
        component_id = self.database.component_add(componentName, component, categoryData["id"])
        if component_id and len(component_id) > 0:
            self.inputs["dbid"] = component_id[0]

            dlg = wx.MessageDialog(
                None, 
                "Componente añadido corréctamente.",
                'OK',
                wx.OK | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()
            self.closed = False
            self.Hide()
        else:
            dlg = wx.MessageDialog(
                None, 
                "Ocurrió un error al añadir el componente.",
                'OK',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            
    def update_component(self, event):
        componentName = self.inputs["name"].GetValue()
        if componentName == "":
          dlg = wx.MessageDialog(
              None, 
              "No ha indicado ningún nombre para el componente.",
              'Error',
              wx.OK | wx.ICON_ERROR
          )
          dlg.ShowModal()
          dlg.Destroy()
          return False
          
        newAmount = strToValue.strToValue(self.inputs["new_amount"].GetValue(), "int")
        recycledAmount = strToValue.strToValue(self.inputs["recycled_amount"].GetValue(), "int")
        
        component_data = {}
        for item, data in self.components_db[self.inputs["component"]].get('data', {}).items():
            for cont, cont_data in data.get('controls', {}).items():
                control_name = "{}_{}".format(item, cont)
                item_data = None
                if cont_data['type'].lower() == "input":
                    item_data = self.inputs[control_name].GetRealValue()
                elif cont_data['type'].lower() == "combobox":
                    item_data = self.inputs[control_name].GetStringSelection()
                elif cont_data['type'].lower() == "checkbox":
                    item_data = str(self.inputs[control_name].GetValue())
                else:
                    log.warning("The component input tipe is not correct {}".format(control_name))
                
                if cont_data.get('required', False) and item_data == "":
                    dlg = wx.MessageDialog(
                        None, 
                        "El campo '{}' es obligatorio.".format(data['text']),
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                else:
                    component_data.update({control_name: item_data})

        component_data.update({"template": self.inputs["component"]})
        
        self.database.query (
            "UPDATE Components SET Name = ?, New_amount = ?, Recycled_amount = ? WHERE id = ?",
            (
              componentName,
              newAmount,
              recycledAmount,
              self.component_id
            )
        )
        
        for item, data in component_data.items():
            if not item in ["name", "template"]:
                exists = self.database.query(
                    "SELECT COUNT(id) FROM Components_Data WHERE Component = ? AND Key = ?;",
                    (
                        self.component_id,
                        item
                    )
                )
                if len(exists) > 0:
                    self.database.query(
                        "INSERT INTO Components_Data(Component, Key, Value) VALUES (?, ?, ?);",
                        (
                          self.component_id,
                          item,
                          str(data)
                        )
                    )
                
                else:
                    self.database.query(
                        "UPDATE Components_Data SET Value = ? WHERE Component = ? AND Key = ?;",
                        (
                          str(data),
                          self.component_id,
                          item
                        )
                    )
        
        self.database.conn.commit()
        dlg = wx.MessageDialog(
            None, 
            "Componente actualizado corréctamente.",
            'OK',
            wx.OK | wx.ICON_INFORMATION
        )
        dlg.ShowModal()
        dlg.Destroy()
        self.closed = False
        self.Hide()