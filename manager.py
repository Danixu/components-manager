#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
27 May 2019
@autor: Daniel Carrasco
'''

import logging
import os
import sys
import wx
import wx.lib.agw.ribbon as RB
import wx.html2
from wx.lib.splitter import MultiSplitterWindow
import wx.lib.scrolledpanel as scrolled
#from PIL import Image
from widgets.ShapedButton import ShapedButton
from widgets.PlaceholderTextCtrl import PlaceholderTextCtrl
import globals
import json
from plugins.database.sqlite import dbase
from io import BytesIO
from threading import Timer


global rootPath
if getattr(sys, 'frozen', False):
    # The application is frozen
    rootPath = os.path.dirname(os.path.realpath(sys.executable))
else:
    # The application is not frozen
    # Change this bit to match where you store your data files:
    rootPath = os.path.dirname(os.path.realpath(__file__))

# Load main data
app = wx.App()
globals.init()

### Log Configuration ###
log = logging.getLogger("cManager")
log.setLevel(logging.DEBUG)
# create a file handler
handler = logging.FileHandler(globals.options['logFile'], 'a+', 'utf-8')
# create a logging format
formatter = logging.Formatter(
    '%(asctime)s - %(funcName)s() - %(levelname)s: %(message)s'
)
handler.setFormatter(formatter)
# add the handlers to the logger
log.addHandler(handler)
log.debug("Changing log level to {}".format(globals.options['logLevel']))
log.setLevel(globals.options['logLevel'])

# ID de los botones
ID_CAT_ADD = wx.ID_HIGHEST + 1
ID_CAT_ADDSUB = ID_CAT_ADD + 1
ID_CAT_RENAME = ID_CAT_ADDSUB + 1
ID_CAT_DELETE = ID_CAT_RENAME + 1
ID_COM_ADD = ID_CAT_DELETE + 1
ID_COM_DEL = ID_COM_ADD + 1
ID_COM_ED = ID_COM_DEL + 1
ID_IMG_ADD = ID_COM_ED + 1
ID_IMG_DEL = ID_IMG_ADD + 1

# Connecting to Database
database = dbase("{}/{}".format(rootPath, "database.sqlite3"), auto_commit = True)

# Loading all components JSON
component_db = {}
for json_file in os.listdir(
      globals.dataFolder["components"], 
    ):
    if json_file.endswith('.json'):
        with open(
          os.path.join(
            globals.dataFolder["components"], 
            json_file
          ), 
          encoding='utf-8'
        ) as file_data:
            json_data = json.loads(file_data.read())
            component_db.update(json_data)
          


########################################################################
########################################################################
########################################################################
class addComponentWindow(wx.Dialog):
###=== Exit Function ===###
    def close_dialog(self, event):
        self.closed = True
        self.Destroy()
    
    #----------------------------------------------------------------------
    def __init__(self, parent = None, component_id = None):
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
        
        # Add a panel so it looks the correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)
        
        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.close_dialog)
        
        # Variables
        self.inputs = {}
        self.parent = parent
        self.component_id = component_id
        
        # Si se está editando, se sacan los datos
        self.edit_component = {}
        if self.component_id:
          component = database.query("SELECT * FROM Components WHERE id = ?;", (self.component_id, ))
          component_data = database.query("SELECT * FROM Components_data WHERE Component = ?;", (self.component_id, ))
          self.edit_component = {
              "name": component[0][2],
              "template": component[0][3]
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
        for obj, data in component_db.items():
            self.combo.Append(data['name'], obj)
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
    

    def _getComponentControl(self, item, type, choices = [], value = None, default = None, size = None, sort = None, placeholder = ""):
        control = None
        if type.lower() == "input":
            control = PlaceholderTextCtrl(
                self.scrolled_panel, 
                value = value or default or "",
                placeholder = placeholder
            )
            if value:
                control.SetValue(value)
                
        elif type.lower() == "combobox":
            if size:
                style = wx.CB_READONLY|wx.CB_SORT|wx.CB_DROPDOWN
                if not sort:
                    style = wx.CB_READONLY|wx.CB_DROPDOWN
                control = wx.ComboBox(
                    self.scrolled_panel, 
                    choices = choices,
                    size=(size, 25),
                    style=style
                )
            else:
                style = wx.CB_READONLY|wx.CB_SORT|wx.CB_DROPDOWN
                if not sort:
                    style = wx.CB_READONLY|wx.CB_DROPDOWN
                control = wx.ComboBox(
                    self.scrolled_panel, 
                    choices = choices,
                    style=style
                )
            
            if value or default:
                located = control.FindString(value or default)
                if located != wx.NOT_FOUND:
                    control.SetSelection(located)
                else:
                    control.SetSelection(0)
            
            elif control.GetCount() > 0:
                control.SetSelection(0)
            
        elif type.lower() == "checkbox":
            control = wx.CheckBox(self.scrolled_panel, id=wx.ID_ANY)
            control.SetValue(
                globals.strToValue(
                    value or default,
                    "bool"
                )
            )
 
        else:
            log.warning("The component input tipe is not correct {}".format(item))
            
        return control
            
        
    def onComponentSelection(self, event):
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
            size=(self.left_collumn_size, 25),
            style=0,
        )
        iDataBox.Add(label)
        
        value = ""
        if self.component_id:
            value = self.edit_component.get("name")
        elif component_db[component].get('default_name', False):
            value = component_db[component].get('default_name')
        
        self.inputs["name"] = PlaceholderTextCtrl(
            self.scrolled_panel, 
            value = value
        )
        iDataBox.Add(self.inputs["name"], 1, wx.EXPAND)
        iDataBox.AddSpacer(self.padding)
        self.spSizer.Add(iDataBox, 0, wx.EXPAND)
        
        for item, data in component_db[component].get('data', {}).items():
            self.spSizer.AddSpacer(self.items_spacing)
            iDataBox = wx.BoxSizer(wx.HORIZONTAL)
            iDataBox.AddSpacer(self.padding)
            label = wx.StaticText(
                self.scrolled_panel,
                id=wx.ID_ANY,
                label=data["text"],
                size=(self.left_collumn_size, 25),
                style=0,
            )
            iDataBox.Add(label)
            
            for cont, cont_data in data.get('controls', {}).items():
                control_name = "{}_{}".format(item, cont)
                self.inputs[control_name] = self._getComponentControl(
                    control_name, 
                    cont_data['type'], 
                    cont_data.get('choices', []),
                    value = self.edit_component.get(control_name, "") if self.component_id else None,
                    default = cont_data.get('default', None),
                    size = cont_data.get('size', None),
                    sort = cont_data.get('sort', True),
                    placeholder = cont_data.get('placeholder', "")
                )
                if not self.inputs.get(control_name, False):
                    log.error("There was an error creating the control {}".format(control_name))
                    continue
                else:
                    if not cont_data.get('size', None):
                        iDataBox.Add(self.inputs[control_name], 1)
                    else:
                        iDataBox.Add(self.inputs[control_name], 0, wx.EXPAND)
            
            iDataBox.AddSpacer(self.padding)
            self.spSizer.Add(iDataBox, 0, wx.EXPAND)
            
        self.scrolled_panel.Layout()
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
        
        
        component_data = {}
        for item, data in component_db[self.inputs["component"]].get('data', {}).items():
            for cont, cont_data in data.get('controls', {}).items():
                control_name = "{}_{}".format(item, cont)
                item_data = None
                if cont_data['type'].lower() == "input":
                    item_data = self.inputs[control_name].GetValue()
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
        if database.component_add(componentName, component_data, categoryData["id"]):
            newID = database.query("SELECT max(id) FROM Components", None)
            self.inputs["dbid"] = newID[0][0]
            
            for item, data in component_data.items():
                if not item in ["name", "template"]:
                    database.query(
                        "INSERT INTO Components_Data(Component, Key, Value) VALUES (?, ?, ?);",
                        (
                          self.inputs["dbid"],
                          item,
                          str(data)
                        )
                    )
            
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
        
        component_data = {}
        for item, data in component_db[self.inputs["component"]].get('data', {}).items():
            for cont, cont_data in data.get('controls', {}).items():
                control_name = "{}_{}".format(item, cont)
                item_data = None
                if cont_data['type'].lower() == "input":
                    item_data = self.inputs[control_name].GetValue()
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
        
        database.query (
            "UPDATE Components SET Name = ? WHERE id = ?",
            (
              componentName,
              self.component_id
            )
        )
        
        for item, data in component_data.items():
            if not item in ["name", "template"]:
                exists = database.query(
                    "SELECT COUNT(id) FROM Components_Data WHERE Component = ? AND Key = ?;",
                    (
                        self.component_id,
                        item
                    )
                )
                if len(exists) > 0:
                    database.query(
                        "INSERT INTO Components_Data(Component, Key, Value) VALUES (?, ?, ?);",
                        (
                          self.component_id,
                          item,
                          str(data)
                        )
                    )
                
                else:
                    database.query(
                        "UPDATE Components_Data SET Value = ? WHERE Component = ? AND Key = ?;",
                        (
                          str(data),
                          self.component_id,
                          item
                        )
                    )
        
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


########################################################################
########################################################################
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


########################################################################
########################################################################
########################################################################
class mainWindow(wx.Frame):
    ###=== Exit Function ===###
    def exitGUI(self, event):
        self.Destroy()
        
        
    def category_create(self, event):
      dlg = wx.TextEntryDialog(self, 'Nombre de la catergoría', 'Añadir categoría')
      dlg.SetValue("")
      if dlg.ShowModal() == wx.ID_OK:
          try:
              if database.category_add(dlg.GetValue()):
                  newID = database.query("SELECT max(id) FROM Categories", None)
                  self.tree.AppendItem(
                      self.tree_root, 
                      dlg.GetValue(), 
                      image=0, 
                      selImage= 1, 
                      data={
                        "id": newID[0][0],
                        "cat": True,
                      }
                  )
                  self.tree.SortChildren(self.tree_root)
                  #self.tree_filter()
                  log.debug("Category {} added correctly".format(dlg.GetValue()))
              else:
                    dlg = wx.MessageDialog(
                        None, 
                        "Error creando la categoría",
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return

          except Exception as e:
              dlg = wx.MessageDialog(
                  None, 
                  "Error creando la categoría: {}".format(e),
                  'Error',
                  wx.OK | wx.ICON_ERROR
              )
              dlg.ShowModal()
              dlg.Destroy()
              return
          
      dlg.Destroy()
      
      
    def subcat_create(self, event):
        item = self.tree.GetSelection()
        if not item.IsOk():
            dlg = wx.MessageDialog(
                None, 
                "Debe seleccionar una categoria",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return

        itemName = self.tree.GetItemText(item)
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        dlg = wx.TextEntryDialog(
          self,
          'Nombre de la subcatergoría a añadir en "{}"'.format(itemName),
          'Añadir subcategoría'
        )
        #dlg.SetValue("")
        if dlg.ShowModal() == wx.ID_OK:
            try:
                if database.category_add(dlg.GetValue(), itemData["id"]):
                    newID = database.query("SELECT max(id) FROM Categories", None)
                    
                    self.tree.AppendItem(
                        self.tree.GetSelection(), 
                        dlg.GetValue(), 
                        image=0, 
                        selImage= 1, 
                        data={
                          "id": newID[0][0],
                          "cat": True,
                        }
                    )
                    self.tree.SortChildren(self.tree.GetSelection())
                    if not self.tree.IsExpanded(self.tree.GetSelection()):
                        self.tree.Expand(self.tree.GetSelection())
                    log.debug("Subcategory {} added correctly".format(dlg.GetValue()))
                    #self.tree_filter()
                else:
                    dlg = wx.MessageDialog(
                        None, 
                        "Error creando la categoría",
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
            except Exceptino as e:
                dlg = wx.MessageDialog(
                    None, 
                    "Error creando la categoría: {}".format(e),
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()
                return
              
        dlg.Destroy()
      
      
    def category_rename(self, event):
      itemName = self.tree.GetItemText(self.tree.GetSelection())
      itemData = self.tree.GetItemData(self.tree.GetSelection())
      dlg = wx.TextEntryDialog(
          self,
          'Nuevo nombre de la categoría',
          'Renombrar categoría'
      )
      dlg.SetValue(itemName)
      if dlg.ShowModal() == wx.ID_OK:
        try:
          database.category_rename(dlg.GetValue(), itemData["id"])
          itemNewName = database.component_data_parse(itemData["id"], dlg.GetValue())
          self.tree.SetItemText(self.tree.GetSelection(), itemNewName)
          log.debug("Category {} renamed to {} correctly".format(itemName, itemNewName))

        except Exception as e:
          log.error("Error renaming {} to {}.".format(itemName, dlg.GetValue()))
          
      dlg.Destroy()
      #self.tree_filter()


    def category_delete_tree(self, event):
        itemName = self.tree.GetItemText(self.tree.GetSelection())
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        if not itemData:
            dlg = wx.MessageDialog(
                None, 
                "Debe seleccionar una categoría".format(itemName),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        dlg = wx.MessageDialog(
            None, 
            "¿Seguro que desea eliminar la categoría {}?.\n\n".format(itemName) +
            "AVISO: Se borrarán todas las subcategorías y componentes que contiene.",
            'Eliminar',
            wx.YES_NO | wx.ICON_QUESTION
        )

        if dlg.ShowModal() == wx.ID_YES:
            self._category_delete(itemData["id"])
            self.tree.Delete(self.tree.GetSelection())
            self.buttonBarUpdate(self.tree.GetSelection())
            log.debug("Category {} deleted correctly".format(itemName))
            
        dlg.Destroy()
        #self.tree_filter()
      
      
    def _category_delete(self, id):
        try:
            database.query("DELETE FROM Components WHERE Category = ?;", (id, ))
            childs = database.query("SELECT id FROM Categories WHERE Parent = ?;", (id, ))
            for child in childs:
              self._category_delete(child[0])
            
            database.query("DELETE FROM Categories WHERE ID = ?;", (id, ))
            log.debug("Category id {} deleted correctly".format(id))
          
        except:
            log.error("There was an error deleting the category.")


    def component_add(self, event):
        component_frame = addComponentWindow(self)
        
        #component_frame.MakeModal(true);
        component_frame.ShowModal()
        if component_frame.inputs.get("dbid", False):
          self.tree.AppendItem(
              self.tree.GetSelection(), 
              database.component_data_parse(
                  component_frame.inputs["dbid"],
                  component_frame.inputs["name"].GetValue()
              ),
              image=2, 
              selImage= 3,
              data={
                "id": component_frame.inputs["dbid"],
                "cat": False,
              }
          )
          self.tree.SortChildren(self.tree.GetSelection())
          if not self.tree.IsExpanded(self.tree.GetSelection()):
              self.tree.Expand(self.tree.GetSelection())
        component_frame.Destroy()
        
        
    def component_edit(self, event):
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        component_frame = addComponentWindow(self, itemData["id"])

        component_frame.ShowModal()
        
        if not component_frame.closed:
            itemNewName = database.component_data_parse(itemData["id"], component_frame.inputs["name"].GetValue())
            self.tree.SetItemText(self.tree.GetSelection(), itemNewName)
            self.tree.SortChildren(self.tree.GetSelection())
            if not self.tree.IsExpanded(self.tree.GetSelection()):
                self.tree.Expand(self.tree.GetSelection())
            
            self.tree_selection(None)
            component_frame.Destroy()
        
        
    def component_delete(self, event):
        itemName = self.tree.GetItemText(self.tree.GetSelection())
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        if not itemData:
            dlg = wx.MessageDialog(
                None, 
                "Debe seleccionar un componente".format(itemName),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        dlg = wx.MessageDialog(
            None, 
            "¿Seguro que desea eliminar el componente {}?.\n\n".format(itemName),
            'Eliminar',
            wx.YES_NO | wx.ICON_QUESTION
        )

        if dlg.ShowModal() == wx.ID_YES:
            try:
                database.query("DELETE FROM Components_Data WHERE Component = ?;", (itemData["id"], ))
                database.query("DELETE FROM Components WHERE ID = ?;", (itemData["id"], ))
                self.tree.Delete(self.tree.GetSelection())
                self.buttonBarUpdate(self.tree.GetSelection())
                log.debug("Component id {} deleted correctly".format(itemData["id"]))
              
            except:
                log.error("There was an error deleting the category.")

    
    def image_add(self, event):
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Abrir fichero de imagen", wildcard="Imágenes (*.jpg, *.jpeg, *.png, *.gif, *.bmp)|*.jpg;*.jpeg;*.png;*.gif;*.bmp|Todos los ficheros (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            image = database.image_add(
                fileDialog.GetPath(), 
                self.image_size, 
                itemData.get('id'), 
                itemData.get('cat')
            )
            if image:
                self.tree_selection(None)
                
                
    def image_delete(self, event):
        itemName = self.tree.GetItemText(self.tree.GetSelection())
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        imageID = self.loaded_images_id[self.actual_image]
        if not imageID:
            dlg = wx.MessageDialog(
                None, 
                "El item no tiene imagen".format(itemName),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False
            
        if not itemData:
            dlg = wx.MessageDialog(
                None, 
                "Debe seleccionar un item",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        dlg = wx.MessageDialog(
            None, 
            "¿Seguro que desea eliminar la imagen de {}?.\n\n".format(itemName),
            'Eliminar',
            wx.YES_NO | wx.ICON_QUESTION
        )

        if dlg.ShowModal() == wx.ID_YES:
            try:
                database.image_delete(imageID)
                self.tree_selection(None)
            except:
                log.error("There was an error deleting the image.")
    
     
    def change_image_next(self, event):
        self.actual_image += 1

        if self.actual_image == 0:
            self.button_back.Disable()
        else:
            self.button_back.Enable()
        
        if self.actual_image == (len(self.loaded_images)-1):
            self.button_next.Disable()
        else:
            self.button_next.Enable()
            
        self.onImageResize(None)
        
        if event:
            event.Skip()
        
        
    def change_image_back(self, event):
        self.actual_image -= 1

        if self.actual_image == 0:
            self.button_back.Disable()
        else:
            self.button_back.Enable()
        
        if self.actual_image == (len(self.loaded_images)-1):
            self.button_next.Disable()
        else:
            self.button_next.Enable()
            
        self.onImageResize(None)
        
        if event:
            event.Skip()
            

    def tree_filter(self, parent_item = None, category_id = -1, filter = None, expanded = False):
      if category_id == -1:
        self.tree.DeleteAllItems()
        
      if not parent_item:
        parent_item = self.tree_root
        
      cats = database.query("SELECT * FROM Categories WHERE Parent = ? ORDER BY Name COLLATE NOCASE ASC;", (category_id, ))
      for item in cats:
        id = self.tree.AppendItem(
            parent_item, 
            item[2], 
            image=0, 
            selImage= 1, 
            data={
              "id": item[0],
              "cat": True,
            }
        )
        
        child_cat = database.query("SELECT COUNT(*) FROM Categories WHERE Parent = ?;", (item[0], ))
        child_com = database.query("SELECT COUNT(*) FROM Components WHERE Category = ?;", (item[0], ))
        if child_cat[0][0] > 0 or child_com[0][0] > 0:
          self.tree_filter(id, item[0], filter, item[3])
        elif filter:
          self.tree.Delete(id)
      
      components = {}
      if filter:
        sql_filter = "%{}%".format(filter)
        components = database.query("SELECT * FROM Components WHERE Category = ? AND Name LIKE ? ORDER BY Name COLLATE NOCASE ASC;", (category_id, sql_filter))
      else:
        components = database.query("SELECT * FROM Components WHERE Category = ? ORDER BY Name COLLATE NOCASE ASC;", (category_id, ))
      for component in components:
        if not filter or filter.lower() in component[2].lower():
            self.tree.AppendItem(
                parent_item, 
                database.component_data_parse(component[0], component[2]),
                image=2,
                selImage= 3,
                data={
                  "id": component[0],
                  "cat": False,
                }
            )

      if not self.tree.ItemHasChildren(parent_item) and filter:
          self.tree.Delete(parent_item)
      else:
          if not parent_item == self.tree_root:
              if expanded:
                  self.tree.Expand(parent_item)
              else:
                  self.tree.Collapse(parent_item)
        
      if category_id == -1:
          self.last_filter = filter
          self.tree.Refresh()
        
               
    def tree_selection(self, event):
        if self.tree and self.tree.GetSelection():
            if self.last_selected_item:
                self.tree.SetItemBold(self.last_selected_item, False)
            self.last_selected_item = self.tree.GetSelection()
            self.tree.SetItemBold(self.last_selected_item, True)
            self.buttonBarUpdate(self.tree.GetSelection())
            self.tree.SelectItem(self.tree.GetSelection())
            itemData = self.tree.GetItemData(self.tree.GetSelection())
            del self.loaded_images
            del self.loaded_images_id
            self.loaded_images = []
            self.loaded_images_id = []
            self.actual_image = 0
            for item in database.query(
                "SELECT * FROM Images WHERE Category = ? AND Parent = ?;",
                (
                    itemData.get('cat'),
                    itemData.get('id')
                )
            ):
                sbuf = BytesIO(item[3])
                self.loaded_images.append(
                    wx.Image(sbuf)
                )
                self.loaded_images_id.append(
                    item[0]
                )
                
            if len(self.loaded_images) == 0:
                self.loaded_images_id.append(None)
                self.loaded_images = [wx.Image()]
                self.loaded_images[0].LoadFile(
                    os.path.join(
                      globals.dataFolder["images"], 
                      'no_image.png'
                    )
                )
                self.button_back.Disable()
                self.button_next.Disable()
            else:
                self.button_back.Disable()
                if len(self.loaded_images) > 1:
                    self.button_next.Enable()
                else:
                    self.button_next.Disable()
            
            if not itemData.get('cat'):
                html = database.selection_to_html(itemData.get('id'), component_db)
                self.textFrame.SetPage(html, "http://localhost/")
            self.onImageResize(None)
            
        if event:
            event.Skip()
            
    def _tree_item_collapsed(self, event):
        if event.GetItem().IsOk():
            itemData = self.tree.GetItemData(event.GetItem())
            database.query("UPDATE Categories SET Expanded = ? WHERE ID = ?;", (False, itemData['id']))
            
        
    def _tree_item_expanded(self, event):
        if event.GetItem().IsOk():
            itemData = self.tree.GetItemData(event.GetItem())
            database.query("UPDATE Categories SET Expanded = ? WHERE ID = ?;", (True, itemData['id']))
            
            
    def _tree_drag_start(self, event):
        event.Allow()
        self.dragItem = event.GetItem()


    def _tree_drag_end(self, event):
        # If we dropped somewhere that isn't on top of an item, ignore the event
        if event.GetItem().IsOk():
            target = event.GetItem()
        else:
            return
            
        # Make sure this member exists.
        try:
            source = self.dragItem
        except:
            return
            
        # Don't do anything if destination is the parent of source
        if self.tree.GetItemParent(source) == target:
            log.info("The destination is the actual parent")
            self.tree.Unselect()
            return
            
        if self._ItemIsChildOf(target, source):
            log.info("Tree item can not be moved into itself or a child!")
            self.tree.Unselect()
            return
            
        src_data = self.tree.GetItemData(source)
        target_data = self.tree.GetItemData(target)  

        if not target_data['cat']:
            log.info("Destination is a component, and only categories are allowed as destination")
            return

        try:
            if src_data['cat']:
                database.query("UPDATE Categories SET Parent = ? WHERE ID = ?;", (target_data['id'], src_data['id']))
            else:
                database.query("UPDATE Components SET Category = ? WHERE ID = ?;", (target_data['id'], src_data['id']))
            
        except Exception as e:
            pass
            return

        self.tree.Delete(source)
        self.tree.DeleteChildren(target)
        self.tree.Freeze()
        self.tree_filter(parent_item = target, category_id = target_data['id'], filter = self.last_filter, expanded = False)
        self.tree.Expand(target)
        self.tree.Thaw()

      
    def _ItemIsChildOf(self, searchID, itemID):
        if itemID == searchID:
            return True
    
        item, cookie = self.tree.GetFirstChild(itemID)
        while item.IsOk():
            itemName = self.tree.GetItemText(item)
            itemSearchName = self.tree.GetItemText(searchID)
            log.debug("Checking if item {} is {}".format(itemName, itemSearchName))
            if item == searchID:
                log.debug("Items are equal")
                return True
            else:
                log.debug("Items are different")
                
            if self.tree.ItemHasChildren(item):
                log.debug("Item {} has children".format(itemName))
                if self._ItemIsChildOf(searchID, item):
                    return True
                
            item, cookie =  self.tree.GetNextChild(itemID, cookie)
        return False
    
    
    def buttonBarUpdate(self, itemID):
      itemData = self.tree.GetItemData(itemID)
      if itemData.get("cat", False):
        self.cat_bbar.EnableButton(ID_CAT_ADDSUB, True)
        self.cat_bbar.EnableButton(ID_CAT_DELETE, True)
        self.cat_bbar.EnableButton(ID_CAT_RENAME, True)
        self.com_bbar.EnableButton(ID_COM_ADD, True)
        self.com_bbar.EnableButton(ID_COM_DEL, False)
        self.com_bbar.EnableButton(ID_COM_ED, False)
        self.img_bbar.EnableButton(ID_IMG_ADD, True)
        self.img_bbar.EnableButton(ID_IMG_DEL, True)
      else:
        self.cat_bbar.EnableButton(ID_CAT_ADDSUB, False)
        self.cat_bbar.EnableButton(ID_CAT_DELETE, False)
        self.cat_bbar.EnableButton(ID_CAT_RENAME, False)
        self.com_bbar.EnableButton(ID_COM_ADD, False)
        self.com_bbar.EnableButton(ID_COM_DEL, True)
        self.com_bbar.EnableButton(ID_COM_ED, True)
        self.img_bbar.EnableButton(ID_IMG_ADD, True)
        self.img_bbar.EnableButton(ID_IMG_DEL, True)
        
        
    def onImageResize(self, event):
        frame_size = self.image.GetSize()
        if frame_size[0] != 0:
          image = self.loaded_images[self.actual_image]
          bitmap = wx.Bitmap(image.Scale(frame_size[0], frame_size[0]))
          self.image.SetBitmap(bitmap)
          
        if event:
            event.Skip()


    def _search(self, event):
        # SQLITE es threadSafe, por lo que de momento no se usa
        if self.timer:
            self.timer.cancel()
        
        searchText = self.search.GetRealValue()
        if len(searchText) > 3:
            self.timer = Timer(2, self.tree_filter, {"filter": searchText})
            self.timer.start()
        
        if event:
            event.Skip()
    
    
    def _searchText(self, event):
        searchText = self.search.GetRealValue()
        
        self.tree.Freeze()
        if len(searchText) > 2:
            self.tree_filter(filter = searchText)
        elif len(searchText) == 0:
            self.tree_filter()
        else:
            dlg = wx.MessageDialog(
                None, 
                "Debe indicar al menos tres letras".format(itemName),
                'Aviso',
                wx.OK | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()
        
        self.tree.Thaw()
        if event:
            event.Skip()
    

    ###=== Main Function ===###
    def __init__(self):
        wx.Frame.__init__(
            self,
            None,
            title="Components Manager",
            size=(800,900)
        )

        # Changing the icon
        icon = wx.Icon(
            os.path.join(globals.dataFolder["images"], 'icon.ico'), 
            wx.BITMAP_TYPE_ICO
        )
        self.SetIcon(icon)
        
        log.info("Loading main windows...")
        self.Bind(wx.EVT_CLOSE, self.exitGUI)
        
        # Variables
        self.actual_image = 0
        self.loaded_images_id = [None]
        self.loaded_images = [wx.Image()]
        self.loaded_images[0].LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'no_image.png'
            )
        )
        self.image_size = (500, 500)
        self.timer = None
        self.last_filter = None
        self.last_selected_item = None

        # Creating splitter
        log.debug("Creating splitter")
        # Main Splitter
        splitter = wx.SplitterWindow(self, -1, style=wx.RAISED_BORDER)
        
        # Ribbon Bar
        ribbon = RB.RibbonBar(self, -1)
        page = RB.RibbonPage(ribbon, wx.ID_ANY, "Page")
        
        ##--------------------##
        ### Panel Categorías ###
        pCat = RB.RibbonPanel(page, wx.ID_ANY, "Categorías")
        self.cat_bbar = RB.RibbonButtonBar(pCat)
        # Add Category
        image = wx.Bitmap()
        image.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'add_cat.png'
            )
        )
        self.cat_bbar.AddSimpleButton(ID_CAT_ADD, "Añadir Categoría", image, '')
        # Add SubCategory
        image = wx.Bitmap()
        image.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'add_subcat.png'
            )
        )
        self.cat_bbar.AddSimpleButton(ID_CAT_ADDSUB, "Añadir Subcategoría", image, '')
        # Change Name
        image = wx.Bitmap()
        image.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'ren_cat.png'
            )
        )
        self.cat_bbar.AddSimpleButton(ID_CAT_RENAME, "Cambiar Nombre", image, '')
        # Delete category
        image = wx.Bitmap()
        image.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'del_cat.png'
            )
        )
        self.cat_bbar.AddSimpleButton(ID_CAT_DELETE, "Eliminar", image, '')
        
        ##---------------------##
        ### Panel Componentes ###
        pCom = RB.RibbonPanel(page, wx.ID_ANY, "Componentes")
        self.com_bbar = RB.RibbonButtonBar(pCom)
        # Add Component
        image = wx.Bitmap()
        image.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'add_com.png'
            )
        )
        self.com_bbar.AddSimpleButton(
            ID_COM_ADD, 
            "Añadir", 
            image, ''
        )
        # Edit Component
        image = wx.Bitmap()
        image.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'edit_com.png'
            )
        )
        self.com_bbar.AddSimpleButton(ID_COM_ED, "Editar", image, '')
        # Delete Component
        image = wx.Bitmap()
        image.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'del_com.png'
            )
        )
        self.com_bbar.AddSimpleButton(ID_COM_DEL, "Eliminar", image, '')
        
        ##------------------##
        ### Panel Imágenes ###
        pImg = RB.RibbonPanel(page, wx.ID_ANY, "Imágenes")
        self.img_bbar = RB.RibbonButtonBar(pImg)
        # Add Component
        image = wx.Bitmap()
        image.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'add_image.png'
            )
        )
        self.img_bbar.AddSimpleButton(ID_IMG_ADD, "Añadir", image, '')
        # Delete Component
        image = wx.Bitmap()
        image.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'del_image.png'
            )
        )
        self.img_bbar.AddSimpleButton(ID_IMG_DEL, "Eliminar", image, '')
        
        # Eventos al pulsar botones
        self.cat_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.category_create, id=ID_CAT_ADD)
        self.cat_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.subcat_create, id=ID_CAT_ADDSUB)
        self.cat_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.category_rename, id=ID_CAT_RENAME)
        self.cat_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.category_delete_tree, id=ID_CAT_DELETE)
        self.com_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.component_add, id=ID_COM_ADD)
        self.com_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.component_edit, id=ID_COM_ED)
        self.com_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.component_delete, id=ID_COM_DEL)
        self.img_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.image_add, id=ID_IMG_ADD)
        self.img_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.image_delete, id=ID_IMG_DEL)
        
        self.cat_bbar.EnableButton(ID_CAT_ADDSUB, False)
        self.cat_bbar.EnableButton(ID_CAT_DELETE, False)
        self.cat_bbar.EnableButton(ID_CAT_RENAME, False)
        self.com_bbar.EnableButton(ID_COM_ADD, False)
        self.com_bbar.EnableButton(ID_COM_DEL, False)
        self.com_bbar.EnableButton(ID_COM_ED, False)
        self.img_bbar.EnableButton(ID_IMG_ADD, False)
        self.img_bbar.EnableButton(ID_IMG_DEL, False)
        
        # Pintar Ribbon
        ribbon.Realize()
        
        b1, b2 = 10, 0
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(ribbon, 0, wx.EXPAND)
        vsizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(vsizer)
        
        # Left Panel
        lPan = wx.Panel(splitter, style=wx.RAISED_BORDER)
        lPanBox = wx.BoxSizer(wx.VERTICAL)
        searchBox = wx.BoxSizer(wx.HORIZONTAL)
        # Search TextBox
        self.search = PlaceholderTextCtrl(
            lPan,
            style=wx.RAISED_BORDER|wx.TE_PROCESS_ENTER,
            value = "",
            placeholder = "Introduce texto a buscar (mínimo 3 letras)"
        )
        searchBox.Add(self.search, 1, wx.EXPAND)
        # Search Button
        button_search_up = wx.Bitmap()
        button_search_up.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'button_search_up.png'
            )
        )
        button_search_down = wx.Bitmap()
        button_search_down.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'button_search_down.png'
            )
        )
        button_search_disabled = button_search_down.ConvertToDisabled()
        button_search_over = wx.Bitmap()
        button_search_over.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'button_search_over.png'
            )
        )
        self.button_search = ShapedButton(lPan, 
            button_search_up,
            button_search_down, 
            button_search_disabled,
            button_search_over,
            size=(25,25)
        )
        self.button_search.Bind(wx.EVT_LEFT_UP, self._searchText)
        searchBox.Add(self.button_search, 0, wx.EXPAND)
        lPanBox.Add(searchBox, 0, wx.EXPAND)
        #self.search.Bind(wx.EVT_TEXT, self._search)
        self.search.Bind(wx.EVT_TEXT_ENTER, self._searchText)
        # Components Tree
        self.tree = CTreeCtrl(lPan)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.tree_selection, id=1)
        self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self._tree_drag_start)
        self.tree.Bind(wx.EVT_TREE_END_DRAG, self._tree_drag_end)
        self.tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self._tree_item_collapsed)
        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self._tree_item_expanded)
        self.tree_root = self.tree.AddRoot('Categorias')
        self.tree_imagelist = wx.ImageList(16, 16)
        self.tree.AssignImageList(self.tree_imagelist)
        lPanBox.Add(self.tree, 1, wx.EXPAND)
        lPan.SetSizer(lPanBox) 
        #ImageList Images
        for imageFN in [
          "folder_closed.png",
          "folder_open.png",
          "component.png",
          "component_selected.png",
        ]:
          log.debug("Load tree image {}".format(imageFN))
          image = wx.Bitmap()
          image.LoadFile(
              os.path.join(
                globals.dataFolder["images"], 
                imageFN
              )
          )
          self.tree_imagelist.Add(image)
        
        # Right Splitter
        rPan = wx.SplitterWindow(splitter, -1, style=wx.RAISED_BORDER)
        splitter.SplitVertically(lPan, rPan)
        splitter.SetSashGravity(0.5)

        imageSizer = wx.BoxSizer(wx.HORIZONTAL)
        imageFrame = wx.Panel(rPan, style=wx.RAISED_BORDER)

        ### Image Frame ###
        # Back Button
        button_back_up = wx.Bitmap()
        button_back_up.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'button_back_up.png'
            )
        )
        button_back_down = wx.Bitmap()
        button_back_down.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'button_back_down.png'
            )
        )
        button_back_disabled = button_back_down.ConvertToDisabled()
        button_back_over = wx.Bitmap()
        button_back_over.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'button_back_over.png'
            )
        )
        self.button_back = ShapedButton(imageFrame, 
            button_back_up,
            button_back_down, 
            button_back_disabled,
            button_back_over,
            size=(36,36)
        )
        self.button_back.Bind(wx.EVT_LEFT_UP, self.change_image_back)
        
        # Next Button
        button_next_up = wx.Bitmap()
        button_next_up.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'button_next_up.png'
            )
        )
        
        button_next_down = wx.Bitmap()
        button_next_down.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'button_next_down.png'
            )
        )
        button_next_disabled = button_next_up.ConvertToDisabled()
        button_next_over = wx.Bitmap()
        button_next_over.LoadFile(
            os.path.join(
              globals.dataFolder["images"], 
              'button_next_over.png'
            )
        )
        self.button_next = ShapedButton(imageFrame, 
            button_next_up,
            button_next_down, 
            button_next_disabled,
            button_next_over,
            size=(36,36)
        )
        self.button_next.Bind(wx.EVT_LEFT_UP, self.change_image_next)
        
        # Image Box
        self.image = wx.StaticBitmap(imageFrame, wx.ID_ANY, self.loaded_images[self.actual_image].ConvertToBitmap(), style=wx.RAISED_BORDER)
        #self.image.SetScaleMode(wx.Scale_AspectFit) # No implementado en el módulo
        self.image.Bind(wx.EVT_SIZE, self.onImageResize)
        self.button_back.Enable(False)
        self.button_next.Enable(False)
        
        # Image Sizer with buttons and image box
        imageSizer.Add(self.button_back, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        imageSizer.AddSpacer(5)
        imageSizer.Add(self.image, 1, wx.SHAPED | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL)
        imageSizer.AddSpacer(10)
        imageSizer.Add(self.button_next, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)
        
        # Righ Panel split
        imageFrame.SetSizer(imageSizer)        
        #self.textFrame = wx.html.HtmlWindow(rPan, -1, style= wx.VSCROLL|wx.HSCROLL|wx.TE_READONLY|wx.BORDER_SIMPLE)
        self.textFrame = wx.html2.WebView.New(rPan, style=wx.TE_READONLY|wx.RAISED_BORDER)
        
        rPan.SplitHorizontally(imageFrame, self.textFrame)
        rPan.SetSashGravity(0.4)
        
        # Updating tree
        self.tree_filter()
        
        
        


#======================
# Start GUI
#======================
mainWindow().Show()
app.MainLoop()

