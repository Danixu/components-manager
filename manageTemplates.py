#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
27 May 2019
@autor: Daniel Carrasco
'''

import logging
import sys
import wx
import wx.lib.agw.ribbon as RB
from widgets import PlaceholderTextCtrl
from modules import getResourcePath, strToValue
import wx.lib.scrolledpanel as scrolled
from modules_local import CTreeCtrl
import globals
from plugins.database.sqlite import dbase
#from threading import Timer

# Load main data
app = wx.App()
globals.init()

### Log Configuration ###
log = logging.getLogger("MainWindow")

# ID de los botones
ID_CAT_ADD = wx.ID_HIGHEST + 1
ID_CAT_ADDSUB = ID_CAT_ADD + 1
ID_CAT_RENAME = ID_CAT_ADDSUB + 1
ID_CAT_DELETE = ID_CAT_RENAME + 1
ID_TEM_ADD = ID_CAT_DELETE + 1
ID_TEM_RENAME = ID_TEM_ADD + 1
ID_TEM_DELETE = ID_TEM_RENAME + 1
ID_FIELD_ADD = ID_TEM_DELETE + 1
ID_FIELD_DELETE = ID_FIELD_ADD + 1


# Connecting to Database
database_templates = dbase("{}/{}".format(globals.rootPath, "templates.sqlite3"), auto_commit = False, templates = True)


########################################################################
########################################################################
########################################################################
class addFieldDialog(wx.Dialog):
    def close_dialog(self, event):
        self.closed = True
        self.Destroy()
    
    def _save(self, event):
        if self.label.GetRealValue() == "":
            dlg = wx.MessageDialog(
                None, 
                "Debe indicar la etiqueta del campo",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        else:
            self.Hide()
            
    def __init__(self, parent):
        wx.Dialog.__init__(
            self, 
            parent, 
            wx.ID_ANY, 
            "Añadir campo", 
            size=(300, 220),
            style=wx.DEFAULT_DIALOG_STYLE
        )
        
        # Values
        self.border = 20
        self.between_items = 5
        self.label_size = 60
        self.closed = False

        panel = wx.Panel(self)
        panelBox = wx.BoxSizer(wx.VERTICAL)
        panelBox.AddSpacer(self.border)
        
        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.close_dialog)        

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.AddSpacer(self.border)
        box.Add(
            wx.StaticText(panel, -1, "Etiqueta", size=(self.label_size, 15)),
            0,
            wx.EXPAND
        )
        self.label = PlaceholderTextCtrl.PlaceholderTextCtrl(
            panel, 
            value = "",
            placeholder = "Etiqueta del campo (obligatoria)"
        )
        box.Add(self.label, -1, wx.EXPAND)
        box.AddSpacer(self.border)
        panelBox.Add(box, 0, wx.EXPAND)
        panelBox.AddSpacer(self.between_items)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.AddSpacer(self.border)
        box.Add(
            wx.StaticText(panel, -1, "Tipo", size=(self.label_size, 15)),
            0,
            wx.EXPAND
        )
        self.type = wx.ComboBox(panel, id=wx.ID_ANY,
            choices=parent.field_kind,
            style=wx.CB_READONLY|wx.CB_DROPDOWN
        )
        self.type.SetSelection(0)
        box.Add(self.type, -1, wx.EXPAND)
        box.AddSpacer(self.border)
        panelBox.Add(box, 0, wx.EXPAND)
        panelBox.AddSpacer(self.between_items)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.AddSpacer(self.border)
        box.Add(
            wx.StaticText(panel, -1, "Tamaño", size=(self.label_size, 15)),
            0,
            wx.EXPAND
        )
        self.width = PlaceholderTextCtrl.PlaceholderTextCtrl(
            panel, 
            value = "",
            placeholder = "Vacío para automático"
        )
        box.Add(self.width, -1, wx.EXPAND)
        box.AddSpacer(self.border)
        panelBox.Add(box, 0, wx.EXPAND)
        panelBox.AddSpacer(self.between_items)
        
        panelBox.AddSpacer(self.border)
        panel.SetSizer(panelBox)
        
        ##--------------------------------------------------##
        # Buttons BoxSizer
        btn_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        btn_add = wx.Button(panel, label="Aceptar")
        btn_add.Bind(wx.EVT_BUTTON, self._save)
        btn_cancel = wx.Button(panel, label="Cancelar")
        btn_cancel.Bind(wx.EVT_BUTTON, self.close_dialog)
        btn_sizer.AddSpacer(10)
        btn_sizer.Add(btn_add)
        btn_sizer.AddSpacer(40)
        btn_sizer.Add(btn_cancel)
        btn_sizer.AddSpacer(10)

        panelBox.Add(btn_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)
        ##--------------------------------------------------##
        

########################################################################
########################################################################
########################################################################
class manageTemplates(wx.Frame):
    ###=== Exit Function ===###
    def exitGUI(self, event):
        # Avoid slow close by deleting tree items
        self.tree.Freeze()
        self.Destroy()


    def _category_create(self, event):
      dlg = wx.TextEntryDialog(self, 'Nombre de la catergoría', 'Añadir categoría')
      dlg.SetValue("")
      if dlg.ShowModal() == wx.ID_OK:
          try:
              category_id = database_templates.category_add(dlg.GetValue())
              if category_id and len(category_id) > 0:
                  newID = category_id[0]
                  self.tree.AppendItem(
                      self.tree_root, 
                      dlg.GetValue(), 
                      image=0, 
                      selImage= 1, 
                      data={
                        "id": newID,
                        "cat": True,
                        "subcat": False,
                        "template": False
                      }
                  )
                  self.tree.SortChildren(self.tree_root)
                  #self._tree_filter()
                  log.debug("Category {} added correctly".format(dlg.GetValue()))
                  return newID
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


    def _subcat_create(self, event):
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
                category_id = database_templates.category_add(dlg.GetValue(), itemData["id"])
                if category_id:
                    newID = category_id[0]
                    self.tree.AppendItem(
                        self.tree.GetSelection(), 
                        dlg.GetValue(), 
                        image=0, 
                        selImage= 1, 
                        data={
                          "id": newID,
                          "cat": False,
                          "subcat": True,
                          "template": False
                        }
                    )
                    self.tree.SortChildren(self.tree.GetSelection())
                    if not self.tree.IsExpanded(self.tree.GetSelection()):
                        self.tree.Expand(self.tree.GetSelection())
                    log.debug("Subcategory {} added correctly".format(dlg.GetValue()))
                    #self._tree_filter()
                else:
                    dlg = wx.MessageDialog(
                        None, 
                        "Error creando la subcategoría",
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
            except Exception as e:
                log.error(
                    "There was an error creating the subcategory: {}".format(e)
                )
                dlg = wx.MessageDialog(
                    None, 
                    "Error creando la subcategoría: {}".format(e),
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()
                return

        dlg.Destroy()


    def _category_rename(self, event):
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
          database_templates.category_rename(dlg.GetValue(), itemData["id"])
          itemNewName = database_templates.component_data_parse(itemData["id"], dlg.GetValue())
          self.tree.SetItemText(self.tree.GetSelection(), itemNewName)
          log.debug("Category {} renamed to {} correctly".format(itemName, itemNewName))

        except Exception as e:
          log.error("Error renaming {} to {}.".format(itemName, dlg.GetValue()))

      dlg.Destroy()
      #self._tree_filter()


    def _category_delete(self, event):
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
            if database_templates.category_delete(itemData["id"]):
                self.tree.Delete(self.tree.GetSelection())
                self._tree_selection(None)
                log.debug("Category {} deleted correctly".format(itemName))
            else:
                print("There was an error deleting the category")
                return


        dlg.Destroy()
        
        
    def _template_create(self, event):
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
          'Nombre de la plantilla a añadir en "{}"'.format(itemName),
          'Añadir plantilla'
        )
        if dlg.ShowModal() == wx.ID_OK:
            try:
                category_id = database_templates.template_add(dlg.GetValue(), itemData["id"])
                if category_id:
                    newID = category_id[0]
                    self.tree.AppendItem(
                        self.tree.GetSelection(), 
                        dlg.GetValue(), 
                        image=2, 
                        selImage= 2, 
                        data={
                          "id": newID,
                          "cat": False,
                          "subcat": False,
                          "template": True
                        }
                    )
                    self.tree.SortChildren(self.tree.GetSelection())
                    if not self.tree.IsExpanded(self.tree.GetSelection()):
                        self.tree.Expand(self.tree.GetSelection())
                    log.debug("Template {} added correctly".format(dlg.GetValue()))
                    #self._tree_filter()
                else:
                    dlg = wx.MessageDialog(
                        None, 
                        "Error creando la plantilla",
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
            except Exception as e:
                log.error(
                    "There was an error creating the template: {}".format(e)
                )
                dlg = wx.MessageDialog(
                    None, 
                    "Error creando la plantilla: {}".format(e),
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()
                return

        dlg.Destroy()


    def _template_rename(self, event):
      itemName = self.tree.GetItemText(self.tree.GetSelection())
      itemData = self.tree.GetItemData(self.tree.GetSelection())
      dlg = wx.TextEntryDialog(
          self,
          'Nuevo nombre de la plantilla',
          'Renombrar plantilla'
      )
      dlg.SetValue(itemName)
      if dlg.ShowModal() == wx.ID_OK:
        try:
          database_templates.template_rename(dlg.GetValue(), itemData["id"])
          itemNewName = dlg.GetValue()
          self.tree.SetItemText(self.tree.GetSelection(), itemNewName)
          log.debug("Template {} renamed to {} correctly".format(itemName, itemNewName))

        except Exception as e:
          log.error("Error renaming {} to {}.".format(itemName, dlg.GetValue()))

      dlg.Destroy()


    def _template_delete(self, event):
        itemName = self.tree.GetItemText(self.tree.GetSelection())
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        if not itemData:
            dlg = wx.MessageDialog(
                None, 
                "Debe seleccionar una plantilla".format(itemName),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        dlg = wx.MessageDialog(
            None, 
            "¿Seguro que desea eliminar la plantilla {}?.\n\n".format(itemName) +
            "AVISO: Se borrarán todos los grupos y campos que contenga.",
            'Eliminar',
            wx.YES_NO | wx.ICON_QUESTION
        )

        if dlg.ShowModal() == wx.ID_YES:
            if database_templates.template_delete(itemData["id"]):
                self.tree.Delete(self.tree.GetSelection())
                self._tree_selection(None)
                log.debug("Template {} deleted correctly".format(itemName))
            else:
                print("There was an error deleting the template")
                return
        dlg.Destroy()
        
        
    def _field_create(self, event):
        item = self.tree.GetSelection()
        if not item.IsOk():
            dlg = wx.MessageDialog(
                None, 
                "Debe seleccionar una plantilla",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return

        itemName = self.tree.GetItemText(item)
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        dlg = addFieldDialog(self)
        dlg.ShowModal()
        
        label = dlg.label.GetRealValue()
        type = dlg.type.GetSelection()
        
        try:
            width = int(dlg.width.GetRealValue())
         
        except:
            width = None
        
        if not dlg.closed:
            database_templates.field_add(
                itemData['id'], 
                label, 
                type, 
                self.fieldList.GetItemCount(),
                width
            )
            self._tree_selection(None)


    def _field_delete(self, event):
        selected = self.fieldList.GetFirstSelected()
        if selected == -1:
            
            dlg = wx.MessageDialog(
                None, 
                "Debe seleccionar un campo",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False
         
        itemName = self.fieldList.GetItem(selected, 0).GetText()
        dlg = wx.MessageDialog(
            None, 
            "¿Seguro que desea eliminar el campo {}?.\n\n".format(itemName),
            'Eliminar',
            wx.YES_NO | wx.ICON_QUESTION
        )

        itemData = self.fieldList.GetItemData(selected)
        if dlg.ShowModal() == wx.ID_YES:
            if database_templates.field_delete(itemData):
                self.fieldList.DeleteItem(selected)
                # Fix for disable delete button when no items left
                if (selected - 1) < 0:
                    self.field_bbar.EnableButton(ID_FIELD_DELETE, False)
                else:
                    self.fieldList.Select(selected-1)
                log.debug("Field {} deleted correctly".format(itemName))
            else:
                print("There was an error deleting the field")
                return
        dlg.Destroy()
        


    def _tree_filter(self, parent_item = None, category_id = -1, filter = None, expanded = False):
      if category_id == -1:
        self.tree.DeleteAllItems()

      if not parent_item:
        parent_item = self.tree_root

      cats = database_templates.query("SELECT * FROM Categories WHERE Parent = ? AND ID <> -1 ORDER BY Name COLLATE NOCASE ASC;", (category_id, ))
      for item in cats:
        id = self.tree.AppendItem(
            parent_item, 
            item[2], 
            image=0, 
            selImage= 1, 
            data={
              "id": item[0],
              "cat": True if parent_item == self.tree_root else False,
              "subcat": False if parent_item == self.tree_root else True,
              "template": False
            }
        )

        child_cat = database_templates.query("SELECT COUNT(*) FROM Categories WHERE Parent = ?;", (item[0], ))
        child_com = database_templates.query("SELECT COUNT(*) FROM Templates WHERE Category = ?;", (item[0], ))
        if child_cat[0][0] > 0 or child_com[0][0] > 0:
          self._tree_filter(id, item[0], filter, item[3])
        elif filter:
          self.tree.Delete(id)

      templates = database_templates.query("SELECT ID, Name FROM Templates WHERE Category = ?;", (category_id, ))
      for template in templates:
          found = False if filter else True

          if filter:
              if filter.lower() in template[1].lower():
                  found = True

          if found:
              tem = self.tree.AppendItem(
                  parent_item, 
                  template[1],
                  image=2,
                  selImage=2,
                  data={
                    "id": template[0],
                    "cat": False,
                    "subcat": False,
                    "template": True
                  }
              )

      if not self.tree.ItemHasChildren(parent_item) and filter:
          self.tree.Delete(parent_item)
      else:
          self.tree.SortChildren(parent_item)
          if not parent_item == self.tree_root:
              if expanded:
                  self.tree.Expand(parent_item)
              else:
                  self.tree.Collapse(parent_item)

      if category_id == -1:
          self.last_filter = filter
          self.tree.Refresh()


    def _tree_selection(self, event):
        if self.tree and self.tree.GetSelection():
            if self.last_selected_item:
                self.tree.SetItemBold(self.last_selected_item, False)
            self.last_selected_item = self.tree.GetSelection()
            self.tree.SetItemBold(self.last_selected_item, True)
            self._buttonBarUpdate(self.tree.GetSelection())
            self.tree.SelectItem(self.tree.GetSelection())
            itemData = self.tree.GetItemData(self.tree.GetSelection())
        
            # Prepare the list
            self.fieldList.DeleteAllItems()
            if itemData.get("template", False):
                self.fieldList.Enable()
                # Add data to list
                query = """SELECT 
                            Fields.ID, 
                            Fields.Label, 
                            Fields.Field_type, 
                            Fields_Data.Value 
                          FROM 
                            Fields 
                          LEFT JOIN 
                            Fields_Data 
                          ON 
                            Fields_Data.Field = Fields.ID 
                          AND 
                            (
                              Fields.Template = ?
                              AND 
                              Fields_Data.Key = 'width'
                            )
                          ORDER BY
                            Fields.Field_order;
                        """
                fields = database_templates.query(query, (itemData.get('id'),))
                for field in fields:
                    index = self.fieldList.InsertItem(self.fieldList.GetItemCount(), field[1])
                    self.fieldList.SetItem(index, 1, self.field_kind[field[2]])
                    self.fieldList.SetItem(index, 2, str(field[3] or "Auto"))
                    self.fieldList.SetItemData(index, field[0])
                
            else:
                self.fieldList.Disable()
        
        if event:
            event.Skip()
            

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
                database_templates.query("UPDATE Categories SET Parent = ? WHERE ID = ?;", (target_data['id'], src_data['id']))
            else:
                database_templates.query("UPDATE Components SET Category = ? WHERE ID = ?;", (target_data['id'], src_data['id']))

        except Exception as e:
            pass
            return

        self.tree.Delete(source)
        self.tree.DeleteChildren(target)
        self.tree.Freeze()
        self._tree_filter(parent_item = target, category_id = target_data['id'], filter = self.last_filter, expanded = False)
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


    def _buttonBarUpdate(self, itemID):
        if not itemID.IsOk():
            log.warning("Tree item is not OK")
            return

        itemData = self.tree.GetItemData(itemID)

        if itemData.get("cat", False):
            self.cat_bbar.EnableButton(ID_CAT_ADDSUB, True)
            self.cat_bbar.EnableButton(ID_CAT_DELETE, True)
            self.cat_bbar.EnableButton(ID_CAT_RENAME, True)
            self.tem_bbar.EnableButton(ID_TEM_ADD, False)
            self.tem_bbar.EnableButton(ID_TEM_RENAME, False)
            self.tem_bbar.EnableButton(ID_TEM_DELETE, False)
            self.field_bbar.EnableButton(ID_FIELD_ADD, False)
            self.field_bbar.EnableButton(ID_FIELD_DELETE, False)
        elif itemData.get("subcat", False):
            self.cat_bbar.EnableButton(ID_CAT_ADDSUB, False)
            self.cat_bbar.EnableButton(ID_CAT_DELETE, True)
            self.cat_bbar.EnableButton(ID_CAT_RENAME, True)
            self.tem_bbar.EnableButton(ID_TEM_ADD, True)
            self.tem_bbar.EnableButton(ID_TEM_RENAME, False)
            self.tem_bbar.EnableButton(ID_TEM_DELETE, False)
            self.field_bbar.EnableButton(ID_FIELD_ADD, False)
            self.field_bbar.EnableButton(ID_FIELD_DELETE, False)
        elif itemData.get("template", False):
            self.cat_bbar.EnableButton(ID_CAT_ADDSUB, False)
            self.cat_bbar.EnableButton(ID_CAT_DELETE, False)
            self.cat_bbar.EnableButton(ID_CAT_RENAME, False)
            self.tem_bbar.EnableButton(ID_TEM_ADD, False)
            self.tem_bbar.EnableButton(ID_TEM_RENAME, True)
            self.tem_bbar.EnableButton(ID_TEM_DELETE, True)
            self.field_bbar.EnableButton(ID_FIELD_ADD, True)
            if self.fieldList.GetFirstSelected() == -1:
                self.field_bbar.EnableButton(ID_FIELD_DELETE, False)
            else:
                self.field_bbar.EnableButton(ID_FIELD_DELETE, True)


    def _searchText(self, event):
        searchText = self.search.GetValue()
        print(searchText)
        self.tree.Freeze()
        if len(searchText) > 2:
            self._tree_filter(filter = searchText)
        elif len(searchText) == 0:
            self._tree_filter()
        else:
            dlg = wx.MessageDialog(
                None, 
                "Debe indicar al menos tres letras",
                'Aviso',
                wx.OK | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()

        self.tree.Thaw()
        if event:
            event.Skip()


    def _cancelSearch(self, event):
        self.search.SetValue("")
        self._searchText(None)
        event.Skip()


    def _vacuum(self, event):
        try:
            dlg = wx.MessageDialog(
                None, 
                "¿Optimizar la Base de Datos?.\n\n" +
                "Este proceso puede tardar un rato",
                'Optimizar',
                wx.YES_NO | wx.ICON_QUESTION
            )

            if dlg.ShowModal() == wx.ID_YES:
                database_templates.vacuum()
                dlg = wx.MessageDialog(
                    None, 
                    "Optimización completa",
                    'Correcto',
                    wx.OK | wx.ICON_INFORMATION
                )
                dlg.ShowModal()
                dlg.Destroy()

        except Exception as e:
            log.error("There was an error optimizing the Database: {}".format(e))
            dlg = wx.MessageDialog(
                None, 
                "There was an error optimizing the Database: {}".format(e),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()


    def _fielfDataSave(self, event):
        pass
        

    def _fieldPanelUpdate(self, event):
        self.modified = False
        selected = self.fieldList.GetFirstSelected()
        try:
            del self.fields
        except:
            pass
        
        self.fields = {}
        if selected != -1:
            selected_id = self.fieldList.GetItemData(selected)
            selected_data = database_templates.field_get_data(selected_id)
            if not selected_data:
                return False
            
            self.scrolled_panel.Freeze()
            self.field_bbar.EnableButton(ID_FIELD_DELETE, True)
            fieldKind = self.fieldList.GetItemText(selected, 1)
            self.fieldEdBox.Clear(True)
            
            self.fieldEdBox.AddSpacer(self.border)
            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(self.scrolled_panel, -1, "Etiqueta", size=(self.label_size, 15)),
                0,
                wx.EXPAND|wx.TOP, 
                5
            )
            self.fields['label'] = PlaceholderTextCtrl.PlaceholderTextCtrl(
                self.scrolled_panel, 
                value = selected_data['label'],
                placeholder = "Etiqueta del campo (obligatoria)"
            )
            box.Add(self.fields['label'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)
            
            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(self.scrolled_panel, -1, "Ancho", size=(self.label_size, 15)),
                0,
                wx.EXPAND|wx.TOP, 
                5
            )
            self.fields['width'] = PlaceholderTextCtrl.PlaceholderTextCtrl(
                self.scrolled_panel, 
                value = selected_data['field_data'].get("width", None) or "",
                placeholder = "Ancho del control (vacío para automático)"
            )
            box.Add(self.fields['width'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)
            
            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(self.scrolled_panel, -1, "Obligatorio", size=(self.label_size, 15)),
                0,
                wx.EXPAND
            )
            self.fields['required'] = wx.CheckBox(self.scrolled_panel, id=wx.ID_ANY)
            self.fields['required'].SetValue(
                strToValue.strToValue(
                    selected_data['field_data'].get("required", "false"), "bool"
                )
            )
            self.fields['required'].SetToolTip("Marca el campo como obligatorio para poder guardar el componente")
            box.Add(self.fields['required'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)
            
            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(self.scrolled_panel, -1, "Mostrar en nombre", size=(self.label_size, 15)),
                0,
                wx.EXPAND
            )
            self.fields['in_name'] = wx.CheckBox(self.scrolled_panel, id=wx.ID_ANY)
            self.fields['in_name'].SetValue(
                strToValue.strToValue(
                    selected_data['field_data'].get("show_in_name", "false"), "bool"
                )
            )
            self.fields['in_name'].SetToolTip("Mostrar este campo en el nombre de componente que se generará")
            box.Add(self.fields['in_name'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)
            
            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(self.scrolled_panel, -1, "Mostrar etiqueta", size=(self.label_size, 15)),
                0,
                wx.EXPAND
            )
            self.fields['show_label'] = wx.CheckBox(self.scrolled_panel, id=wx.ID_ANY)
            self.fields['show_label'].SetValue(
                strToValue.strToValue(
                    selected_data['field_data'].get("show_label", "false"), "bool"
                )
            )
            self.fields['show_label'].SetToolTip("Mostrar etiqueta al añadir componente")
            box.Add(self.fields['show_label'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)
            
            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(self.scrolled_panel, -1, "Fusión con anterior", size=(self.label_size, 15)),
                0,
                wx.EXPAND
            )
            self.fields['join_previous'] = wx.CheckBox(self.scrolled_panel, id=wx.ID_ANY)
            self.fields['join_previous'].SetValue(
                strToValue.strToValue(
                    selected_data['field_data'].get("join_previous", "false"), "bool"
                )
            )
            self.fields['join_previous'].SetToolTip("Este campo se muestra en la misma línea que el anterior en la pantalla de añadir componente")
            box.Add(self.fields['join_previous'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)
            
            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(self.scrolled_panel, -1, "Sin espacio", size=(self.label_size, 15)),
                0,
                wx.EXPAND
            )
            self.fields['no_space'] = wx.CheckBox(self.scrolled_panel, id=wx.ID_ANY)
            self.fields['no_space'].SetValue(
                strToValue.strToValue(
                    selected_data['field_data'].get("no_space", "false"), "bool"
                )
            )
            self.fields['no_space'].SetToolTip("El texto de este campo se unirá con el texto del campo anterior sin dejar espacio entre ellos, al ser mostradoe en el nombre, ventana de detalles o similar")
            box.Add(self.fields['no_space'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)
            
            if fieldKind.lower() == "input":
                box = wx.BoxSizer(wx.HORIZONTAL)
                box.AddSpacer(self.border)
                box.Add(
                    wx.StaticText(self.scrolled_panel, -1, "Default", size=(self.label_size, 15)),
                    0,
                    wx.EXPAND
                )
                self.fields['default'] = PlaceholderTextCtrl.PlaceholderTextCtrl(
                    self.scrolled_panel, 
                    value = selected_data['field_data'].get("default", ""),
                    placeholder = "Texto por defecto del campo"
                )
                self.fields['default'].SetToolTip("Indica el valor por defeco de este campo")
                box.Add(self.fields['default'], -1, wx.EXPAND)
                box.AddSpacer(self.border)
                self.fieldEdBox.Add(box, 0, wx.EXPAND)
                self.fieldEdBox.AddSpacer(self.between_items)
            elif fieldKind.lower() == "checkbox":
                box = wx.BoxSizer(wx.HORIZONTAL)
                box.AddSpacer(self.border)
                box.Add(
                    wx.StaticText(self.scrolled_panel, -1, "Default", size=(self.label_size, 15)),
                    0,
                    wx.EXPAND
                )
                self.fields['default'] = wx.CheckBox(self.scrolled_panel, id=wx.ID_ANY)
                self.fields['no_space'].SetValue(
                    strToValue.strToValue(
                        selected_data['field_data'].get("no_space", "false"), "bool"
                    )
                )
                self.fields['default'].SetToolTip("Indica el valor por defeco de este campo")
                box.Add(self.fields['default'], -1, wx.EXPAND)
                box.AddSpacer(self.border)
                self.fieldEdBox.Add(box, 0, wx.EXPAND)
                self.fieldEdBox.AddSpacer(self.between_items)
            elif fieldKind.lower() == "combobox":
                box = wx.BoxSizer(wx.HORIZONTAL)
                box.AddSpacer(self.border)
                box.Add(
                    wx.StaticText(self.scrolled_panel, -1, "Items", size=(self.label_size, 15)),
                    0,
                    wx.EXPAND|wx.TOP, 
                    5
                )
                box2 = wx.BoxSizer(wx.VERTICAL)
                box2.Add(
                    wx.RadioButton(
                        self.scrolled_panel, 
                        -1, 
                        "Seleccionar desde plantilla",
                        style = wx.RB_GROUP
                    ), 
                    0, 
                    wx.EXPAND
                )
                box2.AddSpacer(self.between_items)
                self.fields['from_template'] = wx.ComboBox(
                    self.scrolled_panel, 
                    choices = [
                        "JPEG (Menor tamaño)",
                        "PNG",
                        "BMP",
                        "TIFF (Mayor tamaño)"
                    ],
                    style=wx.CB_READONLY|wx.CB_DROPDOWN
                )
                box2.Add(self.fields['from_template'], 0, wx.EXPAND)
                box2.AddSpacer(self.between_items)
                box2.Add(
                    wx.RadioButton(
                        self.scrolled_panel, 
                        -1, 
                        "Generar manualmente"
                    ), 
                    0, 
                    wx.EXPAND
                )
                box2.AddSpacer(self.between_items)
                self.fields['items'] = PlaceholderTextCtrl.PlaceholderTextCtrl(
                    self.scrolled_panel, 
                    value = "",
                    placeholder = "Cada línea es un ítem",
                    size = (-1, 100),
                    style = 0|wx.TE_MULTILINE
                )
                box2.Add(self.fields['items'], 0, wx.EXPAND)
                box.Add(box2, -1, wx.EXPAND)
                box.AddSpacer(self.border)
                self.fieldEdBox.Add(box, 0, wx.EXPAND)
                self.fieldEdBox.AddSpacer(self.between_items)
                
                box = wx.BoxSizer(wx.HORIZONTAL)
                box.AddSpacer(self.border)
                box.Add(
                    wx.StaticText(self.scrolled_panel, -1, "Default", size=(self.label_size, 15)),
                    0,
                    wx.EXPAND
                )
                self.fields['default'] = wx.ComboBox(
                    self.scrolled_panel, 
                    choices = [
                        "JPEG (Menor tamaño)",
                        "PNG",
                        "BMP",
                        "TIFF (Mayor tamaño)"
                    ],
                    style=wx.CB_READONLY|wx.CB_DROPDOWN
                )
                self.fields['default'].SetToolTip("Indica el valor por defeco de este campo")
                box.Add(self.fields['default'], -1, wx.EXPAND)
                box.AddSpacer(self.border)
                self.fieldEdBox.Add(box, 0, wx.EXPAND)
                self.fieldEdBox.AddSpacer(self.between_items)
                
                box = wx.BoxSizer(wx.HORIZONTAL)
                box.AddSpacer(self.border)
                box.Add(
                    wx.StaticText(self.scrolled_panel, -1, "Ordenar", size=(self.label_size, 15)),
                    0,
                    wx.EXPAND
                )
                self.fields['ordered'] = wx.CheckBox(self.scrolled_panel, id=wx.ID_ANY)
                self.fields['ordered'].SetValue(
                    strToValue.strToValue(
                        selected_data['field_data'].get("ordered", "false"), "bool"
                    )
                )
                self.fields['ordered'].SetToolTip("Ordenar los items del combobox por orden alfabético")
                box.Add(self.fields['ordered'], -1, wx.EXPAND)
                box.AddSpacer(self.border)
                self.fieldEdBox.Add(box, 0, wx.EXPAND)
                self.fieldEdBox.AddSpacer(self.between_items)
            
            # Buttons
            btn_sizer =  wx.BoxSizer(wx.HORIZONTAL)
            btn_add = wx.Button(self.scrolled_panel, label="Guardar")
            btn_add.Bind(wx.EVT_BUTTON, self._fielfDataSave)
            btn_cancel = wx.Button(self.scrolled_panel, label="Reiniciar")
            btn_cancel.Bind(wx.EVT_BUTTON, self._fieldPanelUpdate)
            btn_sizer.AddSpacer(10)
            btn_sizer.Add(btn_add)
            btn_sizer.AddSpacer(30)
            btn_sizer.Add(btn_cancel)
            btn_sizer.AddSpacer(10)
            self.fieldEdBox.Add(btn_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)
            # Draw the panel
            self.scrolled_panel.Layout()
            self.scrolled_panel.Thaw()
            self.scrolled_panel.SetupScrolling()
        else:
            self.field_bbar.EnableButton(ID_FIELD_DELETE, False)
    
    
    ###=== Main Function ===###
    def __init__(self):
        wx.Frame.__init__(
            self,
            None,
            title="Gestión de Plantillas",
            size=(900, 900),
            style=wx.DEFAULT_FRAME_STYLE
        )

        # Changing the icon
        icon = wx.Icon(
            getResourcePath.getResourcePath(globals.config["folders"]["images"], 'icon.ico'), 
            wx.BITMAP_TYPE_ICO
        )
        self.SetIcon(icon)

        log.info("Loading main windows...")
        self.Bind(wx.EVT_CLOSE, self.exitGUI)

        # Variables
        self.timer = None
        self.last_filter = None
        self.last_selected_item = None
        self.field_kind = [
            "CheckBox",
            "ComboBox",
            "Input"
        ]
        self.fields = {}
        self.border = 20
        self.between_items = 5
        self.label_size = 130
        self.modified = False

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
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'add_cat.png'
            )
        )
        self.cat_bbar.AddSimpleButton(
            ID_CAT_ADD, 
            "Añadir Categoría", 
            image, 
            'Añade una categoría raíz nueva'
        )
        # Add SubCategory
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'add_subcat.png'
            )
        )
        self.cat_bbar.AddSimpleButton(
            ID_CAT_ADDSUB,
            "Añadir Subcategoría", 
            image, 
            'Añade una subcategoría a una categoría principal'
        )
        # Change Name
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'ren_cat.png'
            )
        )
        self.cat_bbar.AddSimpleButton(
            ID_CAT_RENAME, 
            "Renombrar", 
            image, 
            'Cambia el nombre de una categoría o una subcategoría'
        )
        # Delete category
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'del_cat.png'
            )
        )
        self.cat_bbar.AddSimpleButton(
            ID_CAT_DELETE, 
            "Eliminar", 
            image, 
            'Elimina una categoría o subcategoría, incluyendo todas las subcategorías y componentes que hay en ella'
        )
        
        ##--------------------##
        ### Panel Templates ###
        pTem = RB.RibbonPanel(page, wx.ID_ANY, "Plantillas")
        self.tem_bbar = RB.RibbonButtonBar(pTem)
        # Add Category
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'template_add.png'
            )
        )
        self.tem_bbar.AddSimpleButton(
            ID_TEM_ADD, 
            "Añadir", 
            image, 
            'Añade una plantilla vacía nueva'
        )
        # Change template name
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'template_ren.png'
            )
        )
        self.tem_bbar.AddSimpleButton(
            ID_TEM_RENAME, 
            "Renombrar", 
            image, 
            'Cambia el nombre de una plantilla'
        )
        # Delete template
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'template_del.png'
            )
        )
        self.tem_bbar.AddSimpleButton(
            ID_TEM_DELETE, 
            "Eliminar", 
            image, 
            'Elimina una plantilla, incluyendo todos los grupos y campos que hay en ella'
        )
        
        ##--------------------##
        ### Panel Items field ###
        pFields = RB.RibbonPanel(page, wx.ID_ANY, "Campos")
        self.field_bbar = RB.RibbonButtonBar(pFields)
        # Add field
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'field_add.png'
            )
        )
        self.field_bbar.AddSimpleButton(
            ID_FIELD_ADD, 
            "Añadir", 
            image, 
            'Añade un campos básico'
        )
        # Delete field
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'field_del.png'
            )
        )
        self.field_bbar.AddSimpleButton(
            ID_FIELD_DELETE, 
            "Eliminar", 
            image, 
            'Elimina un campo'
        )

        # Eventos al pulsar botones
        self.cat_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._category_create, id=ID_CAT_ADD)
        self.cat_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._subcat_create, id=ID_CAT_ADDSUB)
        self.cat_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._category_rename, id=ID_CAT_RENAME)
        self.cat_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._category_delete, id=ID_CAT_DELETE)
        self.tem_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._template_create, id=ID_TEM_ADD)
        self.tem_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._template_rename, id=ID_TEM_RENAME)
        self.tem_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._template_delete, id=ID_TEM_DELETE)
        self.field_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._field_create, id=ID_FIELD_ADD)
        self.field_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._field_delete, id=ID_FIELD_DELETE)

        self.cat_bbar.EnableButton(ID_CAT_ADDSUB, False)
        self.cat_bbar.EnableButton(ID_CAT_RENAME, False)
        self.cat_bbar.EnableButton(ID_CAT_DELETE, False)
        self.tem_bbar.EnableButton(ID_TEM_ADD, False)
        self.tem_bbar.EnableButton(ID_TEM_RENAME, False)
        self.tem_bbar.EnableButton(ID_TEM_DELETE, False)
        self.field_bbar.EnableButton(ID_FIELD_ADD, False)
        self.field_bbar.EnableButton(ID_FIELD_DELETE, False)

        # Pintar Ribbon
        ribbon.Realize()

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(ribbon, 0, wx.EXPAND)
        vsizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(vsizer)

        # Left Panel
        lPan = wx.Panel(splitter, style=wx.RAISED_BORDER)
        lPanBox = wx.BoxSizer(wx.VERTICAL)
        # Search TextBox
        self.search = self.search = wx.SearchCtrl(lPan, style=wx.TE_PROCESS_ENTER|wx.RAISED_BORDER)
        self.search.ShowCancelButton(True)
        self.search.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self._searchText)
        self.search.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self._cancelSearch)
        self.search.Bind(wx.EVT_TEXT_ENTER, self._searchText)

        lPanBox.Add(self.search, 0, wx.EXPAND)

        # Templates Tree
        self.tree = CTreeCtrl.CTreeCtrl(lPan, wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._tree_selection, id=1)
        self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self._tree_drag_start)
        self.tree.Bind(wx.EVT_TREE_END_DRAG, self._tree_drag_end)
        self.tree_root = self.tree.AddRoot('Categorias')
        self.tree_imagelist = wx.ImageList(16, 16)
        self.tree.AssignImageList(self.tree_imagelist)
        lPanBox.Add(self.tree, 1, wx.EXPAND)
        lPan.SetSizer(lPanBox) 
        #ImageList Images
        for imageFN in [
          "folder_closed.png",
          "folder_open.png",
          "template.png"
        ]:
            log.debug("Load tree image {}".format(imageFN))
            image = wx.Bitmap()
            image.LoadFile(
                getResourcePath.getResourcePath(
                    globals.config["folders"]["images"], 
                    imageFN
                )
            )
            self.tree_imagelist.Add(image)

        # Right Splitter
        rPan = wx.SplitterWindow(splitter, -1, style=wx.RAISED_BORDER)

        # Window Splitter
        splitter.SplitVertically(lPan, rPan)
        splitter.SetSashGravity(0.5)

        fieldLstPanel = wx.Panel(rPan)
        fieldLstBox = wx.BoxSizer(wx.VERTICAL)
        fieldLstPanel.SetSizer(fieldLstBox)
        self.scrolled_panel = scrolled.ScrolledPanel(rPan, style=wx.RAISED_BORDER)
        self.fieldEdBox = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_panel.SetSizer(self.fieldEdBox)
        
        self.fieldList = wx.ListCtrl(
            fieldLstPanel, 
            id=wx.ID_ANY,
            style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES
        )
        fieldLstBox.Add(self.fieldList, 1, wx.EXPAND)
        self.fieldList.AppendColumn("Etiqueta", wx.LIST_FORMAT_CENTRE, 262)
        self.fieldList.AppendColumn("Tipo", wx.LIST_FORMAT_CENTRE)
        self.fieldList.AppendColumn("Ancho", wx.LIST_FORMAT_CENTRE)
        self.fieldList.Bind(wx.EVT_LIST_ITEM_SELECTED, self._fieldPanelUpdate)
        self.fieldList.Disable()
        
        label = wx.StaticText(
            self.scrolled_panel,
            id=wx.ID_ANY,
            label="Debe seleccionar un grupo para ver los campos en el panel superior\n y seleccionar uno de esos campos para poder verlo/editarlo en este panel",
            style=wx.ALIGN_CENTER
        )
        
        self.fieldEdBox.Add(label, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        
        
        rPan.SplitHorizontally(fieldLstPanel, self.scrolled_panel)
        rPan.SetSashGravity(0.4)

        # Updating tree
        self._tree_filter()


#======================
# Start GUI
#======================
manageTemplates().Show()
app.MainLoop()

