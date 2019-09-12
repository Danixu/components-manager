#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
27 May 2019
@autor: Daniel Carrasco
'''

from logging import getLogger, FileHandler, Formatter, DEBUG
from os import path, startfile
import sys
import wx
import wx.lib.agw.ribbon as RB
import wx.html2
from widgets import ShapedButton, PlaceholderTextCtrl
from modules import getResourcePath, compressionTools
from modules_local import addComponentWindow, manageAttachments, CTreeCtrl, setDefaultTemplate, options, manageTemplates
import globals
from plugins.database.sqlite import dbase
from io import BytesIO
#from threading import Timer

global rootPath
if getattr(sys, 'frozen', False):
    # The application is frozen
    rootPath = path.dirname(path.realpath(sys.executable))
else:
    # The application is not frozen
    # Change this bit to match where you store your data files:
    rootPath = path.dirname(path.realpath(__file__))

# Load main data
app = wx.App()
globals.init()

# ID de los botones
ID_CAT_ADD = wx.ID_HIGHEST + 1
ID_CAT_ADDSUB = ID_CAT_ADD + 1
ID_CAT_RENAME = ID_CAT_ADDSUB + 1
ID_CAT_DELETE = ID_CAT_RENAME + 1
ID_CAT_TEM_SET = ID_CAT_DELETE + 1
ID_COM_ADD = ID_CAT_TEM_SET + 1
ID_COM_DEL = ID_COM_ADD + 1
ID_COM_ED = ID_COM_DEL + 1
ID_IMG_ADD = ID_COM_ED + 1
ID_IMG_DEL = ID_IMG_ADD + 1
ID_DS_ADD = ID_IMG_DEL + 1
ID_DS_VIEW = ID_DS_ADD + 1
ID_TOOLS_OPTIONS = ID_DS_VIEW + 1
ID_TOOLS_MANAGE_TEMPLATES =  ID_TOOLS_OPTIONS + 1
ID_TOOLS_VACUUM = ID_TOOLS_MANAGE_TEMPLATES + 1


########################################################################
########################################################################
########################################################################
class mainWindow(wx.Frame):
    ###=== Exit Function ===###
    def exitGUI(self, event):
        if self.IsMaximized():
            globals.config["main_window"]["maximized"] = 1
        else:
            globals.config["main_window"]["maximized"] = 0

        if not options.options(self)._save('config.ini', globals.config):
            dlg = wx.MessageDialog(
                None, 
                "Ocurrió un error al guardar la configuración.",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()

        # Avoid slow close by deleting tree items
        self.tree.Freeze()
        self.Destroy()


    def _category_create(self, event):
      dlg = wx.TextEntryDialog(self, 'Nombre de la catergoría', 'Añadir categoría')
      dlg.SetValue("")
      if dlg.ShowModal() == wx.ID_OK:
          try:
              category_id = self.database_comp.category_add(dlg.GetValue())
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
                      }
                  )
                  self.tree.SortChildren(self.tree_root)
                  #self._tree_filter()
                  self.log.debug("Category {} added correctly".format(dlg.GetValue()))
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
                category_id = self.database_comp.category_add(dlg.GetValue(), itemData["id"])
                if category_id:
                    newID = category_id[0]
                    self.tree.AppendItem(
                        self.tree.GetSelection(), 
                        dlg.GetValue(), 
                        image=0, 
                        selImage= 1, 
                        data={
                          "id": newID,
                          "cat": True,
                        }
                    )
                    self.tree.SortChildren(self.tree.GetSelection())
                    if not self.tree.IsExpanded(self.tree.GetSelection()):
                        self.tree.Expand(self.tree.GetSelection())
                    self.log.debug("Subcategory {} added correctly".format(dlg.GetValue()))
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
                self.log.error(
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
          self.database_comp.category_rename(dlg.GetValue(), itemData["id"])
          itemNewName = self.database_comp.component_data(itemData["id"])
          self.tree.SetItemText(self.tree.GetSelection(), itemNewName)
          self.log.debug("Category {} renamed to {} correctly".format(itemName, itemNewName))

        except Exception as e:
          self.log.error("Error renaming {} to {}.".format(itemName, dlg.GetValue()))

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
            if self.database_comp.category_delete(itemData["id"]):
                self.tree.Delete(self.tree.GetSelection())
                self._tree_selection(None)
                self.log.debug("Category {} deleted correctly".format(itemName))
            else:
                print("There was an error deleting the category")
                return


        dlg.Destroy()
        #self._tree_filter()


    def _component_add(self, event):
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        template = self.database_comp.query("SELECT Template FROM Categories WHERE ID = ?;", (itemData['id'], ))
        component_frame = addComponentWindow.addComponentWindow(self, default_template = template[0][0])
        #component_frame.MakeModal(true);
        component_frame.ShowModal()
        if component_frame.component_id:
            self.tree.AppendItem(
                self.tree.GetSelection(), 
                self.database_comp.component_data(
                    component_frame.component_id
                )['name'],
                image=2, 
                selImage= 3,
                data={
                  "id": component_frame.component_id,
                  "cat": False,
                }
            )
            self.tree.SortChildren(self.tree.GetSelection())
            if not self.tree.IsExpanded(self.tree.GetSelection()):
                self.tree.Expand(self.tree.GetSelection())
        elif not component_frame.closed:
            self.log.error(
                "There was an error creating the component"
            )
            dlg = wx.MessageDialog(
                None, 
                "Error creando el componente",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return
        component_frame.Destroy()


    def _component_edit(self, event):
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        component_frame = addComponentWindow.addComponentWindow(self, itemData["id"])

        component_frame.ShowModal()

        if not component_frame.closed:
            itemNewName = self.database_comp.component_data(itemData["id"])
            self.tree.SetItemText(self.tree.GetSelection(), itemNewName['name'])
            self.tree.SortChildren(self.tree.GetSelection())
            if not self.tree.IsExpanded(self.tree.GetSelection()):
                self.tree.Expand(self.tree.GetSelection())

            self._tree_selection(None)
            component_frame.Destroy()


    def _component_delete(self, event):
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
                if self.database_comp.query("DELETE FROM Components WHERE ID = ?;", (itemData["id"], )) != None:
                    self.log.debug("Commiting changes...")
                    self.database_comp.conn.commit()
                    self.tree.Delete(self.tree.GetSelection())
                    self.log.debug("Component id {} deleted correctly".format(itemData["id"]))
                    self._tree_selection(None)
                else:
                    self.log.error("There was an error deleting the component")
                    return

            except:
                self.log.error("There was an error deleting the component.")
                dlg = wx.MessageDialog(
                    None, 
                    "There was an error deleting the component: {}".format(itemName),
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()


    def _set_default_template(self, event):
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        component_frame = setDefaultTemplate.setDefaultTemplate(self)
        component_frame.ShowModal()

    def _attachments_manage(self, event):
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        component_frame = manageAttachments.manageAttachments(self.database_comp, self, itemData.get('id'))
        component_frame.ShowModal()
        component_frame.Destroy()
        self._tree_selection(None)


    def _datasheet_view(self, event):
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        componentID = itemData['id']

        tempFile = self.database_comp.datasheet_view(itemData.get('id'))
        if tempFile:
            startfile(tempFile) 
        else:
            dlg = wx.MessageDialog(
                None, 
                "Ocurrió un error al abrir el datasheet",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()


    def _image_add(self, event):
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        # otherwise ask the user what new file to open
        with wx.FileDialog(
            self, 
            "Abrir fichero de imagen", 
            wildcard="Imágenes (*.jpg, *.jpeg, *.png, *.gif, *.bmp)|*.jpg;*.jpeg;*.png;*.gif;*.bmp|Todos los ficheros (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            size = (
                (globals.config["images"]["size"] + 1) * 100,
                (globals.config["images"]["size"] + 1) * 100
            )
            format = wx.BITMAP_TYPE_PNG
            if globals.config["images"]["format"] == 0:
                format = wx.BITMAP_TYPE_JPEG
            elif globals.config["images"]["format"] == 1:
                format = wx.BITMAP_TYPE_PNG
            elif globals.config["images"]["format"] == 1:
                format = wx.BITMAP_TYPE_BMP
            elif globals.config["images"]["format"] == 1:
                format = wx.BITMAP_TYPE_TIFF

            quality = None
            if globals.config["images"]["format"] == 0:
                quality = globals.config["images"]["jpeg_quality"]
            elif globals.config["images"]["format"] == 1:
                quality = globals.config["images"]["png_compression"]

            image = self.database_comp.image_add(
                fileDialog.GetPath(), 
                size, 
                itemData.get('id'), 
                itemData.get('cat'),
                format,
                quality,
                globals.config["images"]["compression"]
            )
            if image:
                self._tree_selection(None)
                dlg = wx.MessageDialog(
                    None, 
                    "Imagen añadida correctamente",
                    'Añadida',
                    wx.OK | wx.ICON_INFORMATION
                )
                dlg.ShowModal()
                dlg.Destroy()
            else:
                dlg = wx.MessageDialog(
                    None, 
                    "Ocurrió un error al añadir la imagen",
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()


    def _image_del(self, event):
        itemName = self.tree.GetItemText(self.tree.GetSelection())
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        imageID = self.loaded_images_id[self.actual_image]
        if not imageID:
            dlg = wx.MessageDialog(
                None, 
                "El item no tiene imagen",
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
                if self.database_comp.image_del(imageID):
                    self.log.error("Image deleted sucessfully.")
                    self._tree_selection(None)
                    dlg = wx.MessageDialog(
                        None, 
                        "Imagen eliminada correctamente",
                        'Borrada',
                        wx.OK | wx.ICON_INFORMATION
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                else:
                    self.log.error("There was an error deleting the image.")
                    dlg = wx.MessageDialog(
                        None, 
                        "Ocurrió un error al borrar la imagen",
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
            except Exception as e:
                self.log.error("There was an error deleting the image: {}.".format(e))


    def _change_image_next(self, event):
        self.actual_image += 1

        if self.actual_image == 0:
            self.button_back.Disable()
        else:
            self.button_back.Enable()

        if self.actual_image == (len(self.loaded_images)-1):
            self.button_next.Disable()
        else:
            self.button_next.Enable()

        self._onImageResize(None)

        if event:
            event.Skip()


    def _change_image_back(self, event):
        self.actual_image -= 1

        if self.actual_image == 0:
            self.button_back.Disable()
        else:
            self.button_back.Enable()

        if self.actual_image == (len(self.loaded_images)-1):
            self.button_next.Disable()
        else:
            self.button_next.Enable()

        self._onImageResize(None)

        if event:
            event.Skip()


    def _tree_filter(self, parent_item = None, category_id = -1, filter = None, expanded = False):
      if category_id == -1:
        self.tree.DeleteAllItems()

      if not parent_item:
        parent_item = self.tree_root

      cats = self.database_comp.query("SELECT * FROM Categories WHERE Parent = ? AND ID <> -1 ORDER BY Name COLLATE NOCASE ASC;", (category_id, ))
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

        child_cat = self.database_comp.query("SELECT COUNT(*) FROM Categories WHERE Parent = ?;", (item[0], ))
        child_com = self.database_comp.query("SELECT COUNT(*) FROM Components WHERE Category = ?;", (item[0], ))
        if child_cat[0][0] > 0 or child_com[0][0] > 0:
          self._tree_filter(id, item[0], filter, item[3])
        elif filter:
          self.tree.Delete(id)

      components = self.database_comp.query("SELECT ID, Template FROM Components WHERE Category = ?;", (category_id, ))
      for component in components:
        found = False if filter else True

        if filter:
            component_name = self.database_comp.component_data(component[0])['name']
            if filter.lower() in component_name.lower():
                found = True

            if not found:
                fields = self.database_comp.component_data(component[0])
                for field, field_data in fields['processed_data'].items():
                    if filter.lower() in field_data.lower():
                        found = True
                        break
        if found:
            self.tree.AppendItem(
                parent_item, 
                self.database_comp.component_data(component[0])['name'],
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
            del self.loaded_images
            del self.loaded_images_id
            self.loaded_images = []
            self.loaded_images_id = []
            self.actual_image = 0
            query = "SELECT ID, Image, Imagecompression FROM Images WHERE {} = ?;".format(
                'Category_id' if itemData.get('cat') else 'Component_id'
            )
            for item in self.database_comp.query(query, (itemData.get('id'),)):
                sbuf = BytesIO(
                    compressionTools.decompressData(item[1], item[2])
                )
                self.loaded_images.append(
                    wx.Image(sbuf)
                )
                self.loaded_images_id.append(
                    item[0]
                )
                sbuf.close()

            if len(self.loaded_images) == 0:
                self.loaded_images_id.append(None)
                self.loaded_images = [wx.Image()]
                self.loaded_images[0].LoadFile(
                    getResourcePath.getResourcePath(
                      globals.config["folders"]["images"], 
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

            if itemData.get('cat'):
                html = self.database_comp.category_data_html(itemData.get('id'))
                self.textFrame.SetPage(html, "http://localhost/")
            else:
                html = self.database_comp.component_data_html(itemData.get('id'))
                self.textFrame.SetPage(html, "http://localhost/")
            self._onImageResize(None)

        if event:
            event.Skip()

    def _tree_item_collapsed(self, event):
        if event.GetItem().IsOk():
            itemData = self.tree.GetItemData(event.GetItem())
            self.database_comp.query("UPDATE Categories SET Expanded = ? WHERE ID = ?;", (False, itemData['id']), auto_commit = True)


    def _tree_item_expanded(self, event):
        if event.GetItem().IsOk():
            itemData = self.tree.GetItemData(event.GetItem())
            self.database_comp.query("UPDATE Categories SET Expanded = ? WHERE ID = ?;", (True, itemData['id']), auto_commit = True)


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
            self.log.info("The destination is the actual parent")
            self.tree.Unselect()
            return

        if self._ItemIsChildOf(target, source):
            self.log.info("Tree item can not be moved into itself or a child!")
            self.tree.Unselect()
            return

        src_data = self.tree.GetItemData(source)
        target_data = self.tree.GetItemData(target)

        if not target_data['cat']:
            self.log.info("Destination is a component, and only categories are allowed as destination")
            return

        try:
            if src_data['cat']:
                self.database_comp.query("UPDATE Categories SET Parent = ? WHERE ID = ?;", (target_data['id'], src_data['id']))
            else:
                self.database_comp.query("UPDATE Components SET Category = ? WHERE ID = ?;", (target_data['id'], src_data['id']))

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
            self.log.debug("Checking if item {} is {}".format(itemName, itemSearchName))
            if item == searchID:
                self.log.debug("Items are equal")
                return True
            else:
                self.log.debug("Items are different")

            if self.tree.ItemHasChildren(item):
                self.log.debug("Item {} has children".format(itemName))
                if self._ItemIsChildOf(searchID, item):
                    return True

            item, cookie =  self.tree.GetNextChild(itemID, cookie)
        return False


    def _buttonBarUpdate(self, itemID):
        if not itemID.IsOk():
            self.log.warning("Tree item is not OK")
            return

        itemData = self.tree.GetItemData(itemID)

        if itemData.get("cat", False):
            self.cat_bbar.EnableButton(ID_CAT_ADDSUB, True)
            self.cat_bbar.EnableButton(ID_CAT_DELETE, True)
            self.cat_bbar.EnableButton(ID_CAT_TEM_SET, True)
            self.cat_bbar.EnableButton(ID_CAT_RENAME, True)
            self.com_bbar.EnableButton(ID_COM_ADD, True)
            self.com_bbar.EnableButton(ID_COM_DEL, False)
            self.com_bbar.EnableButton(ID_COM_ED, False)
            self.ds_bbar.EnableButton(ID_DS_ADD, False)
            self.ds_bbar.EnableButton(ID_DS_VIEW, False)
        else:
            query = "SELECT ID FROM Files WHERE Component = ?;"
            exists = self.database_comp.query(query, (itemData['id'],))
            if len(exists) > 0:
                self.ds_bbar.EnableButton(ID_DS_VIEW, True)
            else:
                self.ds_bbar.EnableButton(ID_DS_VIEW, False)

            self.cat_bbar.EnableButton(ID_CAT_ADDSUB, False)
            self.cat_bbar.EnableButton(ID_CAT_DELETE, False)
            self.cat_bbar.EnableButton(ID_CAT_TEM_SET, False)
            self.cat_bbar.EnableButton(ID_CAT_RENAME, False)
            self.com_bbar.EnableButton(ID_COM_ADD, False)
            self.com_bbar.EnableButton(ID_COM_DEL, True)
            self.com_bbar.EnableButton(ID_COM_ED, True)
            self.ds_bbar.EnableButton(ID_DS_ADD, True)

        query = "SELECT ID FROM Images WHERE {} = ?;".format(
            'Category_id' if itemData.get('cat') else 'Component_id'
        )
        exists = self.database_comp.query(query, (itemData['id'],))
        if len(exists) > 0:
            self.img_bbar.EnableButton(ID_IMG_ADD, True)
            self.img_bbar.EnableButton(ID_IMG_DEL, True)
        else:
            self.img_bbar.EnableButton(ID_IMG_ADD, True)
            self.img_bbar.EnableButton(ID_IMG_DEL, False)


    def _onImageResize(self, event):
        frame_size = self.image.GetSize()
        if frame_size[0] != 0:
          image = self.loaded_images[self.actual_image]
          bitmap = wx.Bitmap(image.Scale(frame_size[0], frame_size[0]))
          self.image.SetBitmap(bitmap)

        if event:
            event.Skip()


    #def _search(self, event):
    #    # SQLITE es threadSafe, por lo que de momento no se usa
    #    if self.timer:
    #        self.timer.cancel()

    #    searchText = self.search.GetRealValue()
    #    if len(searchText) > 3:
    #        self.timer = Timer(2, self._tree_filter, {"filter": searchText})
    #        self.timer.start()

    #    if event:
    #        event.Skip()


    def _searchText(self, event):
        searchText = self.search.GetValue()
        self.tree.Freeze()
        if len(searchText) > 2:
            self._tree_filter(filter = searchText)
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
        self.tree.Freeze()
        self._tree_filter()
        self.tree.Thaw()
        event.Skip()



    def _options(self, event):
        options_window = options.options(self)
        options_window.ShowModal()


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
                self.database_comp.vacuum()
                dlg = wx.MessageDialog(
                    None, 
                    "Optimización completa",
                    'Correcto',
                    wx.OK | wx.ICON_INFORMATION
                )
                dlg.ShowModal()
                dlg.Destroy()

        except Exception as e:
            self.log.error("There was an error optimizing the Database: {}".format(e))
            dlg = wx.MessageDialog(
                None, 
                "There was an error optimizing the Database: {}".format(e),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()


    def OnMove(self, event):
        if not self.IsMaximized():
            x, y = event.GetPosition()
            globals.config["main_window"]["pos_x"] = x
            globals.config["main_window"]["pos_y"] = y
        event.Skip()

    def OnSize(self, event):
        if not self.IsMaximized():
            w, h = event.GetSize()
            globals.config["main_window"]["size_w"] = w
            globals.config["main_window"]["size_h"] = h
        event.Skip()


    def _templates_manager(self, event):
        templates_manager = manageTemplates.manageTemplates(self)
        templates_manager.ShowModal()


    ###=== Main Function ===###
    def __init__(self):
        WindowStyle = wx.DEFAULT_FRAME_STYLE
        if globals.config["main_window"]["maximized"]:
            WindowStyle = wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE
        wx.Frame.__init__(
            self,
            None,
            title="Components Manager",
            size = (
                globals.config["main_window"]["size_w"],
                globals.config["main_window"]["size_h"]
            ),
            pos = (
                globals.config["main_window"]["pos_x"],
                globals.config["main_window"]["pos_y"]
            ),
            style=WindowStyle
        )

        # Changing the icon
        icon = wx.Icon(
            getResourcePath.getResourcePath(globals.config["folders"]["images"], 'icon.ico'), 
            wx.BITMAP_TYPE_ICO
        )
        self.SetIcon(icon)
        
        ### Log Configuration ###
        self.log = getLogger()
        self.log.setLevel(DEBUG)
        # create a file handler
        handler = FileHandler(globals.options['logFile'], 'a+', 'utf-8')
        # create a logging format
        formatter = Formatter(
            '%(asctime)s - %(funcName)s() - %(levelname)s: %(message)s'
        )
        handler.setFormatter(formatter)
        # add the handlers to the logger
        self.log.addHandler(handler)
        self.log.debug("Changing log level to {}".format(globals.options['logLevel']))
        self.log.setLevel(globals.options['logLevel'])

        self.log.info("Loading main windows...")
        self.Bind(wx.EVT_CLOSE, self.exitGUI)
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Variables
        self.actual_image = 0
        self.loaded_images_id = [None]
        self.loaded_images = [wx.Image()]
        self.loaded_images[0].LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'no_image.png'
            )
        )
        self.timer = None
        self.last_filter = None
        self.last_selected_item = None
        self.database_comp = dbase(
            "{}/{}".format(
                rootPath, 
                "database.sqlite3"
            ), 
            auto_commit = False,
            parent = self
        )
        self.database_temp = dbase(
            "{}/{}".format(
                globals.rootPath, 
                "templates.sqlite3"
            ), 
            auto_commit = False, 
            templates = True,
            parent = self
        )

        # Creating splitter
        self.log.debug("Creating splitter")
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
            "Cambiar Nombre", 
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
        # Set Default Template
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'template_set.png'
            )
        )
        self.cat_bbar.AddSimpleButton(
            ID_CAT_TEM_SET, 
            "Plantilla por defecto", 
            image, 
            'Indica la plantilla por defecto que se abrirá al añadir un componente'
        )

        ##---------------------##
        ### Panel Componentes ###
        pCom = RB.RibbonPanel(page, wx.ID_ANY, "Componentes")
        self.com_bbar = RB.RibbonButtonBar(pCom)
        # Add Component
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'add_com.png'
            )
        )
        self.com_bbar.AddSimpleButton(
            ID_COM_ADD, 
            "Añadir", 
            image, 
            'Añade un componente nuevo'
        )
        # Edit Component
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'edit_com.png'
            )
        )
        self.com_bbar.AddSimpleButton(
            ID_COM_ED, 
            "Editar", 
            image, 
            'Edita el componente seleccionado'
        )
        # Delete Component
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'del_com.png'
            )
        )
        self.com_bbar.AddSimpleButton(
            ID_COM_DEL, 
            "Eliminar", 
            image, 
            'Elimina el componente seleccionado'
        )

        ##------------------##
        ### Panel Imágenes ###
        pImg = RB.RibbonPanel(
            page, 
            wx.ID_ANY, 
            "Imágenes"
        )
        self.img_bbar = RB.RibbonButtonBar(pImg)
        # Add Image
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'add_image.png'
            )
        )
        self.img_bbar.AddSimpleButton(
            ID_IMG_ADD, 
            "Añadir", 
            image, 
            'Añade una imagen a la categoría o componente'
        )
        # Delete Image
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'del_image.png'
            )
        )
        self.img_bbar.AddSimpleButton(
            ID_IMG_DEL, 
            "Eliminar",
            image, 
            'Elimina la imagen actual'
        )

        ##------------------##
        ### Barra Ficheros ###
        pDS = RB.RibbonPanel(page, wx.ID_ANY, "Ficheros Adjuntos")
        self.ds_bbar = RB.RibbonButtonBar(pDS)
        # Manage files
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'manage_files.png'
            )
        )
        self.ds_bbar.AddSimpleButton(ID_DS_ADD, "Gestionar", image, '')
        # View Datasheet
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'view_datasheet.png'
            )
        )
        self.ds_bbar.AddSimpleButton(ID_DS_VIEW, "Ver Datasheet", image, '')

        ##------------------##
        ### Barra Herramientas ###
        pDS = RB.RibbonPanel(page, wx.ID_ANY, "Herramientas")
        self.tools_bbar = RB.RibbonButtonBar(pDS)
        # Options
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'options.png'
            )
        )
        self.tools_bbar.AddSimpleButton(ID_TOOLS_OPTIONS, "Opciones", image, '')
        # Manage Templates
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'template_manage.png'
            )
        )
        self.tools_bbar.AddSimpleButton(ID_TOOLS_MANAGE_TEMPLATES, "Gestionar Plantillas", image, '')
        # Opitimize Database
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'db_optimize.png'
            )
        )
        self.tools_bbar.AddSimpleButton(ID_TOOLS_VACUUM, "Optimizar BBDD", image, '')

        # Eventos al pulsar botones
        self.cat_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._category_create, id=ID_CAT_ADD)
        self.cat_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._subcat_create, id=ID_CAT_ADDSUB)
        self.cat_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._category_rename, id=ID_CAT_RENAME)
        self.cat_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._category_delete, id=ID_CAT_DELETE)
        self.cat_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._set_default_template, id=ID_CAT_TEM_SET)
        self.com_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._component_add, id=ID_COM_ADD)
        self.com_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._component_edit, id=ID_COM_ED)
        self.com_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._component_delete, id=ID_COM_DEL)
        self.img_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._image_add, id=ID_IMG_ADD)
        self.img_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._image_del, id=ID_IMG_DEL)
        self.ds_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._attachments_manage, id=ID_DS_ADD)
        self.ds_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._datasheet_view, id=ID_DS_VIEW)
        self.tools_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._options, id=ID_TOOLS_OPTIONS)
        self.tools_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._templates_manager, id=ID_TOOLS_MANAGE_TEMPLATES)
        self.tools_bbar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self._vacuum, id=ID_TOOLS_VACUUM)

        self.cat_bbar.EnableButton(ID_CAT_ADDSUB, False)
        self.cat_bbar.EnableButton(ID_CAT_RENAME, False)
        self.cat_bbar.EnableButton(ID_CAT_DELETE, False)
        self.cat_bbar.EnableButton(ID_CAT_TEM_SET, False)
        self.com_bbar.EnableButton(ID_COM_ADD, False)
        self.com_bbar.EnableButton(ID_COM_DEL, False)
        self.com_bbar.EnableButton(ID_COM_ED, False)
        self.img_bbar.EnableButton(ID_IMG_ADD, False)
        self.img_bbar.EnableButton(ID_IMG_DEL, False)
        self.ds_bbar.EnableButton(ID_DS_ADD, False)
        self.ds_bbar.EnableButton(ID_DS_VIEW, False)

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
        #self.search.Bind(wx.EVT_TEXT, self._search)
        #self.search.Bind(wx.EVT_TEXT_ENTER, self._searchText)
        # Components Tree
        self.tree = CTreeCtrl.CTreeCtrl(lPan)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._tree_selection, id=1)
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
          self.log.debug("Load tree image {}".format(imageFN))
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

        imageSizer = wx.BoxSizer(wx.HORIZONTAL)
        imageFrame = wx.Panel(rPan, style=wx.RAISED_BORDER)

        ### Image Frame ###
        # Back Button
        button_back_up = wx.Bitmap()
        button_back_up.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'button_back_up.png'
            )
        )
        button_back_down = wx.Bitmap()
        button_back_down.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'button_back_down.png'
            )
        )
        button_back_disabled = button_back_down.ConvertToDisabled()
        button_back_over = wx.Bitmap()
        button_back_over.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'button_back_over.png'
            )
        )
        self.button_back = ShapedButton.ShapedButton(imageFrame, 
            button_back_up,
            button_back_down, 
            button_back_disabled,
            button_back_over,
            size=(36,36)
        )
        self.button_back.Bind(wx.EVT_LEFT_UP, self._change_image_back)

        # Next Button
        button_next_up = wx.Bitmap()
        button_next_up.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'button_next_up.png'
            )
        )

        button_next_down = wx.Bitmap()
        button_next_down.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'button_next_down.png'
            )
        )
        button_next_disabled = button_next_up.ConvertToDisabled()
        button_next_over = wx.Bitmap()
        button_next_over.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"], 
              'button_next_over.png'
            )
        )
        self.button_next = ShapedButton.ShapedButton(imageFrame, 
            button_next_up,
            button_next_down, 
            button_next_disabled,
            button_next_over,
            size=(36,36)
        )
        self.button_next.Bind(wx.EVT_LEFT_UP, self._change_image_next)

        # Image Box
        self.image = wx.StaticBitmap(imageFrame, wx.ID_ANY, self.loaded_images[self.actual_image].ConvertToBitmap(), style=wx.RAISED_BORDER)
        #self.image.SetScaleMode(wx.Scale_AspectFit) # No implementado en el módulo
        self.image.Bind(wx.EVT_SIZE, self._onImageResize)
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
        self._tree_filter()


#======================
# Start GUI
#======================
mainWindow().Show()
app.MainLoop()

