# -*- coding: utf-8 -*-

'''
27 May 2019
@autor: Daniel Carrasco
'''
import wx
import wx.lib.agw.ribbon as RB
from widgets import ShapedButton, PlaceholderTextCtrl
from modules import getResourcePath, strToValue
import wx.lib.scrolledpanel as scrolled
from modules_local import CTreeCtrl
import globals

# Load main data
app = wx.App()
globals.init()

# ID de los botones
ID_CAT_ADD = wx.ID_HIGHEST + 1
ID_CAT_ADDSUB = ID_CAT_ADD + 1
ID_CAT_RENAME = ID_CAT_ADDSUB + 1
ID_CAT_DELETE = ID_CAT_RENAME + 1
ID_TEM_ADD = ID_CAT_DELETE + 1
ID_TEM_RENAME = ID_TEM_ADD + 1
ID_TEM_DELETE = ID_TEM_RENAME + 1
ID_FIELD_ADD = ID_TEM_DELETE + 1
ID_FIELD_UP = ID_FIELD_ADD + 1
ID_FIELD_DOWN = ID_FIELD_UP + 1
ID_FIELD_DELETE = ID_FIELD_DOWN + 1
ID_TOOLS_MANAGE = ID_FIELD_DELETE + 1
ID_TOOLS_VACUUM = ID_TOOLS_MANAGE + 1


# ###################################################################### #
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
        self.log = parent.log

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
            value="",
            placeholder="Etiqueta del campo (obligatoria)"
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
        self.type = wx.ComboBox(
            panel,
            id=wx.ID_ANY,
            choices=parent.field_kind,
            style=wx.CB_READONLY | wx.CB_DROPDOWN
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
            value="",
            placeholder="Vacío para automático"
        )
        box.Add(self.width, -1, wx.EXPAND)
        box.AddSpacer(self.border)
        panelBox.Add(box, 0, wx.EXPAND)
        panelBox.AddSpacer(self.between_items)

        panelBox.AddSpacer(self.border)
        panel.SetSizer(panelBox)

        # #--------------------------------------------------# #
        # Buttons BoxSizer
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_add = wx.Button(panel, label="Aceptar")
        btn_add.Bind(wx.EVT_BUTTON, self._save)
        self.SetDefaultItem(btn_add)
        btn_cancel = wx.Button(panel, label="Cancelar")
        btn_cancel.Bind(wx.EVT_BUTTON, self.close_dialog)
        btn_sizer.AddSpacer(10)
        btn_sizer.Add(btn_add)
        btn_sizer.AddSpacer(40)
        btn_sizer.Add(btn_cancel)
        btn_sizer.AddSpacer(10)

        panelBox.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        # #--------------------------------------------------# #


