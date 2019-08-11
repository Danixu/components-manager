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
import globals
import json
from plugins.database.sqlite import dbase
from io import BytesIO


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
handler = logging.FileHandler(globals.options['logFile'])
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
database = dbase("{}/{}".format(rootPath, "test.sqlite3"))

# Loading all components JSON
component_db = {}
for json_file in os.listdir(
      os.path.join(
        globals.dataFolder["plugins"], 
        'components/'
      )
    ):
    if json_file.endswith('.json'):
        with open(
          os.path.join(
            globals.dataFolder["plugins"], 
            'components/',
            json_file
          )
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
            size=(500,500)
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
                    "No se ha encontrado la plantilla del componente. No podrá editarlo.",
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
            size=(self.left_collumn_size, 20),
            style=0,
        )
        iDataBox.Add(label)
        
        self.inputs["name"] = wx.TextCtrl(self.scrolled_panel, value="")
        if self.component_id:
            self.inputs["name"].SetValue(self.edit_component.get("name"))
        iDataBox.Add(self.inputs["name"], 1, wx.EXPAND)
        self.spSizer.Add(iDataBox, 0, wx.EXPAND)
        
        for item, data in component_db[component].get('data', {}).items():
            self.spSizer.AddSpacer(self.items_spacing)
            iDataBox = wx.BoxSizer(wx.HORIZONTAL)
            iDataBox.AddSpacer(self.padding)
            label = wx.StaticText(
                self.scrolled_panel,
                id=wx.ID_ANY,
                label=data["text"],
                size=(self.left_collumn_size, 20),
                style=0,
            )
            iDataBox.Add(label)
            
            self.inputs[item] = None
            if data['type'].lower() == "input":
                self.inputs[item] = wx.TextCtrl(self.scrolled_panel, value="")
                if self.component_id:
                    self.inputs[item].SetValue(self.edit_component.get(item, ""))
                iDataBox.Add(self.inputs[item], 1, wx.EXPAND)
            elif data['type'].lower() == "combobox":
                self.inputs[item] = wx.ComboBox(
                    self.scrolled_panel,
                    choices = data['choices'],
                    style=wx.CB_READONLY|wx.CB_SORT|wx.CB_DROPDOWN
                )
                if self.component_id:
                    located = self.inputs[item].FindString(self.edit_component.get(item, ""))
                    if located != wx.NOT_FOUND:
                        self.inputs[item].SetSelection(located)
                    else:
                        self.inputs[item].SetSelection(0)
                
                elif self.inputs[item].GetCount() > 0:
                    self.inputs[item].SetSelection(0)
                iDataBox.Add(self.inputs[item], 1, wx.EXPAND)
            elif data['type'].lower() == "checkbox":
                self.inputs[item] = wx.CheckBox(self.scrolled_panel, id=wx.ID_ANY)
                if self.component_id:
                    self.inputs[item].SetValue(
                        globals.strToValue(
                            self.edit_component.get(
                                item,
                                data.get('default', "false")
                            ),
                            "bool"
                        )
                    )
                else:
                    self.inputs[item].SetValue(globals.strToValue(data.get('default', "false"), "bool"))
                iDataBox.Add(self.inputs[item], 1)
            else:
                log.warning("The component input tipe is not correct {}".format(item))
            
            #iDataBox.Add(self.inputs[item], 1, wx.EXPAND)
            iDataBox.AddSpacer(self.padding)
            
            self.spSizer.Add(iDataBox, 0, wx.EXPAND)
            
        self.scrolled_panel.Layout()
        self.scrolled_panel.SetupScrolling()
        
        
    def add_component(self, event):
        categoryData = self.parent.tree.GetItemData(self.parent.tree_itemID)
        
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
            item_data = None
            if data['type'].lower() == "input":
                item_data = self.inputs[item].GetValue()
            elif data['type'].lower() == "combobox":
                item_data = self.inputs[item].GetStringSelection()
            elif data['type'].lower() == "checkbox":
                item_data = str(self.inputs[item].GetValue())
            else:
                log.warning("The component input tipe is not correct {}".format(item))
            
            component_data.update({item: item_data})

        component_data.update({"template": self.inputs["component"]})
        if database.add_component(componentName, component_data, categoryData["id"]):
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
            database.conn.commit()
            
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
            item_data = None
            if data['type'].lower() == "input":
                item_data = self.inputs[item].GetValue()
            elif data['type'].lower() == "combobox":
                item_data = self.inputs[item].GetStringSelection()
            elif data['type'].lower() == "checkbox":
                item_data = str(self.inputs[item].GetValue())
            else:
                log.warning("The component input tipe is not correct {}".format(item))
            
            component_data.update({item: item_data})

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
        database.conn.commit()
        
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
        print( 'in CTreeCtrl.OnCompareItems()' )
        
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
      dlg = wx.TextEntryDialog(self, 'Nombre de la catergoría','Añadir categoría')
      dlg.SetValue("")
      if dlg.ShowModal() == wx.ID_OK:
        database.add_category(dlg.GetValue())
        newID = database.query("SELECT max(id) FROM Category", None)
        self.tree.AppendItem(
            self.tree_root, 
            dlg.GetValue(), 
            image=0, 
            selImage= 1, 
            data={
              "id": newID[0],
              "cat": True,
            }
        )
        self.tree.SortChildren(self.tree_root)
        #self.filter_tree()
        log.debug("Category {} added correctly".format(dlg.GetValue()))
          
      dlg.Destroy()
      
      
    def subcat_create(self, event):
      itemName = self.tree.GetItemText(self.tree.GetSelection())
      itemData = self.tree.GetItemData(self.tree.GetSelection())
      dlg = wx.TextEntryDialog(
        self,
        'Nombre de la subcatergoría a añadir en "{}"'.format(itemName),
        'Añadir subcategoría'
      )
      #dlg.SetValue("")
      if dlg.ShowModal() == wx.ID_OK:
        database.add_category(dlg.GetValue(), itemData["id"])
        newID = database.query("SELECT max(id) FROM Category", None)
        
        self.tree.AppendItem(
            self.tree.GetSelection(), 
            dlg.GetValue(), 
            image=0, 
            selImage= 1, 
            data={
              "id": newID[0],
              "cat": True,
            }
        )
        self.tree.SortChildren(self.tree.GetSelection())
        if not self.tree.IsExpanded(self.tree.GetSelection()):
            self.tree.Expand(self.tree.GetSelection())
        log.debug("Subcategory {} added correctly".format(dlg.GetValue()))
        #self.filter_tree()
        
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
          database.rename_category(dlg.GetValue(), itemData["id"])
          self.tree.SetItemText(self.tree.GetSelection(), dlg.GetValue())
          log.debug("Category {} renamed to {} correctly".format(itemName, dlg.GetValue()))

        except Exception as e:
          log.error("Error renaming {} to {}.".format(itemName, dlg.GetValue()))
          
      dlg.Destroy()
      #self.filter_tree()


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
            database.conn.commit()
            self.tree.Delete(self.tree.GetSelection())
            self.buttonBarUpdate(self.tree.GetSelection())
            log.debug("Category {} deleted correctly".format(itemName))
            
        dlg.Destroy()
        #self.filter_tree()
      
      
    def _category_delete(self, id):
        try:
            database.query("DELETE FROM Components WHERE Category = ?;", (id, ))
            childs = database.query("SELECT id FROM Category WHERE Parent = ?;", (id, ))
            for child in childs:
              self._category_delete(child[0])
            
            database.query("DELETE FROM Category WHERE ID = ?;", (id, ))
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
              component_frame.inputs["name"].GetValue(),
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
            self.tree.SetItemText(self.tree.GetSelection(), component_frame.inputs["name"].GetValue())
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
                database.conn.commit()
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
                "Debe seleccionar un item".format(itemName),
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
    
    def filter_tree(self, parent_item = None, category_id = -1, filter = None):
      if category_id == -1:
        self.tree.DeleteAllItems()
        
      if not parent_item:
        parent_item = self.tree_root
        
      cats = database.query("SELECT * FROM Category WHERE Parent = ? ORDER BY Name COLLATE NOCASE ASC;", (category_id, ))
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
        
        child_cat = database.query("SELECT COUNT(*) FROM Category WHERE Parent = ?;", (item[0], ))
        child_com = database.query("SELECT COUNT(*) FROM Components WHERE Category = ?;", (item[0], ))
        if child_cat[0][0] > 0 or child_com[0][0] > 0:
          self.filter_tree(id, item[0], filter)
        elif filter:
          self.tree.Delete(id)
      
      components = {}
      if filter:
        components = database.query("SELECT * FROM Components WHERE Category = ? AND Name LIKE \"%?%\" ORDER BY Name COLLATE NOCASE ASC;", (category_id, filter))
      else:
        components = database.query("SELECT * FROM Components WHERE Category = ? ORDER BY Name COLLATE NOCASE ASC;", (category_id, ))
      for component in components:
        if not filter or filter.lower() in component[2].lower():
          self.tree.AppendItem(
              parent_item, 
              component[2],
              image=2, 
              selImage= 3,
              data={
                "id": component[0],
                "cat": False,
              }
          )

      if not self.tree.ItemHasChildren(parent_item):
        self.tree.Delete(parent_item)
        
        
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
            
            
    def tree_selection(self, event):
      if self.tree and self.tree.GetSelection():
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
      
      
    def buttonBarUpdate(self, itemID):
      itemData = self.tree.GetItemData(itemID)
      if itemData.get("cat", False):
        self.cat_bbar.EnableButton(ID_CAT_ADDSUB, True)
        self.cat_bbar.EnableButton(ID_CAT_DELETE, True)
        self.cat_bbar.EnableButton(ID_CAT_RENAME, True)
        self.com_bbar.EnableButton(ID_COM_ADD, True)
        self.com_bbar.EnableButton(ID_COM_DEL, False)
        self.com_bbar.EnableButton(ID_COM_ED, False)
      else:
        self.cat_bbar.EnableButton(ID_CAT_ADDSUB, False)
        self.cat_bbar.EnableButton(ID_CAT_DELETE, False)
        self.cat_bbar.EnableButton(ID_CAT_RENAME, False)
        self.com_bbar.EnableButton(ID_COM_ADD, False)
        self.com_bbar.EnableButton(ID_COM_DEL, True)
        self.com_bbar.EnableButton(ID_COM_ED, True)
        
        
    def onImageResize(self, event):
        print("Resized")
        frame_size = self.image.GetSize()
        if frame_size[0] != 0:
          image = wx.Bitmap(self.loaded_images[self.actual_image].Scale(frame_size[0], frame_size[0]))
          self.image.SetBitmap(image)


    ###=== Main Function ===###
    def __init__(self):
        wx.Frame.__init__(
            self,
            None,
            title="Components Manager",
            size=(800,900)
        )
        
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
        
        # Pintar Ribbon
        ribbon.Realize()
        
        b1, b2 = 10, 0
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(ribbon, 0, wx.EXPAND)
        vsizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(vsizer)
        
        # Left Panel (Tree)
        self.tree = CTreeCtrl(splitter)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.tree_selection, id=1)
        self.tree_root = self.tree.AddRoot('Categorias')
        self.tree_imagelist = wx.ImageList(16, 16)
        self.tree.AssignImageList(self.tree_imagelist)
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
        splitter.SplitVertically(self.tree, rPan)
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
        self.filter_tree()
        
        
        


#======================
# Start GUI
#======================
mainWindow().Show()
app.MainLoop()

