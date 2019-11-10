#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
27 May 2019
@autor: Daniel Carrasco
'''

from logging import getLogger, FileHandler, Formatter, DEBUG
from os import path
from modules_local.startfile import open_file as startfile
from io import BytesIO
from tempfile import _get_candidate_names, _get_default_tempdir
from hashlib import sha256, sha512
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import sys
import wx
import wx.lib.agw.ribbon as RB
from wx.grid import Grid

from widgets import ShapedButton
from modules import getResourcePath, compressionTools, crypto
from modules_local import (
    addComponentWindow,
    manageAttachments,
    CTreeCtrl,
    setDefaultTemplate,
    options,
    manageTemplates
)
import globals
from plugins.database.sqlite import dbase
from plugins.database.mysql import dbase as MySQL

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
ID_STOCK_ADD = ID_COM_ED + 1
ID_STOCK_REM = ID_STOCK_ADD + 1
ID_DS_ADD = ID_STOCK_REM + 1
ID_DS_VIEW = ID_DS_ADD + 1
ID_TOOLS_OPTIONS = ID_DS_VIEW + 1
ID_TOOLS_MANAGE_TEMPLATES = ID_TOOLS_OPTIONS + 1
ID_TOOLS_VACUUM = ID_TOOLS_MANAGE_TEMPLATES + 1


########################################################################
########################################################################
########################################################################
class mainWindow(wx.Frame):
    # ##=== Exit Function ===## #
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
        dlg = wx.TextEntryDialog(
            self,
            'Nombre de la catergoría',
            'Añadir categoría'
        )
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
                        selImage=1,
                        data={
                            "id": newID,
                            "cat": True,
                        }
                    )
                    self.tree.SortChildren(self.tree_root)
                    self.log.debug(
                        "Category {} added correctly".format(dlg.GetValue())
                    )
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
        if dlg.ShowModal() == wx.ID_OK:
            try:
                category_id = self.database_comp.category_add(
                    dlg.GetValue(),
                    itemData["id"]
                )
                if category_id:
                    newID = category_id[0]
                    self.tree.AppendItem(
                        self.tree.GetSelection(),
                        dlg.GetValue(),
                        image=0,
                        selImage=1,
                        data={
                            "id": newID,
                            "cat": True,
                        }
                    )
                    self.tree.SortChildren(self.tree.GetSelection())
                    if not self.tree.IsExpanded(self.tree.GetSelection()):
                        self.tree.Expand(self.tree.GetSelection())
                    self.log.debug(
                        "Subcategory {} added correctly".format(dlg.GetValue())
                    )
                    # self._tree_filter()
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
                self.database_comp.category_rename(
                    dlg.GetValue(),
                    itemData["id"]
                )
                self.tree.SetItemText(self.tree.GetSelection(), dlg.GetValue())
                self.log.debug(
                    "Category {} renamed to {} correctly".format(
                        itemName,
                        dlg.GetValue()
                    )
                )

            except Exception as e:
                self.log.error(
                    "Error renaming {} to {}: {}.".format(
                        itemName,
                        dlg.GetValue(),
                        e
                    )
                )

        dlg.Destroy()
        # self._tree_filter()

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
            "¿Seguro que desea eliminar la categoría {}?.".format(itemName) +
            "\n\nAVISO: Se borrarán todas las subcategorías y componentes" +
            " que contiene.",
            'Eliminar',
            wx.YES_NO | wx.ICON_QUESTION
        )

        if dlg.ShowModal() == wx.ID_YES:
            if self.database_comp.category_delete(itemData["id"]):
                self.tree.Delete(self.tree.GetSelection())
                self._tree_selection(None)
                self.log.debug(
                    "Category {} deleted correctly".format(itemName)
                )
            else:
                print("There was an error deleting the category")
                return

        dlg.Destroy()

    def _component_add(self, event):
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        template = self.database_comp._select(
            "Categories",
            ["Template"],
            where=[
                {'key': 'ID', 'value': itemData['id']},
            ]
        )
        component_frame = addComponentWindow.addComponentWindow(
            self,
            default_template=template[0][0]
        )
        # component_frame.MakeModal(true);
        component_frame.ShowModal()
        if component_frame.component_id:
            self.tree.AppendItem(
                self.tree.GetSelection(),
                self.database_comp.component_data(
                    component_frame.component_id
                )['name'],
                image=2,
                selImage=3,
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
        component_frame = addComponentWindow.addComponentWindow(
            self,
            itemData["id"]
        )

        component_frame.ShowModal()

        if not component_frame.closed:
            itemNewName = self.database_comp.component_data(itemData["id"])
            self.tree.SetItemText(
                self.tree.GetSelection(),
                itemNewName['name']
            )
            if int(itemNewName.get("stock") > 0):
                self.tree.SetItemTextColour(self.tree.GetSelection(), wx.Colour(0, 0, 0))
            else:
                self.tree.SetItemTextColour(self.tree.GetSelection(), wx.Colour(255, 0, 0))
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
            "¿Seguro que desea eliminar el componente {}?.\n\n".format(
                itemName
            ),
            'Eliminar',
            wx.YES_NO | wx.ICON_QUESTION
        )

        if dlg.ShowModal() == wx.ID_YES:
            try:
                if self.database_comp._delete(
                    "Components",
                    [
                        {'key': 'ID', 'value': itemData["id"]}
                    ]
                ) is not None:
                    self.log.debug("Commiting changes...")
                    self.database_comp.conn.commit()
                    self.tree.Delete(self.tree.GetSelection())
                    self.log.debug(
                        "Component id {} deleted correctly".format(
                            itemData["id"]
                        )
                    )
                    self._tree_selection(None)
                else:
                    self.log.error("There was an error deleting the component")
                    return

            except Exception as e:
                self.log.error(
                    "There was an error deleting the component: {}".format(e)
                )
                dlg = wx.MessageDialog(
                    None,
                    "There was an error deleting the component: {}".format(
                        itemName
                    ),
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()

    def _set_default_template(self, event):
        component_frame = setDefaultTemplate.setDefaultTemplate(self)
        component_frame.ShowModal()

    def _stock_add(self, event):
        item = self.tree.GetSelection()
        if not item.IsOk():
            self.log.warning("Tree item is not OK")
            return

        itemData = self.tree.GetItemData(item)
        stock = self.database_comp._select(
            "Components",
            ["Stock"],
            where=[
                {
                    'key': 'ID',
                    'value': itemData['id']
                },
            ]
        )

        while True:
            dlg = wx.TextEntryDialog(
                self,
                'Añadir componentes a añadir',
                'Añadir componentes'
            )
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    added = int(dlg.GetValue())
                except Exception as e:
                    dlg = wx.MessageDialog(
                        None,
                        "La entrada indicada no es un número: {}".format(e),
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    continue

                try:
                    new_stock = stock[0][0] + added
                    self.database_comp._update(
                        "Components",
                        updates=[
                            {
                                'key': 'Stock',
                                'value': new_stock,
                            },
                        ],
                        where=[
                            {
                                'key': 'ID',
                                'value': itemData['id']
                            },
                        ],
                        auto_commit=True
                    )
                    self.update_data_grid(itemData['id'])
                    if new_stock > 0:
                        self.stock_bbar.EnableButton(ID_STOCK_REM, True)
                        self.tree.SetItemTextColour(item, wx.Colour(0, 0, 0))
                    dlg = wx.MessageDialog(
                        None,
                        "Stock añadido correctamente",
                        'Correcto',
                        wx.OK | wx.ICON_INFORMATION
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    break

                except Exception as e:
                    self.log.error("There was an error addind the stock: {}".format(e))
                    dlg = wx.MessageDialog(
                        None,
                        "Ocurrió un error al añadir el stock: {}".format(e),
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    break
            else:
                break

    def _stock_remove(self, event):
        item = self.tree.GetSelection()
        if not item.IsOk():
            self.log.warning("Tree item is not OK")
            return

        itemData = self.tree.GetItemData(item)
        stock = self.database_comp._select(
            "Components",
            ["Stock"],
            where=[
                {
                    'key': 'ID',
                    'value': itemData['id']
                },
            ]
        )

        while True:
            dlg = wx.TextEntryDialog(
                self,
                'Componentes usados (stock {})'.format(stock[0][0]),
                'Quitar componentes'
            )
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    removed = int(dlg.GetValue())
                except Exception as e:
                    dlg = wx.MessageDialog(
                        None,
                        "La entrada indicada no es un número: {}".format(e),
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    continue

                if removed <= stock[0][0]:
                    try:
                        new_stock = stock[0][0] - removed
                        self.database_comp._update(
                            "Components",
                            updates=[
                                {
                                    'key': 'Stock',
                                    'value': new_stock,
                                },
                            ],
                            where=[
                                {
                                    'key': 'ID',
                                    'value': itemData['id']
                                },
                            ],
                            auto_commit=True
                        )
                        self.update_data_grid(itemData['id'])
                        if new_stock == 0:
                            self.stock_bbar.EnableButton(ID_STOCK_REM, False)
                            self.tree.SetItemTextColour(item, wx.Colour(255, 0, 0))
                        dlg = wx.MessageDialog(
                            None,
                            "Stock quitado correctamente",
                            'Correcto',
                            wx.OK | wx.ICON_INFORMATION
                        )
                        dlg.ShowModal()
                        dlg.Destroy()
                        break

                    except Exception as e:
                        self.log.error("There was an error removing the stock: {}".format(e))
                        dlg = wx.MessageDialog(
                            None,
                            "Ocurrió un error al quitar el stock: {}".format(e),
                            'Error',
                            wx.OK | wx.ICON_ERROR
                        )
                        dlg.ShowModal()
                        dlg.Destroy()
                        break
                else:
                    self.log.warning(
                        "The stock {} is lower than used components {}".format(
                            stock[0][0],
                            removed
                        )
                    )
                    dlg = wx.MessageDialog(
                        None,
                        "No hay stock suficiente",
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
            else:
                break

    def _attachments_manage(self, event):
        itemData = self.tree.GetItemData(self.tree.GetSelection())
        component_frame = manageAttachments.manageAttachments(
            self.database_comp,
            self, itemData.get('id')
        )
        component_frame.ShowModal()
        component_frame.Destroy()
        self._tree_selection(None)

    def _datasheet_view(self, event):
        itemData = self.tree.GetItemData(self.tree.GetSelection())

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
            wildcard="Imágenes (*.jpg, *.jpeg, *.png, *.gif, *.bmp)|" +
                "*.jpg;*.jpeg;*.png;*.gif;*.bmp|Todos los ficheros (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Proceed loading the file chosen by the user
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
            "¿Seguro que desea eliminar la imagen de {}?.\n\n".format(
                itemName
            ),
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
                self.log.error(
                    "There was an error deleting the image: {}.".format(e)
                )

    def _image_export(self, event):
        with wx.FileDialog(
            self,
            "Guardar fichero de imagen",
            wildcard="Imágenes PNG (*.png)|*.png",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            try:
                bitmap = self.image.GetBitmap()
                bitmap.SaveFile(fileDialog.GetPath(), wx.BITMAP_TYPE_PNG)

                dlg = wx.MessageDialog(
                    None,
                    "Imagen guardada correctamente",
                    'Borrada',
                    wx.OK | wx.ICON_INFORMATION
                )
                dlg.ShowModal()
                dlg.Destroy()
            except Exception as e:
                self.log.error(
                    "There was an error saving the image: {}.".format(e)
                )
                dlg = wx.MessageDialog(
                    None,
                    "Ocurrió un error al exportar la imagen",
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()

    def _image_view(self, event):
        bitmap = wx.Bitmap(self.loaded_images[self.actual_image])
        tempName = next(_get_candidate_names())
        tempFolder = _get_default_tempdir()
        fName = path.join(
            tempFolder,
            tempName +
            ".png"
        )

        try:
            bitmap.SaveFile(fName, wx.BITMAP_TYPE_PNG)
            startfile(fName)
            print("done")
        except Exception as e:
            self.log.error(
                "There was an error saving the image: {}.".format(e)
            )
            dlg = wx.MessageDialog(
                None,
                "Ocurrió un error al exportar la imagen",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()

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

    def update_data_grid(self, id, category=False):
        Name = None
        Data = {}

        # Is a category
        if category:
            # Getting data
            category = self.database_comp._select(
                "Categories",
                ["Name"],
                where=[
                    {
                        'key': 'ID',
                        'value': id
                    },
                ]
            )
            parentOfCats = self.database_comp._select(
                "Categories",
                ["COUNT(*)"],
                where=[
                    {
                        'key': 'Parent',
                        'value': id
                    },
                ]
            )
            parentOfComp = self.database_comp._select(
                "Components",
                ["COUNT(*)"],
                where=[
                    {
                        'key': 'Category',
                        'value': id
                    },
                ]
            )

            # Generating Name and Data
            Name = category[0][0]
            Data = {
                "Subcategorías": parentOfCats[0][0],
                "Componentes": parentOfComp[0][0]
            }
        else:
            component_data = self.database_comp.component_data(id)
            if not component_data:
                self.log.warning(
                    "There is no component data"
                )
                Name = (
                    "Tipo de componente no encontrado. Por favor, "
                    "verifica si se borró la plantilla."
                )
            else:
                Name = component_data['name']
                first = True
                Key = ""
                Value = ""
                for item in component_data['template_data']['fields']:
                    item_value = component_data['data_real'].get(item['id'], {}).get('value', '--')
                    if item_value == "":
                        item_value = '--'

                    if first:
                        Key = item['label']
                        first = False
                    elif item['field_data']['join_previous'].lower() == 'false':
                        Data.update({
                            Key: Value
                        })
                        Value = ""
                        Key = item['label']
                        first = False
                    else:
                        if item['field_data']['no_space'].lower() == 'false' and not first:
                            Value += " "
                        if item['field_data']['in_name_label'].lower() == 'true':
                            if item['field_data'].get(
                                'in_name_label_separator',
                                'true'
                            ).lower() == 'true':
                                Value += "{}:".format(item['label'])
                            else:
                                Value += "{}".format(item['label'])
                            if item['field_data'].get(
                                'no_space',
                                'false'
                            ).lower() == 'false' and not first:
                                Value += " "

                    Value += item_value

                Data.update({
                    Key: Value
                })
                Data.update({
                    "Stock": component_data['stock']
                })

        # No Name
        if Name is None:
            self.log.warning("There's no name for component id {}".format(id))
            return

        # Cleanup GRID
        if self.textFrame.GetNumberRows() > 1:
            self.textFrame.DeleteRows(
                1,
                self.textFrame.GetNumberRows()-1
            )

        # Setting data
        self.textFrame.SetCellValue(0, 0, Name)
        current = 1
        for key, value in Data.items():
            self.textFrame.InsertRows(-1, 1)
            inserted = self.textFrame.GetNumberRows()-1

            self.textFrame.SetReadOnly(inserted, 0, True)
            self.textFrame.SetReadOnly(inserted, 1, True)

            self.textFrame.SetCellValue(inserted, 0, str(key))
            self.textFrame.SetCellValue(inserted, 1, str(value))

            self.textFrame.SetCellFont(current, 0, self.grid_left_row_font)
            self.textFrame.SetCellFont(current, 1, self.grid_right_row_font)
            current += 1

        self.OnGridSize(None)

    def _toggleHasStock(self, event):
        button = event.GetEventObject()
        globals.config['general']['only_show_stock'] = str(button.GetValue())
        self.tree.Freeze()
        self._tree_filter(
            filter=self.last_filter
        )
        self.tree.Thaw()

    def _tree_filter(
        self,
        parent_item=None,
        category_id=-1,
        filter=None,
        expanded=False
    ):
        if category_id == -1:
            self.tree.DeleteAllItems()
            self.searching = True

        if not parent_item:
            parent_item = self.tree_root

        cats = self.database_comp._select(
            "Categories",
            ["*"],
            where=[
                {'key': 'Parent', 'value': category_id},
                {'key': 'ID', 'comparator': '<>', 'value': '-1'},
            ],
            order=[
                {'key': 'Name'}
            ]
        )
        for item in cats:
            id = self.tree.AppendItem(
                parent_item,
                item[2],
                image=0,
                selImage=1,
                data={
                    "id": item[0],
                    "cat": True,
                }
            )

            child_cat = self.database_comp._select(
                "Categories",
                ["COUNT(*)"],
                where=[
                    {'key': 'Parent', 'value': item[0]},
                ]
            )
            child_com = self.database_comp._select(
                "Components",
                ["COUNT(*)"],
                where=[
                    {'key': 'Category', 'value': item[0]},
                ]
            )
            if child_cat[0][0] > 0 or child_com[0][0] > 0:
                self._tree_filter(id, item[0], filter, item[3])
            elif filter:
                self.tree.Delete(id)

        components = self.database_comp._select(
            "Components",
            ["ID", "Stock"],
            where=[
                {'key': 'Category', 'value': category_id},
            ]
        )

        for component in components:
            found = False if filter else True

            if filter:
                component_name = self.database_comp.component_data(
                    component[0]
                )['name']
                if filter.lower() in component_name.lower():
                    found = True

                if not found:
                    fields = self.database_comp.component_data(component[0])
                    for item in fields['data_real']:
                        for field, field_data in (
                             fields['data_real'][item].items()):
                            if filter.lower() in field_data.lower():
                                found = True
                                break
            if found:
                if (globals.config['general']['only_show_stock'].lower() == "false"
                        or component[1] > 0):
                    item = self.tree.AppendItem(
                        parent_item,
                        self.database_comp.component_data(component[0])['name'],
                        image=2,
                        selImage=3,
                        data={
                            "id": component[0],
                            "cat": False,
                        }
                    )
                    if component[1] == 0:
                        self.tree.SetItemTextColour(item, wx.Colour(255, 0, 0))

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
            self.searching = False
        self.tree.Update()

    def _tree_selection(self, event):
        if self.searching:
            return
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

            for item in self.database_comp._select(
                "Images",
                ["ID", "Image", "Imagecompression"],
                where=[
                    {
                        'key': 'Category_id' if itemData.get('cat') else 'Component_id',
                        'value': itemData.get('id')
                    },
                ]
            ):
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
                self.update_data_grid(
                    itemData.get('id'),
                    category=True
                )
            else:
                self.update_data_grid(
                    itemData.get('id')
                )
            self._onImageResize(None)

        if event:
            event.Skip()

    def _tree_item_collapsed(self, event):
        if event.GetItem().IsOk() and not self.searching:
            print("Tree_collapsed")
            itemData = self.tree.GetItemData(event.GetItem())
            self.database_comp._update(
                "Categories",
                updates=[
                    {
                        'key': 'Expanded',
                        'value': False,
                    },
                ],
                where=[
                    {
                        'key': 'ID',
                        'value': itemData['id']
                    },
                ],
                auto_commit=True
            )

    def _tree_item_expanded(self, event):
        if event.GetItem().IsOk() and not self.searching:
            print("Tree_Expanded", self.searching)
            itemData = self.tree.GetItemData(event.GetItem())
            self.database_comp._update(
                "Categories",
                updates=[
                    {
                        'key': 'Expanded',
                        'value': True,
                    },
                ],
                where=[
                    {
                        'key': 'ID',
                        'value': itemData['id']
                    },
                ],
                auto_commit=True
            )

    def _tree_drag_start(self, event):
        event.Allow()
        self.dragItem = event.GetItem()

    def _tree_drag_end(self, event):
        # If we dropped somewhere that isn't on top
        # of an item, ignore the event
        if event.GetItem().IsOk():
            target = event.GetItem()
        else:
            return

        # Make sure this member exists.
        try:
            source = self.dragItem
        except Exception as e:
            self.log.warning("Exception: {}".format(e))
            return

        # Don't do anything if destination is the parent of source
        if self.tree.GetItemParent(source) == target:
            self.log.info("The destination is the actual parent")
            self.tree.Unselect()
            return

        if self._ItemIsChildOf(target, source):
            self.log.info(
                "Tree item can not be moved into itself or a child!"
            )
            self.tree.Unselect()
            return

        src_data = self.tree.GetItemData(source)
        target_data = self.tree.GetItemData(target)

        if not target_data['cat']:
            self.log.info(
                "Destination is a component, and only categories are " +
                "allowed as destination"
            )
            return

        try:
            if src_data['cat']:
                self.database_comp._update(
                    "Categories",
                    [
                        {'key': 'Parent', 'value': target_data['id']}
                    ],
                    [
                        {'key': 'ID', 'value': src_data['id']}
                    ]
                )
            else:
                self.database_comp._update(
                    "Components",
                    [
                        {'key': 'Category', 'value': target_data['id']}
                    ],
                    [
                        {'key': 'ID', 'value': src_data['id']}
                    ]
                )

        except Exception as e:
            self.log.error(
                "There was an error moving the object: {}".format(e)
            )
            return

        self.tree.Delete(source)
        self.tree.DeleteChildren(target)
        self.tree.Freeze()
        self._tree_filter(
            parent_item=target,
            category_id=target_data['id'],
            filter=self.last_filter,
            expanded=False
        )
        self.tree.Expand(target)
        self.tree.Thaw()

    def _ItemIsChildOf(self, searchID, itemID):
        if itemID == searchID:
            return True

        item, cookie = self.tree.GetFirstChild(itemID)
        while item.IsOk():
            itemName = self.tree.GetItemText(item)
            itemSearchName = self.tree.GetItemText(searchID)
            self.log.debug(
                "Checking if item {} is {}".format(itemName, itemSearchName)
            )
            if item == searchID:
                self.log.debug("Items are equal")
                return True
            else:
                self.log.debug("Items are different")

            if self.tree.ItemHasChildren(item):
                self.log.debug("Item {} has children".format(itemName))
                if self._ItemIsChildOf(searchID, item):
                    return True

            item, cookie = self.tree.GetNextChild(itemID, cookie)
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
            self.stock_bbar.EnableButton(ID_STOCK_ADD, False)
            self.stock_bbar.EnableButton(ID_STOCK_REM, False)
        else:
            exists = self.database_comp._select(
                "Files",
                ["ID"],
                where=[
                    {
                        'key': 'Component',
                        'value': itemData['id']
                    },
                ]
            )
            if len(exists) > 0:
                self.ds_bbar.EnableButton(ID_DS_VIEW, True)
            else:
                self.ds_bbar.EnableButton(ID_DS_VIEW, False)

            stock = self.database_comp._select(
                "Components",
                ["Stock"],
                where=[
                    {
                        'key': 'ID',
                        'value': itemData['id']
                    },
                ]
            )
            if stock[0][0] > 0:
                self.stock_bbar.EnableButton(ID_STOCK_REM, True)
            else:
                self.stock_bbar.EnableButton(ID_STOCK_REM, False)

            self.cat_bbar.EnableButton(ID_CAT_ADDSUB, False)
            self.cat_bbar.EnableButton(ID_CAT_DELETE, False)
            self.cat_bbar.EnableButton(ID_CAT_TEM_SET, False)
            self.cat_bbar.EnableButton(ID_CAT_RENAME, False)
            self.com_bbar.EnableButton(ID_COM_ADD, False)
            self.com_bbar.EnableButton(ID_COM_DEL, True)
            self.com_bbar.EnableButton(ID_COM_ED, True)
            self.ds_bbar.EnableButton(ID_DS_ADD, True)
            self.stock_bbar.EnableButton(ID_STOCK_ADD, True)

        exists = self.database_comp._select(
            "Images",
            ["ID"],
            where=[
                {
                    'key': 'Category_id' if itemData.get('cat') else 'Component_id',
                    'value': itemData['id']
                },
            ]
        )
        if len(exists) > 0:
            self.button_add.Enable()
            self.button_del.Enable()
            self.button_download.Enable()
        else:
            self.button_add.Enable()
            self.button_del.Disable()
            self.button_download.Disable()

    def _onImageResize(self, event):
        frame_size = self.image.GetSize()
        if frame_size[0] != 0:
            bitmap = None
            image = self.loaded_images[self.actual_image]
            if self.image_keep_ratio:
                width = None
                height = None
                if frame_size[0] > frame_size[1]:
                    width = frame_size[1]
                    height = frame_size[1]
                else:
                    width = frame_size[0]
                    height = frame_size[0]

                if (width > 0) and (height > 0):
                    new_img = image.Scale(width, height)
                    pos_x = int((frame_size[0] - width) / 2)
                    pos_y = int((frame_size[1] - height) / 2)
                    new_img.Resize((frame_size[0], frame_size[1]), (pos_x, pos_y))
                    bitmap = wx.Bitmap(new_img)
            else:
                bitmap = wx.Bitmap(image.Scale(frame_size[0], frame_size[1]))

            if bitmap:
                self.image.SetBitmap(bitmap)

        if event:
            event.Skip()

    def _search(self, event):
        if globals.config["general"]["automatic_search"].lower() == 'true':
            searchText = self.search.GetValue()
            if len(searchText) > 3:
                self.timer.StartOnce(1000)
            else:
                self.timer.Stop()

        if event:
            event.Skip()

    def _searchText(self, event):
        searchText = self.search.GetValue()
        self.tree.Freeze()
        if len(searchText) > 2:
            self._tree_filter(filter=searchText)
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
        if options_window.changed_components_db:
            self.tree.Freeze()
            self._tree_filter(
                filter=self.last_filter
            )
            self.tree.Thaw()

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
            self.log.error(
                "There was an error optimizing the Database: {}".format(e)
            )
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
            globals.config["main_window"]["pos_x"] = int(x)
            globals.config["main_window"]["pos_y"] = int(y)
        event.Skip()

    def OnSize(self, event):
        if not self.IsMaximized():
            w, h = event.GetSize()
            globals.config["main_window"]["size_w"] = int(w)
            globals.config["main_window"]["size_h"] = int(h)
        event.Skip()

    def OnGridSize(self, event):
        last_column_size = self.textFrame.GetClientRect()[2]
        for column in range(0, self.textFrame.GetNumberCols()-1):
            last_column_size -= self.textFrame.GetColSize(column)

        if last_column_size > 1:
            self.textFrame.SetColSize(1, last_column_size)

        if event:
            event.Skip()

    def _templates_manager(self, event):
        templates_manager = manageTemplates.manageTemplates(self)
        templates_manager.ShowModal()

    # ##=== Main Function ===## #
    def __init__(self):
        WindowStyle = wx.DEFAULT_FRAME_STYLE
        if globals.config["main_window"]["maximized"]:
            WindowStyle = wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE
        wx.Frame.__init__(
            self,
            None,
            title="Components Manager",
            size=(
                globals.config["main_window"]["size_w"],
                globals.config["main_window"]["size_h"]
            ),
            pos=(
                globals.config["main_window"]["pos_x"],
                globals.config["main_window"]["pos_y"]
            ),
            style=WindowStyle
        )

        # Changing the icon
        icon = wx.Icon(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"], 'icon.ico'
            ),
            wx.BITMAP_TYPE_ICO
        )
        self.SetIcon(icon)

        # ## Log Configuration ## #
        self.log = getLogger()
        self.log.setLevel(DEBUG)
        # create a file handler
        handler = FileHandler(globals.config["general"]['log_file'], 'a+', 'utf-8')
        # create a logging format
        formatter = Formatter(
            '%(asctime)s - %(funcName)s() - %(levelname)s: %(message)s'
        )
        handler.setFormatter(formatter)
        # add the handlers to the logger
        self.log.addHandler(handler)
        self.log.debug("Changing log level to {}".format(
            globals.config["general"]['log_level'])
        )
        self.log.setLevel(globals.config["general"]['log_level'])

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
        self.last_filter = None
        self.last_selected_item = None
        self.searching = False
        self.image_keep_ratio = True
        self.grid_left_column_size = 130
        self.grid_title_font = wx.Font(
            wx.FontInfo(10).Bold()
        )
        self.grid_left_row_font = wx.Font(
            wx.FontInfo(8).Bold()
        )
        self.grid_right_row_font = wx.Font(
            wx.FontInfo(8)
        )

        # Database data decryption
        self.dbase_config = {
            'salt': None,
            'pass': None,
            'components_db': {
                'mysql_host': None,
                'mysql_port': None,
                'mysql_user': None,
                'mysql_pass': None,
                'mysql_dbase': None
            },
            'templates_db': {
                'mysql_host': None,
                'mysql_port': None,
                'mysql_user': None,
                'mysql_pass': None,
                'mysql_dbase': None
            }
        }

        if globals.config.get("general", {}).get('enc_key', '').lower() in ['', 'none', 'false']:
            self.dbase_config['components_db']['mysql_host'] = (
                globals.config['components_db']['mysql_host']
            )
            self.dbase_config['components_db']['mysql_port'] = (
                globals.config['components_db']['mysql_port']
            )
            self.dbase_config['components_db']['mysql_user'] = (
                globals.config['components_db']['mysql_user']
            )
            self.dbase_config['components_db']['mysql_pass'] = (
                globals.config['components_db']['mysql_pass']
            )
            self.dbase_config['components_db']['mysql_dbase'] = (
                globals.config['components_db']['mysql_dbase']
            )
            self.dbase_config['templates_db']['mysql_host'] = (
                globals.config['templates_db']['mysql_host']
            )
            self.dbase_config['templates_db']['mysql_port'] = (
                globals.config['templates_db']['mysql_port']
            )
            self.dbase_config['templates_db']['mysql_user'] = (
                globals.config['templates_db']['mysql_user']
            )
            self.dbase_config['templates_db']['mysql_pass'] = (
                globals.config['templates_db']['mysql_pass']
            )
            self.dbase_config['templates_db']['mysql_dbase'] = (
                globals.config['templates_db']['mysql_dbase']
            )
        else:
            key = globals.config["general"]['enc_key'].split("$")
            while True:
                dlg = wx.PasswordEntryDialog(
                    self,
                    'Introduzca la contraseña de protección de los datos de la BBDD',
                    'Desencriptar datos'
                )
                dlg.SetValue("")
                if dlg.ShowModal() == wx.ID_OK:
                    if sha256(dlg.GetValue().encode('utf-8')).hexdigest() == key[2]:
                        try:
                            # Storing password settings
                            self.dbase_config['salt'] = base64.b64decode(key[1])
                            self.dbase_config['pass'] = dlg.GetValue().encode('utf8')

                            # Generating encryption/decryption key
                            hash_sha512 = sha512(self.dbase_config['pass'])
                            self.dbase_config['iterations'] = (
                                crypto.hash_to_iterations(hash_sha512.hexdigest(), 6)
                            )
                            kdf = PBKDF2HMAC(
                                algorithm=hashes.SHA512(),
                                length=32,
                                salt=self.dbase_config['salt'],
                                iterations=self.dbase_config['iterations'],
                                backend=default_backend()
                            )
                            encryption_key = base64.urlsafe_b64encode(
                                kdf.derive(self.dbase_config['pass'])
                            )

                            # Decrypting data
                            dec = Fernet(encryption_key)
                            self.dbase_config['components_db']['mysql_host'] = (
                                dec.decrypt(
                                    globals.config['components_db']['mysql_host'].encode('utf8')
                                )
                            ).decode()
                            self.dbase_config['components_db']['mysql_port'] = (
                                globals.config['components_db']['mysql_port']
                            )
                            self.dbase_config['components_db']['mysql_user'] = (
                                dec.decrypt(
                                    globals.config['components_db']['mysql_user'].encode('utf8')
                                )
                            ).decode()
                            self.dbase_config['components_db']['mysql_pass'] = (
                                dec.decrypt(
                                    globals.config['components_db']['mysql_pass'].encode('utf8')
                                )
                            ).decode()
                            self.dbase_config['components_db']['mysql_dbase'] = (
                                dec.decrypt(
                                    globals.config['components_db']['mysql_dbase'].encode('utf8')
                                )
                            ).decode()
                            self.dbase_config['templates_db']['mysql_host'] = (
                                dec.decrypt(
                                    globals.config['templates_db']['mysql_host'].encode('utf8')
                                )
                            ).decode()
                            self.dbase_config['templates_db']['mysql_port'] = (
                                    globals.config['templates_db']['mysql_port']
                            )
                            self.dbase_config['templates_db']['mysql_user'] = (
                                dec.decrypt(
                                    globals.config['templates_db']['mysql_user'].encode('utf8')
                                )
                            ).decode()
                            self.dbase_config['templates_db']['mysql_pass'] = (
                                dec.decrypt(
                                    globals.config['templates_db']['mysql_pass'].encode('utf8')
                                )
                            ).decode()
                            self.dbase_config['templates_db']['mysql_dbase'] = (
                                dec.decrypt(
                                    globals.config['templates_db']['mysql_dbase'].encode('utf8')
                                )
                            ).decode()

                            break
                        except Exception as e:
                            self.log.error("There was an error decrypting data: {}".format(e))
                            dlg = wx.MessageDialog(
                                None,
                                "Error desencriptando los datos de la BBDD.\n " +
                                "Verifique que no ha modificado algún dato manualmente",
                                'Error',
                                wx.OK | wx.ICON_ERROR
                            )
                            dlg.ShowModal()
                            dlg.Destroy()
                            sys.exit(1)
                    else:
                        dlg = wx.MessageDialog(
                            None,
                            "La contraseña indicada no es correcta...",
                            'Error',
                            wx.OK | wx.ICON_ERROR
                        )
                        dlg.ShowModal()
                        dlg.Destroy()
                else:
                    exit(1)

        # Components Database connection
        if globals.config['components_db']['mode'] == 0:
            try:
                self.database_comp = dbase(
                    globals.config['components_db']['sqlite_file_real'],
                    auto_commit=False,
                    parent=self
                )

            except Exception as e:
                self.log.error("There was an error opening components DB: {}".format(e))
                dlg = wx.MessageDialog(
                    None,
                    "Error al abrir la BBDD de componentes: {}".format(e),
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()

        elif globals.config['components_db']['mode'] == 1:
            try:
                self.database_comp = MySQL(
                    self.dbase_config['components_db']['mysql_host'],
                    self.dbase_config['components_db']['mysql_user'],
                    self.dbase_config['components_db']['mysql_pass'],
                    self.dbase_config['components_db']['mysql_dbase'],
                    auto_commit=False,
                    parent=self
                )
            except Exception as e:
                self.log.error("There was an error connecting to components DB: {}".format(e))
                dlg = wx.MessageDialog(
                    None,
                    "Error al conectar a la BBDD de componentes: {}".format(e),
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()

        # Templates Database connection
        if globals.config['templates_db']['mode'] == 0:
            try:
                self.database_temp = dbase(
                    globals.config['templates_db']['sqlite_file_real'],
                    auto_commit=False,
                    templates=True,
                    parent=self
                )

            except Exception as e:
                self.log.error("There was an error opening templates DB: {}".format(e))
                dlg = wx.MessageDialog(
                    None,
                    "Error al abrir la BBDD de plantillas: {}".format(e),
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()

        elif globals.config['templates_db']['mode'] == 1:
            try:
                self.database_temp = MySQL(
                    self.dbase_config['templates_db']['mysql_host'],
                    self.dbase_config['templates_db']['mysql_user'],
                    self.dbase_config['templates_db']['mysql_pass'],
                    self.dbase_config['templates_db']['mysql_dbase'],
                    auto_commit=False,
                    templates=True,
                    parent=self
                )

            except Exception as e:
                self.log.error("There was an error connecting to templates DB: {}".format(e))
                dlg = wx.MessageDialog(
                    None,
                    "Error al conectar a la BBDD de plantillas: {}".format(e),
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()

        # Timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._searchText, self.timer)

        # Creating splitter
        self.log.debug("Creating splitter")
        # Main Splitter
        splitter = wx.SplitterWindow(self, -1, style=wx.RAISED_BORDER)

        # Ribbon Bar
        ribbon = RB.RibbonBar(self, -1)
        page = RB.RibbonPage(ribbon, wx.ID_ANY, "Page")

        # #--------------------# #
        # ## Panel Categorías ## #
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
            'Elimina una categoría o subcategoría, incluyendo ' +
            'todas las subcategorías y componentes que hay en ella'
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
            'Indica la plantilla por defecto que se abrirá al ' +
            'añadir un componente'
        )

        # #---------------------# #
        # ## Panel Componentes ## #
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

        # #------------------# #
        # ## Barra stock ## #
        pST = RB.RibbonPanel(page, wx.ID_ANY, "Stock")
        self.stock_bbar = RB.RibbonButtonBar(pST)
        # Manage files
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                'component_buy.png'
            )
        )
        self.stock_bbar.AddSimpleButton(
            ID_STOCK_ADD,
            "Añadir Stock",
            image,
            ''
        )
        # View Datasheet
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                'component_use.png'
            )
        )
        self.stock_bbar.AddSimpleButton(
            ID_STOCK_REM,
            "Quitar Stock",
            image,
            ''
        )

        # #------------------# #
        # ## Barra Ficheros ## #
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
        self.ds_bbar.AddSimpleButton(
            ID_DS_ADD,
            "Gestionar",
            image,
            ''
        )
        # View Datasheet
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                'view_datasheet.png'
            )
        )
        self.ds_bbar.AddSimpleButton(
            ID_DS_VIEW,
            "Ver Datasheet",
            image,
            ''
        )

        # #----------------------# #
        # ## Barra Herramientas ## #
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
        self.tools_bbar.AddSimpleButton(
            ID_TOOLS_OPTIONS,
            "Opciones",
            image,
            ''
        )
        # Manage Templates
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                'template_manage.png'
            )
        )
        self.tools_bbar.AddSimpleButton(
            ID_TOOLS_MANAGE_TEMPLATES,
            "Gestionar Plantillas",
            image,
            ''
        )
        # Opitimize Database
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                'db_optimize.png'
            )
        )
        self.tools_bbar.AddSimpleButton(
            ID_TOOLS_VACUUM,
            "Optimizar BBDD",
            image,
            ''
        )

        # Eventos al pulsar botones
        self.cat_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._category_create,
            id=ID_CAT_ADD
        )
        self.cat_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._subcat_create,
            id=ID_CAT_ADDSUB
        )
        self.cat_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._category_rename,
            id=ID_CAT_RENAME
        )
        self.cat_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._category_delete,
            id=ID_CAT_DELETE
        )
        self.cat_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._set_default_template,
            id=ID_CAT_TEM_SET
        )
        self.com_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._component_add,
            id=ID_COM_ADD
        )
        self.com_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._component_edit,
            id=ID_COM_ED
        )
        self.com_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._component_delete,
            id=ID_COM_DEL
        )
        self.stock_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._stock_add,
            id=ID_STOCK_ADD
        )
        self.stock_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._stock_remove,
            id=ID_STOCK_REM
        )
        self.ds_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._attachments_manage,
            id=ID_DS_ADD
        )
        self.ds_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._datasheet_view,
            id=ID_DS_VIEW
        )
        self.tools_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._options,
            id=ID_TOOLS_OPTIONS
        )
        self.tools_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._templates_manager,
            id=ID_TOOLS_MANAGE_TEMPLATES
        )
        self.tools_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._vacuum,
            id=ID_TOOLS_VACUUM
        )

        self.cat_bbar.EnableButton(ID_CAT_ADDSUB, False)
        self.cat_bbar.EnableButton(ID_CAT_RENAME, False)
        self.cat_bbar.EnableButton(ID_CAT_DELETE, False)
        self.cat_bbar.EnableButton(ID_CAT_TEM_SET, False)
        self.com_bbar.EnableButton(ID_COM_ADD, False)
        self.com_bbar.EnableButton(ID_COM_DEL, False)
        self.com_bbar.EnableButton(ID_COM_ED, False)
        self.ds_bbar.EnableButton(ID_DS_ADD, False)
        self.ds_bbar.EnableButton(ID_DS_VIEW, False)
        self.stock_bbar.EnableButton(ID_STOCK_ADD, False)
        self.stock_bbar.EnableButton(ID_STOCK_REM, False)

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
        searchBox = wx.BoxSizer(wx.HORIZONTAL)
        self.search = wx.SearchCtrl(
            lPan,
            style=wx.TE_PROCESS_ENTER | wx.RAISED_BORDER
        )
        self.search.ShowCancelButton(True)
        self.search.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self._searchText)
        self.search.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self._cancelSearch)
        self.search.Bind(wx.EVT_TEXT_ENTER, self._searchText)
        stock = wx.ToggleButton(
            lPan,
            id=wx.ID_ANY,
            label="S",
            pos=wx.DefaultPosition,
            size=(22, 22),
            style=wx.BORDER_SIMPLE,
        )
        stock.Bind(wx.EVT_TOGGLEBUTTON, self._toggleHasStock)
        stock.SetToolTip(wx.ToolTip("Mostrar sólo resultados con stock"))
        if globals.config['general']['only_show_stock'].lower() == 'true':
            stock.SetValue(True)

        searchBox.Add(self.search, 1, wx.EXPAND)
        searchBox.Add(stock, 0, wx.EXPAND)
        lPanBox.Add(searchBox, 0, wx.EXPAND)
        self.search.Bind(wx.EVT_TEXT, self._search)
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
        # ImageList Images
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
        rPan = wx.SplitterWindow(splitter, -1, style=wx.BORDER_RAISED)

        # Window Splitter
        splitter.SplitVertically(lPan, rPan)
        splitter.SetSashGravity(0.6)

        imageSizer = wx.BoxSizer(wx.VERTICAL)
        imageFrame = wx.Panel(rPan)

        # ## Image Frame ## #
        image_frm_box = wx.BoxSizer(wx.VERTICAL)
        image_ctrl_panel = wx.Panel(
            imageFrame,
            style=wx.BORDER_RAISED,
            size=(-1, 39)
        )
        image_ctrl_box = wx.BoxSizer(wx.HORIZONTAL)

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
        self.button_back = ShapedButton.ShapedButton(
            image_ctrl_panel,
            button_back_up,
            button_back_down,
            button_back_disabled,
            button_back_over,
            size=(36, 36)
        )
        self.button_back.Bind(wx.EVT_LEFT_UP, self._change_image_back)

        # Add Button
        button_add_up = wx.Bitmap()
        button_add_up.LoadFile(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                'button_add_up_32.png'
            )
        )
        button_add_down = wx.Bitmap()
        button_add_down.LoadFile(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                'button_add_down_32.png'
            )
        )
        button_add_disabled = button_add_down.ConvertToDisabled()
        self.button_add = ShapedButton.ShapedButton(
            image_ctrl_panel,
            button_add_up,
            button_add_down,
            button_add_disabled,
            size=(36, 36)
        )
        self.button_add.Bind(wx.EVT_LEFT_UP, self._image_add)
        self.button_add.Disable()

        # Delete Button
        button_del_up = wx.Bitmap()
        button_del_up.LoadFile(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                'button_remove_up_32.png'
            )
        )
        button_del_down = wx.Bitmap()
        button_del_down.LoadFile(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                'button_remove_down_32.png'
            )
        )
        button_del_disabled = button_del_down.ConvertToDisabled()
        self.button_del = ShapedButton.ShapedButton(
            image_ctrl_panel,
            button_del_up,
            button_del_down,
            button_del_disabled,
            size=(36, 36)
        )
        self.button_del.Bind(wx.EVT_LEFT_UP, self._image_del)
        self.button_del.Disable()

        # Download Button
        button_download_up = wx.Bitmap()
        button_download_up.LoadFile(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                'button_down_up_32.png'
            )
        )
        button_download_down = wx.Bitmap()
        button_download_down.LoadFile(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                'button_down_down_32.png'
            )
        )
        button_download_disabled = button_download_down.ConvertToDisabled()
        self.button_download = ShapedButton.ShapedButton(
            image_ctrl_panel,
            button_download_up,
            button_download_down,
            button_download_disabled,
            size=(36, 36)
        )
        self.button_download.Bind(wx.EVT_LEFT_UP, self._image_export)
        self.button_download.Disable()

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
        self.button_next = ShapedButton.ShapedButton(
            image_ctrl_panel,
            button_next_up,
            button_next_down,
            button_next_disabled,
            button_next_over,
            size=(33, 36)
        )
        self.button_next.Bind(wx.EVT_LEFT_UP, self._change_image_next)

        # Image Box
        self.image = wx.StaticBitmap(
            imageFrame,
            wx.ID_ANY,
            self.loaded_images[self.actual_image].ConvertToBitmap(),
            style=wx.BORDER_RAISED
        )
        # No implementado en el módulo
        # self.image.SetScaleMode(wx.Scale_AspectFit)
        self.image.Bind(wx.EVT_SIZE, self._onImageResize)
        self.image.Bind(wx.EVT_LEFT_DCLICK, self._image_view)
        self.button_back.Enable(False)
        self.button_next.Enable(False)

        image_ctrl_box.Add(self.button_back, 0, 0, 0)
        image_ctrl_box.Add((0, 0), 1, wx.EXPAND, 0)
        image_ctrl_box.Add(self.button_add, 0, 0, 0)
        image_ctrl_box.Add(self.button_del, 0, 0, 0)
        image_ctrl_box.Add(self.button_download, 0, 0, 0)
        image_ctrl_box.Add((0, 0), 1, wx.EXPAND, 0)
        image_ctrl_box.Add(self.button_next, 0, 0, 0)
        image_ctrl_panel.SetSizer(image_ctrl_box)
        image_frm_box.Add(self.image, 1, wx.EXPAND)
        image_frm_box.AddSpacer(2)
        image_frm_box.Add(image_ctrl_panel, 0, wx.EXPAND, 0)
        imageSizer.Add(
            image_frm_box,
            1,
            wx.ALIGN_CENTER_HORIZONTAL | wx.SHAPED | wx.ALIGN_CENTER_VERTICAL
        )

        # Righ Panel split
        imageFrame.SetSizer(imageSizer)
        self.textFrame = Grid(
            rPan,
            style=wx.TE_READONLY | wx.BORDER_RAISED
        )
        self.textFrame.Bind(wx.EVT_SIZE, self.OnGridSize)
        self.textFrame.Bind(wx.grid.EVT_GRID_COL_SIZE, self.OnGridSize)
        self.textFrame.HideRowLabels()
        self.textFrame.HideColLabels()
        self.textFrame.CreateGrid(1, 2)
        self.textFrame.SetCellSize(0, 0, 1, 2)
        self.textFrame.SetCellBackgroundColour(0, 0, "#d3d3d3")
        self.textFrame.SetReadOnly(0, 0, True)
        self.textFrame.SetCellAlignment(0, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.textFrame.SetColSize(0, self.grid_left_column_size)
        self.textFrame.SetRowSize(0, 50)
        self.textFrame.SetCellFont(0, 0, self.grid_title_font)
        self.textFrame.SetCellValue(0, 0, "Seleccione un item para ver los datos")

        rPan.SplitHorizontally(imageFrame, self.textFrame)
        rPan.SetSashGravity(0.5)

        # Updating tree
        self._tree_filter()


# =========== #
#  Start GUI  #
# =========== #
mainWindow().Show()
app.MainLoop()