class manageValuesGroups(wx.Dialog):
    def close_dialog(self, event):
        self.Hide()

    def _add_group(self, event):
        dlg = wx.TextEntryDialog(
            self,
            'Nombre del grupo de valores',
            'Añadir Grupo'
        )
        if dlg.ShowModal() == wx.ID_OK:
            try:
                group_id = self.database_temp._insert(
                    "Values_group",
                    items=["Name"],
                    values=[dlg.GetValue()]
                )
                self.database_temp.conn.commit()
                self.updated = True
                if group_id and len(group_id) > 0:
                    new_item = self.group.Append(dlg.GetValue(), group_id[0])
                    self.group.SetSelection(new_item)
                    self._update_list(None)
                else:
                    self.log.error("There was an error creating the group.")
                    dlg = wx.MessageDialog(
                        None,
                        "Error creando el grupo",
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                """
                dlg = wx.MessageDialog(
                    None,
                    "Grupo añadido corréctamente",
                    'Correcto',
                    wx.OK | wx.ICON_INFORMATION
                )
                dlg.ShowModal()
                dlg.Destroy()
                """
            except Exception as e:
                self.log.error(
                    "There was an error adding the group to DB: {}".format(e)
                )
                dlg = wx.MessageDialog(
                    None,
                    "Error creando el grupo",
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()
                return False

    def _del_group(self, event):
        selected = self.group.GetSelection()
        if selected == -1:
            dlg = wx.MessageDialog(
                None,
                "Debe seleccionar un grupo del selector para poder borrarlo",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False
        itemName = self.group.GetString(selected)
        itemID = self.group.GetClientData(selected)
        dlg = wx.MessageDialog(
            None,
            "¿Seguro que desea eliminar el grupo {}?.\n\n".format(itemName) +
            "AVISO: Se borrarán todos los valores que contenga",
            'Eliminar',
            wx.YES_NO | wx.ICON_QUESTION
        )

        if dlg.ShowModal() == wx.ID_YES:
            try:
                self.database_temp._delete(
                    "Values_group",
                    where=[
                        {'key': "ID", 'value': itemID}
                    ]
                )
                self.database_temp.conn.commit()
                self.updated = True
                self.group.Delete(selected)
                if self.group.GetCount()-1 > selected:
                    self.group.SetSelection(selected)
                else:
                    self.group.SetSelection(self.group.GetCount()-1)

                self._update_list(None)
                """
                dlg = wx.MessageDialog(
                    None,
                    "Grupo eliminado corréctamente",
                    'Correcto',
                    wx.OK | wx.ICON_INFORMATION
                )
                dlg.ShowModal()
                dlg.Destroy()
                """

            except Exception as e:
                self.log.error(
                    "There was an error deleting the group: {}".format(e)
                )
                dlg = wx.MessageDialog(
                    None,
                    "Error eliminando el grupo",
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()
                return False

    def _add_value_to_group(self, event):
        selected = self.group.GetSelection()
        if selected == -1:
            dlg = wx.MessageDialog(
                None,
                "Debe seleccionar un grupo para poder añadir un valor.",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False
        itemID = self.group.GetClientData(selected)

        dlg = wx.TextEntryDialog(self, 'Valor a añadir', 'Añadir Valor')
        if dlg.ShowModal() == wx.ID_OK:
            try:
                value_id = self.database_temp._insert(
                    "Values",
                    items=[
                        "Group",
                        "Value",
                        "Order"
                    ],
                    values=[
                        itemID,
                        dlg.GetValue(),
                        self.listBox.GetCount(),
                    ]
                )
                self.database_temp.conn.commit()
                self.updated = True
                if value_id and len(value_id) > 0:
                    self.listBox.Append(dlg.GetValue(), value_id[0])
                else:
                    self.log.error("There was an error creating the value.")
                    err = wx.MessageDialog(
                        None,
                        "Error creando el valor",
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    err.ShowModal()
                    err.Destroy()
                    return False
                """
                ok = wx.MessageDialog(
                    None,
                    "Valor añadido corréctamente",
                    'Correcto',
                    wx.OK | wx.ICON_INFORMATION
                )
                ok.ShowModal()
                ok.Destroy()
                """
            except Exception as e:
                self.log.error(
                    "There was an error adding the value to DB: {}".format(e)
                )
                err = wx.MessageDialog(
                    None,
                    "Error creando el valor",
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                err.ShowModal()
                err.Destroy()
                return False
        dlg.Destroy()

    def _del_value_from_group(self, event):
        selected = self.listBox.GetSelection()
        if selected == -1:
            dlg = wx.MessageDialog(
                None,
                "Debe seleccionar un valor",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        itemName = self.listBox.GetString(selected)
        dlg = wx.MessageDialog(
            None,
            "¿Seguro que desea eliminar el valor {}?.\n\n".format(itemName),
            'Eliminar',
            wx.YES_NO | wx.ICON_QUESTION
        )

        itemData = self.listBox.GetClientData(selected)
        if dlg.ShowModal() == wx.ID_YES:
            try:
                self.database_temp.query(
                    "DELETE FROM [Values] WHERE ID = ?;",
                    (itemData, )
                )
                self.database_temp.conn.commit()
                self.updated = True
                self.listBox.Delete(selected)
                self.log.debug("Value {} deleted correctly".format(itemName))
                """
                ok = wx.MessageDialog(
                    None,
                    "Valor eliminado corréctamente",
                    'Correcto',
                    wx.OK | wx.ICON_INFORMATION
                )
                ok.ShowModal()
                ok.Destroy()
                """
            except Exception as e:
                self.log.error(
                    "There was an error deleting the value: {}".format(e)
                )
                err = wx.MessageDialog(
                    None,
                    "Error eliminando el valor",
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                err.ShowModal()
                err.Destroy()
                return False
        dlg.Destroy()

    def _ren_group(self, event):
        selected = self.group.GetSelection()
        if selected == -1:
            dlg = wx.MessageDialog(
                None,
                ("Debe seleccionar un grupo del "
                 "selector para poder renombrarlo"),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False
        dlg = wx.TextEntryDialog(
            self,
            'Nuevo nombre del grupo',
            'Renombrar grupo'
        )

        dlg.SetValue(self.group.GetString(selected))
        if dlg.ShowModal() == wx.ID_OK:
            try:
                self.database_temp._update(
                    "Values_group",
                    updates=[
                        {'key': 'Name', 'value': dlg.GetValue()}
                    ],
                    where=[
                        {'key': "ID", 'value': self.group.GetClientData(selected)}
                    ]
                )
                self.database_temp.conn.commit()
                self.updated = True
                self.group.SetString(selected, dlg.GetValue())
                dlg = wx.MessageDialog(
                    None,
                    "Grupo renombrado corréctamente",
                    'Correcto',
                    wx.OK | wx.ICON_INFORMATION
                )
                dlg.ShowModal()
                dlg.Destroy()

            except Exception as e:
                self.log.error(
                    "There was an error renaming the group: {}".format(e)
                )
                dlg = wx.MessageDialog(
                    None,
                    "Error renombrando el grupo",
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()
                return False

    def _ren_value_from_group(self, event):
        selected = self.listBox.GetSelection()
        if selected == -1:
            dlg = wx.MessageDialog(
                None,
                "Debe seleccionar un valor para poder renombrarlo",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        itemName = self.listBox.GetString(selected)
        dlg = wx.TextEntryDialog(
            self,
            'Nuevo nombre del valor',
            'Renombrar valor'
        )

        itemData = self.listBox.GetClientData(selected)
        dlg.SetValue(self.listBox.GetString(selected))
        if dlg.ShowModal() == wx.ID_OK:
            try:
                self.database_temp._update(
                    "Values",
                    updates=[
                        {'key': "Value", 'value': dlg.GetValue()}
                    ],
                    where=[
                        {'key': "ID", 'value': itemData}
                    ]
                )
                self.database_temp.conn.commit()
                self.updated = True
                self.listBox.SetString(selected, dlg.GetValue())
                self.log.debug(
                    "Value {} renamed to {} correctly".format(
                        itemName,
                        dlg.GetValue()
                    )
                )
                ok = wx.MessageDialog(
                    None,
                    "Valor renombrado corréctamente",
                    'Correcto',
                    wx.OK | wx.ICON_INFORMATION
                )
                ok.ShowModal()
                ok.Destroy()

            except Exception as e:
                self.log.error(
                    "There was an error renaming the value: {}".format(e)
                )
                err = wx.MessageDialog(
                    None,
                    "Error renombrando el valor",
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                err.ShowModal()
                err.Destroy()
                return False
        dlg.Destroy()

    def _move_up_value(self, event):
        selected = self.listBox.GetSelection()
        if selected == -1:
            dlg = wx.MessageDialog(
                None,
                "Debe seleccionar un valor",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if selected == 0:
            dlg = wx.MessageDialog(
                None,
                "El valor seleccionado no puede moverse arriba",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        try:
            sel_label = self.listBox.GetString(selected)
            sel_data = self.listBox.GetClientData(selected)
            up_label = self.listBox.GetString(selected-1)
            up_data = self.listBox.GetClientData(selected-1)

            self.database_temp._update(
                "Values",
                updates=[
                    {'key': "Order", 'value': selected-1}
                ],
                where=[
                    {'key': "ID", 'value': sel_data}
                ]
            )
            self.database_temp._update(
                "Values",
                updates=[
                    {'key': "Order", 'value': selected}
                ],
                where=[
                    {'key': "ID", 'value': sel_data}
                ]
            )
            self.listBox.SetString(selected, up_label)
            self.listBox.SetClientData(selected, up_data)
            self.listBox.SetString(selected-1, sel_label)
            self.listBox.SetClientData(selected-1, sel_data)
            self.listBox.SetSelection(selected-1)
            self.database_temp.conn.commit()
            self.updated = True

        except Exception as e:
            self.log.error(
                "There was an error moving the value up: {}".format(e)
            )
            dlg = wx.MessageDialog(
                None,
                "Ocurrió un error moviendo el valor arriba: {}".format(e),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

    def _move_down_value(self, event):
        selected = self.listBox.GetSelection()
        if selected == -1:
            dlg = wx.MessageDialog(
                None,
                "Debe seleccionar un valor",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if selected == self.listBox.GetCount()-1:
            dlg = wx.MessageDialog(
                None,
                "El valor seleccionado no puede moverse abajo",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        try:
            sel_label = self.listBox.GetString(selected)
            sel_data = self.listBox.GetClientData(selected)
            down_label = self.listBox.GetString(selected+1)
            down_data = self.listBox.GetClientData(selected+1)

            self.database_temp._update(
                "Values",
                updates=[
                    {'key': "Order", 'value': selected+1}
                ],
                where=[
                    {'key': "ID", 'value': sel_data}
                ]
            )
            self.database_temp._update(
                "Values",
                updates=[
                    {'key': "Order", 'value': selected}
                ],
                where=[
                    {'key': "ID", 'value': down_data}
                ]
            )
            self.listBox.SetString(selected, down_label)
            self.listBox.SetClientData(selected, down_data)
            self.listBox.SetString(selected+1, sel_label)
            self.listBox.SetClientData(selected+1, sel_data)
            self.listBox.SetSelection(selected+1)
            self.database_temp.conn.commit()
            self.updated = True

        except Exception as e:
            self.log.error(
                "There was an error moving the value down: {}".format(e)
            )
            dlg = wx.MessageDialog(
                None,
                "Ocurrió un error moviendo el valor abajo: {}".format(e),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

    def _update_list(self, event):
        selected = self.group.GetSelection()
        if selected != -1:
            itemID = self.group.GetClientData(selected)
            self.listBox.Freeze()
            self.listBox.Clear()
            values = self.database_temp._select(
                "Values",
                items=["ID", "Value"],
                where=[
                    {'key': "Group", 'value': itemID}
                ],
                order=[
                    {'key': "Order"}
                ]
            )
            for item in values:
                self.listBox.Append(item[1], item[0])
            self.listBox.Thaw()

    def _key_pressed(self, event):
        print(dir(event))
        if event.GetEventObject() == self.listBox:
            print(event.GetKeyCode())
            if event.GetKeyCode() == 13:
                self._add_value_to_group(None)
            elif event.GetKeyCode() == 127:
                self._del_value_from_group(None)

    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            wx.ID_ANY,
            "Añadir campo",
            size=(350, 265),
            style=wx.DEFAULT_DIALOG_STYLE
        )
        # Values
        self.border = 10
        self.between_items = 5
        self.updated = False
        self.log = parent.log
        self.database_temp = parent.database_temp

        panel = wx.Panel(self)
        panelBox = wx.BoxSizer(wx.VERTICAL)
        panelBox.AddSpacer(self.border)

        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.close_dialog)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.AddSpacer(self.border)
        self.group = wx.ComboBox(
            panel,
            id=wx.ID_ANY,
            style=wx.CB_READONLY | wx.CB_DROPDOWN | wx.CB_SORT
        )
        values = self.database_temp._select(
            "Values_group",
            items=["ID", "Name"]
        )
        print(values)
        if values:
            for group in values:
                self.group.Append(group[1], group[0])
        self.group.Bind(wx.EVT_COMBOBOX, self._update_list)
        self.group.SetSelection(0)
        box.Add(self.group, -1, wx.EXPAND)
        box.AddSpacer(self.between_items)
        # Add Button
        button_up = wx.Bitmap()
        button_up.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_add_up.png'
            )
        )
        button_down = wx.Bitmap()
        button_down.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_add_down.png'
            )
        )
        button_disabled = button_down.ConvertToDisabled()
        button = ShapedButton.ShapedButton(
            panel,
            button_up,
            button_down,
            button_disabled,
            size=(24, 24)
        )
        button.Bind(wx.EVT_LEFT_UP, self._add_group)
        box.Add(button, 0)
        box.AddSpacer(self.between_items)
        # Ren Button
        button_up = wx.Bitmap()
        button_up.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_rename_up.png'
            )
        )
        button_down = wx.Bitmap()
        button_down.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_rename_down.png'
            )
        )
        button_disabled = button_down.ConvertToDisabled()
        button = ShapedButton.ShapedButton(
            panel,
            button_up,
            button_down,
            button_disabled,
            size=(24, 24)
        )
        button.Bind(wx.EVT_LEFT_UP, self._ren_group)
        box.Add(button, 0)
        box.AddSpacer(self.between_items)
        # Remove Button
        button_up = wx.Bitmap()
        button_up.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_remove_up.png'
            )
        )
        button_down = wx.Bitmap()
        button_down.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_remove_down.png'
            )
        )
        button_disabled = button_down.ConvertToDisabled()
        button = ShapedButton.ShapedButton(
            panel,
            button_up,
            button_down,
            button_disabled,
            size=(24, 24)
        )
        button.Bind(wx.EVT_LEFT_UP, self._del_group)
        box.Add(button, 0)
        box.AddSpacer(self.border-6)
        panelBox.Add(box, 0, wx.EXPAND)
        panelBox.AddSpacer(self.between_items)
        panelBox.AddSpacer(self.between_items)

        # Listbox and panels
        lbBox = wx.BoxSizer(wx.HORIZONTAL)
        panelBox.Add(lbBox, 0, wx.EXPAND)
        panelBox.AddSpacer(self.between_items)
        bBox = wx.BoxSizer(wx.VERTICAL)
        self.listBox = wx.ListBox(
            panel,
            id=wx.ID_ANY,
            size=(-1, 170),
            style=0 | wx.LB_SINGLE,
            name="ItemList"
        )
        self.listBox.Bind(wx.EVT_KEY_DOWN, self._key_pressed)
        lbBox.AddSpacer(self.border)
        lbBox.Add(self.listBox, -1, wx.EXPAND)
        lbBox.AddSpacer(self.between_items)
        lbBox.Add(bBox, 0, wx.EXPAND)
        lbBox.AddSpacer(self.border-6)

        # Listbox Buttons
        # Add Button
        button_up = wx.Bitmap()
        button_up.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_add_up.png'
            )
        )
        button_down = wx.Bitmap()
        button_down.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_add_down.png'
            )
        )
        button_disabled = button_down.ConvertToDisabled()
        button = ShapedButton.ShapedButton(
            panel,
            button_up,
            button_down,
            button_disabled,
            size=(24, 24)
        )
        button.Bind(wx.EVT_LEFT_UP, self._add_value_to_group)
        bBox.Add(button, 0)
        bBox.AddSpacer(self.between_items)
        # Ren Button
        button_up = wx.Bitmap()
        button_up.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_rename_up.png'
            )
        )
        button_down = wx.Bitmap()
        button_down.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_rename_down.png'
            )
        )
        button_disabled = button_down.ConvertToDisabled()
        button = ShapedButton.ShapedButton(
            panel,
            button_up,
            button_down,
            button_disabled,
            size=(24, 24)
        )
        button.Bind(wx.EVT_LEFT_UP, self._ren_value_from_group)
        bBox.Add(button, 0)
        bBox.AddSpacer(self.between_items)
        # Remove Button
        button_up = wx.Bitmap()
        button_up.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_remove_up.png'
            )
        )
        button_down = wx.Bitmap()
        button_down.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_remove_down.png'
            )
        )
        button_disabled = button_down.ConvertToDisabled()
        button = ShapedButton.ShapedButton(
            panel,
            button_up,
            button_down,
            button_disabled,
            size=(24, 24)
        )
        button.Bind(wx.EVT_LEFT_UP, self._del_value_from_group)
        bBox.Add(button, 0)
        bBox.AddSpacer(self.between_items)
        # Up Button
        button_up = wx.Bitmap()
        button_up.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_up_up.png'
            )
        )
        button_down = wx.Bitmap()
        button_down.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_up_down.png'
            )
        )
        button_disabled = button_down.ConvertToDisabled()
        button = ShapedButton.ShapedButton(
            panel,
            button_up,
            button_down,
            button_disabled,
            size=(24, 24)
        )
        button.Bind(wx.EVT_LEFT_UP, self._move_up_value)
        bBox.Add(button, 0)
        bBox.AddSpacer(self.between_items)
        # Down Button
        button_up = wx.Bitmap()
        button_up.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_down_up.png'
            )
        )
        button_down = wx.Bitmap()
        button_down.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'button_down_down.png'
            )
        )
        button_disabled = button_down.ConvertToDisabled()
        button = ShapedButton.ShapedButton(
            panel,
            button_up,
            button_down,
            button_disabled,
            size=(24, 24)
        )
        button.Bind(wx.EVT_LEFT_UP, self._move_down_value)
        bBox.Add(button, 0)
        self._update_list(None)
        panel.SetSizer(panelBox)


# ###################################################################### #
class manageTemplates(wx.Dialog):
    # ##=== Exit Function ===## #
    def exitGUI(self, event):
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
                category_id = self.database_temp.category_add(dlg.GetValue())
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
                          "subcat": False,
                          "template": False
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
                category_id = self.database_temp.category_add(
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
                          "cat": False,
                          "subcat": True,
                          "template": False
                        }
                    )
                    self.tree.SortChildren(self.tree.GetSelection())
                    if not self.tree.IsExpanded(self.tree.GetSelection()):
                        self.tree.Expand(self.tree.GetSelection())
                    self.log.debug(
                        "Subcategory {} added correctly".format(dlg.GetValue())
                    )
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
                self.database_temp.category_rename(
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
            ("¿Seguro que desea eliminar la categoría "
             "{}?.\n\n".format(itemName) +
             "AVISO: Se borrarán todas las subcategorías "
             "y componentes que contiene."),
            'Eliminar',
            wx.YES_NO | wx.ICON_QUESTION
        )

        if dlg.ShowModal() == wx.ID_YES:
            if self.database_temp.category_delete(itemData["id"]):
                self.tree.Delete(self.tree.GetSelection())
                self._tree_selection(None)
                self.log.debug(
                    "Category {} deleted correctly".format(itemName)
                )
            else:
                self.log.error("There was an error deleting the category")
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
                category_id = self.database_temp.template_add(
                    dlg.GetValue(),
                    itemData["id"]
                )
                if category_id:
                    newID = category_id[0]
                    self.tree.AppendItem(
                        self.tree.GetSelection(),
                        dlg.GetValue(),
                        image=2,
                        selImage=2,
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
                    self.log.debug(
                        "Template {} added correctly".format(dlg.GetValue())
                    )
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
                self.log.error(
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

    def _template_ren(self, event):
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
                self.database_temp.template_ren(dlg.GetValue(), itemData["id"])
                itemNewName = dlg.GetValue()
                self.tree.SetItemText(self.tree.GetSelection(), itemNewName)
                self.log.debug(
                    "Template {} renamed to {} correctly".format(
                        itemName,
                        itemNewName
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

    def _template_del(self, event):
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
            ("¿Seguro que desea eliminar la plantilla "
             "{}?.\n\n".format(itemName) +
             "AVISO: Se borrarán todos los grupos y campos que contenga."),
            'Eliminar',
            wx.YES_NO | wx.ICON_QUESTION
        )

        if dlg.ShowModal() == wx.ID_YES:
            if self.database_temp.template_del(itemData["id"]):
                self.tree.Delete(self.tree.GetSelection())
                self._tree_selection(None)
                self.log.debug(
                    "Template {} deleted correctly".format(itemName)
                )
            else:
                self.log.error("There was an error deleting the template")
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

        itemData = self.tree.GetItemData(self.tree.GetSelection())
        dlg = addFieldDialog(self)
        dlg.ShowModal()

        label = dlg.label.GetRealValue()
        type = dlg.type.GetSelection()

        try:
            width = int(dlg.width.GetRealValue())

        except Exception as e:
            self.log.debug("Value maybe is not int: {}".format(e))
            width = None

        if not dlg.closed:
            self.database_temp.field_add(
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
            if self.database_temp.field_delete(itemData):
                self.fieldList.DeleteItem(selected)
                # Fix for disable delete button when no items left
                if (selected - 1) < 0:
                    self.field_bbar.EnableButton(ID_FIELD_UP, False)
                    self.field_bbar.EnableButton(ID_FIELD_DOWN, False)
                    self.field_bbar.EnableButton(ID_FIELD_DELETE, False)
                else:
                    self.fieldList.Select(selected-1)
                self.log.debug("Field {} deleted correctly".format(itemName))
            else:
                self.log.error("There was an error deleting the field")
                return
        dlg.Destroy()

    def _tree_filter(self, parent_item=None, category_id=-1,
                     filter=None, expanded=False):
        if category_id == -1:
            self.tree.DeleteAllItems()

        if not parent_item:
            parent_item = self.tree_root

        cats = self.database_temp._select(
            "Categories",
            items=["*"],
            where=[
                {'key': "Parent", 'value': category_id},
                {'key': "ID", 'comparator': "<>", 'value': -1}
            ],
            order=[
                {'key': "Name"}
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
                  "cat": True if parent_item == self.tree_root else False,
                  "subcat": False if parent_item == self.tree_root else True,
                  "template": False
                }
            )

            child_cat = self.database_temp._select(
                "Categories",
                items=["COUNT(*)"],
                where=[
                    {'key': "Parent", 'value': item[0]}
                ]
            )
            child_com = self.database_temp._select(
                "Templates",
                items=["COUNT(*)"],
                where=[
                    {'key': "Category", 'value': item[0]}
                ]
            )
            if child_cat[0][0] > 0 or child_com[0][0] > 0:
                self._tree_filter(id, item[0], filter, item[3])
            elif filter:
                self.tree.Delete(id)

        templates = self.database_temp._select(
            "Templates",
            items=["ID", "Name"],
            where=[
                {'key': "Category", 'value': category_id}
            ]
        )
        for template in templates:
            found = False if filter else True
            if filter:
                if filter.lower() in template[1].lower():
                    found = True

            if found:
                self.tree.AppendItem(
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
                self.fieldEdBox.Clear(True)
                label = wx.StaticText(
                    self.scrolled_panel,
                    id=wx.ID_ANY,
                    label=("Debe seleccionar un grupo para ver los campos "
                           "en el panel superior\n y seleccionar uno de "
                           "esos campos para poder verlo/editarlo en "
                           "este panel"),
                    style=wx.ALIGN_CENTER
                )
                self.fieldEdBox.Add(
                    label,
                    1,
                    wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL
                )
                self.scrolled_panel.Layout()
                self.scrolled_panel.SetupScrolling()
                # Add data to list
                fields = self.database_temp._select(
                    "Fields",
                    items=[
                        ["Fields", "ID"],
                        ["Fields", "Label"],
                        ["Fields", "Field_type"],
                        ["Fields_Data", "Value"],
                    ],
                    join={
                        'table': "Fields_Data",
                        'where': [
                            {'key': ['Fields_Data', 'Field'], 'value': ['Fields', 'ID']},
                            {'key': ['Fields_Data', 'Key'], 'value': "width"}
                        ]
                    },
                    where=[
                        {'key': ['Fields', 'Template'], 'value': itemData.get('id')}
                    ],
                    order=[
                        {'key': ['Fields', 'Order']}
                    ]
                )
                self.fieldList.Freeze()
                for field in fields:
                    index = self.fieldList.InsertItem(
                        self.fieldList.GetItemCount(),
                        field[1]
                    )
                    self.fieldList.SetItem(index, 1, self.field_kind[field[2]])
                    self.fieldList.SetItem(index, 2, str(field[3] or "Auto"))
                    self.fieldList.SetItemData(index, field[0])
                self.fieldList.Thaw()

            else:
                self.fieldList.Disable()
                self.fieldEdBox.Clear(True)
                label = wx.StaticText(
                    self.scrolled_panel,
                    id=wx.ID_ANY,
                    label=("Debe seleccionar un grupo para ver los campos "
                           "en el panel superior\n y seleccionar uno de "
                           "esos campos para poder verlo/editarlo en "
                           "este panel"),
                    style=wx.ALIGN_CENTER
                )
                self.fieldEdBox.Add(
                    label,
                    1,
                    wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL
                )
                self.scrolled_panel.Layout()
                self.scrolled_panel.SetupScrolling()

        if event:
            event.Skip()

    def _tree_item_collapsed(self, event):
        if event.GetItem().IsOk():
            itemData = self.tree.GetItemData(event.GetItem())
            self.database_temp._update(
                'Categories',
                updates=[
                    {'key': 'Expanded', 'value': False}
                ],
                where=[
                    {'key': 'ID', 'value': itemData['id']}
                ],
                auto_commit=True
            )

    def _tree_item_expanded(self, event):
        if event.GetItem().IsOk():
            itemData = self.tree.GetItemData(event.GetItem())
            self.database_temp._update(
                'Categories',
                updates=[
                    {'key': 'Expanded', 'value': True}
                ],
                where=[
                    {'key': 'ID', 'value': itemData['id']}
                ],
                auto_commit=True
            )

    def _tree_drag_start(self, event):
        event.Allow()
        self.dragItem = event.GetItem()

    def _tree_drag_end(self, event):
        # If we dropped somewhere that isn't on top of an item,
        # ignore the event
        if event.GetItem().IsOk():
            target = event.GetItem()
        else:
            return

        # Make sure this member exists.
        try:
            source = self.dragItem
        except Exception as e:
            self.log.debug(
                "Source doesn't exists: {}".format(e)
            )
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

        if not target_data['cat'] and not target_data['subcat']:
            self.log.info(
                "Destination is a component, and only "
                "categories are allowed as destination"
            )
            return

        try:
            if src_data['cat'] or src_data['subcat']:
                self.database_temp._update(
                    'Categories',
                    updates=[
                        {'key': 'Parent', 'value': target_data['id']}
                    ],
                    where=[
                        {'key': 'ID', 'value': src_data['id']}
                    ],
                    auto_commit=True
                )
            else:
                self.database_temp._update(
                    'Templates',
                    updates=[
                        {'key': 'Category', 'value': target_data['id']}
                    ],
                    where=[
                        {'key': 'ID', 'value': src_data['id']}
                    ],
                    auto_commit=True
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
            self.cat_bbar.EnableButton(ID_CAT_RENAME, True)
            self.tem_bbar.EnableButton(ID_TEM_ADD, True)
            self.tem_bbar.EnableButton(ID_TEM_RENAME, False)
            self.tem_bbar.EnableButton(ID_TEM_DELETE, False)
            self.field_bbar.EnableButton(ID_FIELD_ADD, False)
            self.field_bbar.EnableButton(ID_FIELD_UP, False)
            self.field_bbar.EnableButton(ID_FIELD_DOWN, False)
            self.field_bbar.EnableButton(ID_FIELD_DELETE, False)
        elif itemData.get("subcat", False):
            self.cat_bbar.EnableButton(ID_CAT_ADDSUB, False)
            self.cat_bbar.EnableButton(ID_CAT_DELETE, True)
            self.cat_bbar.EnableButton(ID_CAT_RENAME, True)
            self.tem_bbar.EnableButton(ID_TEM_ADD, True)
            self.tem_bbar.EnableButton(ID_TEM_RENAME, False)
            self.tem_bbar.EnableButton(ID_TEM_DELETE, False)
            self.field_bbar.EnableButton(ID_FIELD_ADD, False)
            self.field_bbar.EnableButton(ID_FIELD_UP, False)
            self.field_bbar.EnableButton(ID_FIELD_DOWN, False)
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
                self.field_bbar.EnableButton(ID_FIELD_UP, False)
                self.field_bbar.EnableButton(ID_FIELD_DOWN, False)
                self.field_bbar.EnableButton(ID_FIELD_DELETE, False)
            else:
                self.field_bbar.EnableButton(ID_FIELD_UP, True)
                self.field_bbar.EnableButton(ID_FIELD_DOWN, True)
                self.field_bbar.EnableButton(ID_FIELD_DELETE, True)

    def _searchText(self, event):
        searchText = self.search.GetValue()
        self.tree.Freeze()
        if len(searchText) > 2:
            self._tree_filter(filter=searchText)
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

    def _fieldDataSave(self, event):
        selected = self.fieldList.GetFirstSelected()
        fieldKind = self.fieldList.GetItemText(selected, 1)
        if selected == -1:
            return False
        selected_id = self.fieldList.GetItemData(selected)
        selected_data = self.database_temp.field_get_data(selected_id)
        if not selected_data:
            return False

        if (fieldKind.lower() == "combobox" and
                self.fields['from_values'].GetSelection() == -1):
            dlg = wx.MessageDialog(
                None,
                "El campo de Origen de datos no puede estar vacío",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False
        # Updating component
        try:
            # Base items
            items_input = [
                'width'
            ]
            items_checkbox = [
                'required',
                'in_name',
                'show_label',
                'in_name_label',
                'in_name_label_separator',
                'join_previous',
                'no_space'
            ]
            items_combobox = [
            ]
            # Conditional items
            if fieldKind.lower() == "input":
                items_input.append('placeholder')
                items_input.append('default')
            elif fieldKind.lower() == "checkbox":
                items_checkbox.append('default')
            elif fieldKind.lower() == "combobox":
                items_combobox.append('from_values')
                items_checkbox.append('ordered')

            # Updating Data
            self.database_temp._update(
                'Fields',
                updates=[
                    {'key': 'Label', 'value': self.fields['label'].GetRealValue()}
                ],
                where=[
                    {'key': 'ID', 'value': selected_id}
                ],
                auto_commit=True
            )
            for item in items_input:
                self.database_temp._insert_or_update(
                    'Fields_data',
                    items=[
                        "Field",
                        "Key",
                        "Value"
                    ],
                    values=[
                        selected_id,
                        item,
                        self.fields[item].GetRealValue()
                    ],
                    conflict=[
                        "Field",
                        "Key"
                    ]
                )

            for item in items_checkbox:
                self.database_temp._insert_or_update(
                    'Fields_data',
                    items=[
                        "Field",
                        "Key",
                        "Value"
                    ],
                    values=[
                        selected_id,
                        item,
                        str(self.fields[item].GetValue())
                    ],
                    conflict=[
                        "Field",
                        "Key"
                    ]
                )

            for item in items_combobox:
                self.database_temp._insert_or_update(
                    'Fields_data',
                    items=[
                        "Field",
                        "Key",
                        "Value"
                    ],
                    values=[
                        selected_id,
                        item,
                        str(
                            self.fields[item].GetClientData(
                                self.fields[item].GetSelection(),
                            )
                        )
                    ],
                    conflict=[
                        "Field",
                        "Key"
                    ]
                )
                default_sel = self.fields['default'].GetSelection()
                default_data = None
                if default_sel != -1:
                    default_data = self.fields['default'].GetClientData(
                        self.fields['default'].GetSelection()
                    )
                else:
                    self.log.warning("There's no data in default ComboBox")

                self.database_temp._insert_or_update(
                    'Fields_data',
                    items=[
                        "Field",
                        "Key",
                        "Value"
                    ],
                    values=[
                        selected_id,
                        "default",
                        str(default_data)
                    ],
                    conflict=[
                        "Field",
                        "Key"
                    ]
                )

            self.database_temp.conn.commit()

            width = self.fields['width'].GetRealValue()
            if width == "":
                width = "Auto"
            self.fieldList.SetItem(
                selected,
                0,
                self.fields['label'].GetRealValue()
            )
            self.fieldList.SetItem(selected, 2, width)

            dlg = wx.MessageDialog(
                None,
                "Se han guardado los cambios",
                'Correcto',
                wx.OK | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()
            return True

        except Exception as e:
            self.log.error(
                "There was an error updating the template "
                "in database: {}".format(e)
            )
            self.database_temp.conn.rollback()
            dlg = wx.MessageDialog(
                None,
                "Error actualizando la plantilla: {}".format(e),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

    def _defaultComboUpdate(self, event):
        selected_tree = self.fieldList.GetFirstSelected()
        selected_id = self.fieldList.GetItemData(selected_tree)
        selected_data = self.database_temp.field_get_data(selected_id)
        selected = self.fields['from_values'].GetSelection()
        self.fields['default'].Clear()
        if selected != -1:
            tID = self.fields['from_values'].GetClientData(selected)
            values = self.database_temp._select(
                "Values",
                items=[
                    "ID",
                    "Value"
                ],
                where=[
                    {'key': "Group", 'value': tID}
                ],
                order=[
                    {'key': "Order"}
                ]
            )
            for group in values:
                self.fields['default'].Append(group[1], group[0])
            self.fields['default'].SetSelection(0)
            for comboid in range(0, self.fields['default'].GetCount()):
                tID = self.fields['default'].GetClientData(comboid)
                if (
                    selected_data['field_data'].get(
                        "default",
                        "-1"
                    ) == str(tID)
                ):
                    self.fields['default'].SetSelection(comboid)
                    break

    def _fieldPanelUpdate(self, event):
        self.modified = False
        selected = self.fieldList.GetFirstSelected()
        try:
            del self.fields
        except Exception as e:
            self.log.warning("Error deleting variable {}".format(e))
            pass

        self.fields = {}
        if selected != -1:
            selected_id = self.fieldList.GetItemData(selected)
            selected_data = self.database_temp.field_get_data(selected_id)
            if not selected_data:
                return False

            self.scrolled_panel.Freeze()
            self.field_bbar.EnableButton(ID_FIELD_DELETE, True)
            self.field_bbar.EnableButton(ID_FIELD_UP, True)
            self.field_bbar.EnableButton(ID_FIELD_DOWN, True)
            fieldKind = self.fieldList.GetItemText(selected, 1)
            self.fieldEdBox.Clear(True)

            self.fieldEdBox.AddSpacer(self.border)
            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(
                    self.scrolled_panel,
                    -1,
                    "Etiqueta",
                    size=(self.label_size, 15)
                ),
                0,
                wx.EXPAND | wx.TOP,
                5
            )
            self.fields['label'] = PlaceholderTextCtrl.PlaceholderTextCtrl(
                self.scrolled_panel,
                value=selected_data['label'],
                placeholder="Etiqueta del campo (obligatoria)"
            )
            box.Add(self.fields['label'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)

            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(
                    self.scrolled_panel,
                    -1,
                    "Ancho",
                    size=(self.label_size, 15)
                ),
                0,
                wx.EXPAND | wx.TOP,
                5
            )
            self.fields['width'] = PlaceholderTextCtrl.PlaceholderTextCtrl(
                self.scrolled_panel,
                value=selected_data['field_data'].get("width", None) or "",
                placeholder="Ancho del control (vacío para automático)"
            )
            box.Add(self.fields['width'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)

            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(
                    self.scrolled_panel,
                    -1,
                    "Obligatorio",
                    size=(self.label_size, 15)
                ),
                0,
                wx.EXPAND
            )
            self.fields['required'] = wx.CheckBox(
                self.scrolled_panel,
                id=wx.ID_ANY
            )
            self.fields['required'].SetValue(
                strToValue.strToValue(
                    selected_data['field_data'].get(
                        "required",
                        "false"
                    ),
                    "bool"
                )
            )
            self.fields['required'].SetToolTip(
                "Marca el campo como obligatorio "
                "para poder guardar el componente"
            )
            box.Add(self.fields['required'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)

            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(
                    self.scrolled_panel,
                    -1,
                    "Mostrar en nombre",
                    size=(self.label_size, 15)
                ),
                0,
                wx.EXPAND
            )
            self.fields['in_name'] = wx.CheckBox(
                self.scrolled_panel,
                id=wx.ID_ANY
            )
            self.fields['in_name'].SetValue(
                strToValue.strToValue(
                    selected_data['field_data'].get("in_name", "false"),
                    "bool"
                )
            )
            self.fields['in_name'].SetToolTip(
                "Mostrar este campo en el nombre "
                "de componente que se generará"
            )
            box.Add(self.fields['in_name'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)

            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(
                    self.scrolled_panel,
                    -1,
                    "Etiqueta en nombre",
                    size=(self.label_size, 15)
                ),
                0,
                wx.EXPAND
            )
            self.fields['in_name_label'] = wx.CheckBox(
                self.scrolled_panel,
                id=wx.ID_ANY
            )
            self.fields['in_name_label'].SetValue(
                strToValue.strToValue(
                    selected_data['field_data'].get("in_name_label", "false"),
                    "bool"
                )
            )
            self.fields['in_name_label'].SetToolTip(
                "Mostrar etiqueta al añadir componente"
            )
            box.Add(self.fields['in_name_label'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)

            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(
                    self.scrolled_panel,
                    -1,
                    "Separador en etiqueta",
                    size=(self.label_size, 15)
                ),
                0,
                wx.EXPAND
            )
            self.fields['in_name_label_separator'] = wx.CheckBox(
                self.scrolled_panel,
                id=wx.ID_ANY
            )
            self.fields['in_name_label_separator'].SetValue(
                strToValue.strToValue(
                    selected_data['field_data'].get(
                        "in_name_label_separator",
                        "true"
                    ),
                    "bool"
                )
            )
            self.fields['in_name_label_separator'].SetToolTip(
                "Mostrar separador de la etiqueta"
            )
            box.Add(self.fields['in_name_label_separator'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)

            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(
                    self.scrolled_panel,
                    -1,
                    "Etiqueta en editor",
                    size=(self.label_size, 15)
                ),
                0,
                wx.EXPAND
            )
            self.fields['show_label'] = wx.CheckBox(
                self.scrolled_panel,
                id=wx.ID_ANY
            )
            self.fields['show_label'].SetValue(
                strToValue.strToValue(
                    selected_data['field_data'].get("show_label", "true"),
                    "bool"
                )
            )
            self.fields['show_label'].SetToolTip(
                "Mostrar etiqueta al añadir componente"
            )
            box.Add(self.fields['show_label'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)

            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(
                    self.scrolled_panel,
                    -1,
                    "Fusión con anterior",
                    size=(self.label_size, 15)
                ),
                0,
                wx.EXPAND
            )
            self.fields['join_previous'] = wx.CheckBox(
                self.scrolled_panel,
                id=wx.ID_ANY
            )
            self.fields['join_previous'].SetValue(
                strToValue.strToValue(
                    selected_data['field_data'].get("join_previous", "false"),
                    "bool"
                )
            )
            self.fields['join_previous'].SetToolTip(
                "Este campo se muestra en la misma línea que el "
                "anterior en la pantalla de añadir componente"
            )
            box.Add(self.fields['join_previous'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)

            box = wx.BoxSizer(wx.HORIZONTAL)
            box.AddSpacer(self.border)
            box.Add(
                wx.StaticText(
                    self.scrolled_panel,
                    -1,
                    "Sin espacio",
                    size=(self.label_size, 15)
                ),
                0,
                wx.EXPAND
            )
            self.fields['no_space'] = wx.CheckBox(
                self.scrolled_panel,
                id=wx.ID_ANY
            )
            self.fields['no_space'].SetValue(
                strToValue.strToValue(
                    selected_data['field_data'].get("no_space", "false"),
                    "bool"
                )
            )
            self.fields['no_space'].SetToolTip(
                "El texto de este campo se unirá con el texto del campo "
                "anterior sin dejar espacio entre ellos, al ser mostrado "
                "en el nombre, ventana de detalles o similar"
            )
            box.Add(self.fields['no_space'], -1, wx.EXPAND)
            box.AddSpacer(self.border)
            self.fieldEdBox.Add(box, 0, wx.EXPAND)
            self.fieldEdBox.AddSpacer(self.between_items)

            if fieldKind.lower() == "input":
                box = wx.BoxSizer(wx.HORIZONTAL)
                box.AddSpacer(self.border)
                box.Add(
                    wx.StaticText(
                        self.scrolled_panel,
                        -1,
                        "Placeholder",
                        size=(self.label_size, 15)
                    ),
                    0,
                    wx.EXPAND
                )
                self.fields['placeholder'] = PlaceholderTextCtrl.PlaceholderTextCtrl(
                    self.scrolled_panel,
                    value=selected_data['field_data'].get("placeholder", ""),
                    placeholder="Mostrado cuando el campo no tiene texto"
                )
                self.fields['placeholder'].SetToolTip(
                    "Texto de ayuda con campo vacío"
                )
                box.Add(self.fields['placeholder'], -1, wx.EXPAND)
                box.AddSpacer(self.border)
                self.fieldEdBox.Add(box, 0, wx.EXPAND)
                self.fieldEdBox.AddSpacer(self.between_items)
                box = wx.BoxSizer(wx.HORIZONTAL)
                box.AddSpacer(self.border)
                box.Add(
                    wx.StaticText(
                        self.scrolled_panel,
                        -1,
                        "Default",
                        size=(self.label_size, 15)
                    ),
                    0,
                    wx.EXPAND
                )
                self.fields['default'] = PlaceholderTextCtrl.PlaceholderTextCtrl(
                    self.scrolled_panel,
                    value=selected_data['field_data'].get("default", ""),
                    placeholder="Texto por defecto del campo"
                )
                self.fields['default'].SetToolTip(
                    "Indica el valor por defeco de este campo"
                )
                box.Add(self.fields['default'], -1, wx.EXPAND)
                box.AddSpacer(self.border)
                self.fieldEdBox.Add(box, 0, wx.EXPAND)
                self.fieldEdBox.AddSpacer(self.between_items)
            elif fieldKind.lower() == "checkbox":
                box = wx.BoxSizer(wx.HORIZONTAL)
                box.AddSpacer(self.border)
                box.Add(
                    wx.StaticText(
                        self.scrolled_panel,
                        -1,
                        "Default",
                        size=(self.label_size, 15)
                    ),
                    0,
                    wx.EXPAND
                )
                self.fields['default'] = wx.CheckBox(
                    self.scrolled_panel,
                    id=wx.ID_ANY
                )
                self.fields['default'].SetValue(
                    strToValue.strToValue(
                        selected_data['field_data'].get("default", "false"),
                        "bool"
                    )
                )
                self.fields['default'].SetToolTip(
                    "Indica el valor por defeco de este campo"
                )
                box.Add(self.fields['default'], -1, wx.EXPAND)
                box.AddSpacer(self.border)
                self.fieldEdBox.Add(box, 0, wx.EXPAND)
                self.fieldEdBox.AddSpacer(self.between_items)
            elif fieldKind.lower() == "combobox":
                box = wx.BoxSizer(wx.HORIZONTAL)
                box.AddSpacer(self.border)
                box.Add(
                    wx.StaticText(
                        self.scrolled_panel,
                        -1,
                        "Origen de datos",
                        size=(self.label_size, 15)
                    ),
                    0,
                    wx.EXPAND | wx.TOP,
                    5
                )
                self.fields['from_values'] = wx.ComboBox(
                    self.scrolled_panel,
                    style=wx.CB_READONLY | wx.CB_DROPDOWN | wx.CB_SORT
                )
                values = self.database_temp._select(
                    "Values_group",
                    items=[
                        "ID",
                        "Name"
                    ]
                )
                for group in values:
                    self.fields['from_values'].Append(group[1], group[0])
                self.fields['from_values'].SetSelection(0)
                for comboid in range(0, self.fields['from_values'].GetCount()):
                    tID = self.fields['from_values'].GetClientData(comboid)
                    if (
                        selected_data['field_data'].get(
                            "from_values",
                            "-1"
                        ) == str(tID)
                    ):
                        self.fields['from_values'].SetSelection(comboid)
                        break

                box.Add(self.fields['from_values'], -1, wx.EXPAND)
                self.fields['from_values'].Bind(
                    wx.EVT_COMBOBOX,
                    self._defaultComboUpdate
                )
                box.AddSpacer(self.border)
                self.fieldEdBox.Add(box, 0, wx.EXPAND)
                self.fieldEdBox.AddSpacer(self.between_items)

                box = wx.BoxSizer(wx.HORIZONTAL)
                box.AddSpacer(self.border)
                box.Add(
                    wx.StaticText(
                        self.scrolled_panel,
                        -1,
                        "Default",
                        size=(self.label_size, 15)
                    ),
                    0,
                    wx.EXPAND
                )
                self.fields['default'] = wx.ComboBox(
                    self.scrolled_panel,
                    style=wx.CB_READONLY | wx.CB_DROPDOWN
                )
                self.fields['default'].SetToolTip(
                    "Indica el valor por defeco de este campo"
                )
                self._defaultComboUpdate(None)

                box.Add(self.fields['default'], -1, wx.EXPAND)
                box.AddSpacer(self.border)
                self.fieldEdBox.Add(box, 0, wx.EXPAND)
                self.fieldEdBox.AddSpacer(self.between_items)

                box = wx.BoxSizer(wx.HORIZONTAL)
                box.AddSpacer(self.border)
                box.Add(
                    wx.StaticText(
                        self.scrolled_panel,
                        -1,
                        "Ordenar",
                        size=(self.label_size, 15)
                    ),
                    0,
                    wx.EXPAND
                )
                self.fields['ordered'] = wx.CheckBox(
                    self.scrolled_panel,
                    id=wx.ID_ANY
                )
                self.fields['ordered'].SetValue(
                    strToValue.strToValue(
                        selected_data['field_data'].get("ordered", "false"),
                        "bool"
                    )
                )
                self.fields['ordered'].SetToolTip(
                    "Ordenar los items del combobox por orden alfabético"
                )
                box.Add(self.fields['ordered'], -1, wx.EXPAND)
                box.AddSpacer(self.border)
                self.fieldEdBox.Add(box, 0, wx.EXPAND)
                self.fieldEdBox.AddSpacer(self.between_items)

            # Buttons
            btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
            btn_add = wx.Button(self.scrolled_panel, label="Guardar")
            btn_add.Bind(wx.EVT_BUTTON, self._fieldDataSave)
            btn_cancel = wx.Button(self.scrolled_panel, label="Reiniciar")
            btn_cancel.Bind(wx.EVT_BUTTON, self._fieldPanelUpdate)
            btn_sizer.AddSpacer(10)
            btn_sizer.Add(btn_add)
            btn_sizer.AddSpacer(30)
            btn_sizer.Add(btn_cancel)
            btn_sizer.AddSpacer(10)
            self.fieldEdBox.Add(
                btn_sizer,
                0,
                wx.ALL | wx.ALIGN_CENTER_HORIZONTAL,
                10
            )
            # Draw the panel
            self.scrolled_panel.Layout()
            self.scrolled_panel.Thaw()
            self.scrolled_panel.SetupScrolling()
        else:
            self.field_bbar.EnableButton(ID_FIELD_DELETE, False)
            self.field_bbar.EnableButton(ID_FIELD_UP, False)
            self.field_bbar.EnableButton(ID_FIELD_DOWN, False)
            self.fieldEdBox.Clear(True)
            label = wx.StaticText(
                self.scrolled_panel,
                id=wx.ID_ANY,
                label=("Debe seleccionar un grupo para ver los campos en "
                       "el panel superior\n y seleccionar uno de esos "
                       "campos para poder verlo/editarlo en este panel"),
                style=wx.ALIGN_CENTER
            )
            self.fieldEdBox.Add(
                label,
                1,
                wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL
            )
            self.scrolled_panel.Layout()
            self.scrolled_panel.SetupScrolling()

    def _valuesManager(self, event):
        manager = manageValuesGroups(self)
        manager.ShowModal()

        if manager.updated and self.fields.get('from_values', False):
            selected = self.fields['from_values'].GetSelection()
            oldSelection = None
            if selected != -1:
                oldSelection = self.fields['from_values'].GetString(selected)

            self.fields['from_values'].Clear()
            values = self.database_temp._select(
                "Values_group",
                items=[
                    "ID",
                    "Name"
                ]
            )
            for group in values:
                self.fields['from_values'].Append(group[1], group[0])

            if selected != -1:
                found = self.fields['from_values'].FindString(oldSelection)
                if found == wx.NOT_FOUND:
                    self.fields['from_values'].SetSelection(0)
                else:
                    self.fields['from_values'].SetSelection(found)
            else:
                self.fields['from_values'].SetSelection(0)

            self._defaultComboUpdate(None)

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
                self.database_temp.vacuum()
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

    def _move_down_field(self, event):
        selected = self.fieldList.GetFirstSelected()
        if selected == -1:
            dlg = wx.MessageDialog(
                None,
                "Debe seleccionar un valor",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if selected == self.fieldList.GetColumnCount()-1:
            dlg = wx.MessageDialog(
                None,
                "El valor seleccionado no puede moverse abajo",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        try:
            sel_labels = []
            sel_data = self.fieldList.GetItemData(selected)
            up_labels = []
            up_data = self.fieldList.GetItemData(selected+1)

            for i in range(0, self.fieldList.GetColumnCount()):
                sel_labels.append(self.fieldList.GetItemText(selected, i))
                up_labels.append(self.fieldList.GetItemText(selected+1, i))

            self.database_temp._update(
                "Fields",
                updates=[
                    {'key': "Order", 'value': selected+1}
                ],
                where=[
                    {'key': "ID", 'value': sel_data}
                ]
            )
            self.database_temp._update(
                "Fields",
                updates=[
                    {'key': "Order", 'value': selected}
                ],
                where=[
                    {'key': "ID", 'value': up_data}
                ]
            )

            for i in range(0, self.fieldList.GetColumnCount()):
                self.fieldList.SetItem(selected, i, up_labels[i])
                self.fieldList.SetItem(selected+1, i, sel_labels[i])

            self.fieldList.SetItemData(selected, up_data)
            self.fieldList.SetItemData(selected+1, sel_data)
            self.database_temp.conn.commit()
            self.log.debug("Setting below item (moved): {}".format(selected+1))
            self.fieldList.Select(selected+1)

        except Exception as e:
            self.log.error(
                "There was an error moving the value down: {}".format(e)
            )
            dlg = wx.MessageDialog(
                None,
                "Ocurrió un error moviendo el valor abajo: {}".format(e),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

    def _move_up_field(self, event):
        selected = self.fieldList.GetFirstSelected()
        if selected == -1:
            dlg = wx.MessageDialog(
                None,
                "Debe seleccionar un valor",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if selected == 0:
            dlg = wx.MessageDialog(
                None,
                "El valor seleccionado no puede moverse arriba",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        try:
            sel_labels = []
            sel_data = self.fieldList.GetItemData(selected)
            up_labels = []
            up_data = self.fieldList.GetItemData(selected-1)

            for i in range(0, self.fieldList.GetColumnCount()):
                sel_labels.append(self.fieldList.GetItemText(selected, i))
                up_labels.append(self.fieldList.GetItemText(selected-1, i))

            self.database_temp._update(
                "Fields",
                updates=[
                    {'key': "Order", 'value': selected-1}
                ],
                where=[
                    {'key': "ID", 'value': sel_data}
                ]
            )
            self.database_temp._update(
                "Fields",
                updates=[
                    {'key': "Order", 'value': selected}
                ],
                where=[
                    {'key': "ID", 'value': up_data}
                ]
            )

            for i in range(0, self.fieldList.GetColumnCount()):
                self.fieldList.SetItem(selected, i, up_labels[i])
                self.fieldList.SetItem(selected-1, i, sel_labels[i])

            self.fieldList.SetItemData(selected, up_data)
            self.fieldList.SetItemData(selected-1, sel_data)
            self.database_temp.conn.commit()
            self.log.debug("Setting above item (moved): {}".format(selected-1))
            self.fieldList.Select(selected-1)

        except Exception as e:
            self.log.error(
                "There was an error moving the value up: {}".format(e)
            )
            dlg = wx.MessageDialog(
                None,
                "Ocurrió un error moviendo el valor arriba: {}".format(e),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            title="Gestión de Plantillas",
            size=(900, 900),
            style=wx.DEFAULT_FRAME_STYLE
        )

        # Changing the icon
        icon = wx.Icon(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                'icon.ico'
            ),
            wx.BITMAP_TYPE_ICO
        )
        self.SetIcon(icon)

        self.log = parent.log
        self.log.info("Loading main windows...")
        self.Bind(wx.EVT_CLOSE, self.exitGUI)

        # Variables
        self.database_temp = parent.database_temp
        self.timer = None
        self.last_filter = None
        self.last_selected_item = None
        self.field_kind = globals.field_kind
        self.fields = {}
        self.border = 20
        self.between_items = 5
        self.label_size = 130
        self.modified = False

        # Creating splitter
        self.log.debug("Creating splitter")
        # Main Splitter
        splitter = wx.SplitterWindow(self, -1, style=wx.RAISED_BORDER)

        # Ribbon Bar
        ribbon = RB.RibbonBar(self, -1)
        page = RB.RibbonPage(ribbon, wx.ID_ANY, "Page")

        # #--------------------##
        # ## Panel Categorías ###
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
            ("Elimina una categoría o subcategoría, incluyendo "
             "todas las subcategorías y componentes que hay en ella")
        )

        # #--------------------# #
        # ## Panel Templates ## #
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
            ("Elimina una plantilla, incluyendo todos los "
             "grupos y campos que hay en ella")
        )

        # #--------------------# #
        # ## Panel Items field ## #
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
            'Añade un campo básico'
        )
        # Field up
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'field_up.png'
            )
        )
        self.field_bbar.AddSimpleButton(
            ID_FIELD_UP,
            "Subir",
            image,
            'Sube el campo una posición'
        )
        # Field down
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'field_down.png'
            )
        )
        self.field_bbar.AddSimpleButton(
            ID_FIELD_DOWN,
            "Bajar",
            image,
            'Baja el campo una posición'
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

        # #--------------------# #
        # ## Panel Data Source ## #
        bFields = RB.RibbonPanel(page, wx.ID_ANY, "Herramientas")
        self.tools_bbar = RB.RibbonButtonBar(bFields)
        # Add field
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'data_source.png'
            )
        )
        self.tools_bbar.AddSimpleButton(
            ID_TOOLS_MANAGE,
            "Gestionar Orígenes de Datos",
            image,
            'Gestiona los orígenes de datos'
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
        self.tem_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._template_create,
            id=ID_TEM_ADD
        )
        self.tem_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._template_ren,
            id=ID_TEM_RENAME
        )
        self.tem_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._template_del,
            id=ID_TEM_DELETE
        )
        self.field_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._field_create,
            id=ID_FIELD_ADD
        )
        self.field_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._move_up_field,
            id=ID_FIELD_UP
        )
        self.field_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._move_down_field,
            id=ID_FIELD_DOWN
        )
        self.field_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._field_delete,
            id=ID_FIELD_DELETE
        )
        self.tools_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._valuesManager,
            id=ID_TOOLS_MANAGE
        )
        self.tools_bbar.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._vacuum,
            id=ID_TOOLS_VACUUM
        )

        self.cat_bbar.EnableButton(ID_CAT_ADDSUB, False)
        self.cat_bbar.EnableButton(ID_CAT_RENAME, False)
        self.cat_bbar.EnableButton(ID_CAT_DELETE, False)
        self.tem_bbar.EnableButton(ID_TEM_ADD, False)
        self.tem_bbar.EnableButton(ID_TEM_RENAME, False)
        self.tem_bbar.EnableButton(ID_TEM_DELETE, False)
        self.field_bbar.EnableButton(ID_FIELD_ADD, False)
        self.field_bbar.EnableButton(ID_FIELD_UP, False)
        self.field_bbar.EnableButton(ID_FIELD_DOWN, False)
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
        self.search = self.search = wx.SearchCtrl(
            lPan,
            style=wx.TE_PROCESS_ENTER | wx.RAISED_BORDER
        )
        self.search.ShowCancelButton(True)
        self.search.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self._searchText)
        self.search.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self._cancelSearch)
        self.search.Bind(wx.EVT_TEXT_ENTER, self._searchText)

        lPanBox.Add(self.search, 0, wx.EXPAND)

        # Templates Tree
        self.tree = CTreeCtrl.CTreeCtrl(
            lPan,
            wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_LINES_AT_ROOT
        )
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
          "template.png"
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

        fieldLstPanel = wx.Panel(rPan)
        fieldLstBox = wx.BoxSizer(wx.VERTICAL)
        fieldLstPanel.SetSizer(fieldLstBox)
        self.scrolled_panel = scrolled.ScrolledPanel(
            rPan,
            style=wx.RAISED_BORDER
        )
        self.fieldEdBox = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_panel.SetSizer(self.fieldEdBox)

        self.fieldList = wx.ListCtrl(
            fieldLstPanel,
            id=wx.ID_ANY,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES
        )
        fieldLstBox.Add(self.fieldList, 1, wx.EXPAND)
        self.fieldList.AppendColumn("Etiqueta", wx.LIST_FORMAT_CENTRE, 262)
        self.fieldList.AppendColumn("Tipo", wx.LIST_FORMAT_CENTRE)
        self.fieldList.AppendColumn("Ancho", wx.LIST_FORMAT_CENTRE)
        self.fieldList.Bind(wx.EVT_LIST_ITEM_SELECTED, self._fieldPanelUpdate)
        self.fieldList.Bind(
            wx.EVT_LIST_ITEM_DESELECTED,
            self._fieldPanelUpdate
        )
        self.fieldList.Disable()

        label = wx.StaticText(
            self.scrolled_panel,
            id=wx.ID_ANY,
            label=("Debe seleccionar un grupo para ver los campos "
                   "en el panel superior\n y seleccionar uno de esos "
                   "campos para poder verlo/editarlo en este panel"),
            style=wx.ALIGN_CENTER
        )

        self.fieldEdBox.Add(
            label,
            1,
            wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL
        )

        rPan.SplitHorizontally(fieldLstPanel, self.scrolled_panel)
        rPan.SetSashGravity(0.4)

        # Updating tree
        self._tree_filter()
