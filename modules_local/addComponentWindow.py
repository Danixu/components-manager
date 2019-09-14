# -*- coding: utf-8 -*-

'''
22 Aug 2019
@autor: Daniel Carrasco
'''

import wx
import wx.lib.scrolledpanel as scrolled
from widgets import PlaceholderTextCtrl
from modules import strToValue
import globals
#from threading import Timer

# Load main data
app = wx.App()
globals.init()

class addComponentWindow(wx.Dialog):
###=== Exit Function ===###
    def close_dialog(self, event):
        self.closed = True
        self.Destroy()

    #----------------------------------------------------------------------
    def __init__(self, parent = None, component_id = None, default_template = None):
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
        self.default_template = default_template

        # Si se está editando, se sacan los datos
        try:
          del(self.edit_component)

        except:
          pass

        # Getting component data on edit
        self.edit_component = {}
        if self.component_id:
            component = self.parent.database_comp.query(
                """SELECT * FROM [Components] WHERE [ID] = ?;""", 
                (
                    self.component_id, 
                )
            )
            component_data = self.parent.database_comp.query(
                """SELECT * FROM [Components_data] WHERE [Component] = ?;""", 
                (
                    self.component_id, 
                )
            )
            self.edit_component = {
                "template": component[0][2]
            }
            for item in component_data:
              self.edit_component.update({ item[2]: item[3] })

            category = self.parent.database_temp.query(
                """SELECT [Category] FROM [Templates] WHERE [ID] = ?;""",
                (
                    self.edit_component["template"],
                )
            )
            parent = self.parent.database_temp.query(
                """SELECT [ID], [Parent] FROM [Categories] WHERE [ID] = ?;""",
                (
                    category[0][0],
                )
            )

            if parent[0][1] == -1:
                self.edit_component['category'] = parent[0][0]
                self.edit_component['subcategory'] = -1
            else:
                self.edit_component['category'] = parent[0][1]
                self.edit_component['subcategory'] = parent[0][0]

        elif self.default_template:
            self.edit_component = {
                "template": self.default_template
            }
            category = self.parent.database_temp.query(
                """SELECT [Category] FROM [Templates] WHERE [ID] = ?;""",
                (
                    self.edit_component["template"],
                )
            )
            parent = self.parent.database_temp.query(
                """SELECT [ID], [Parent] FROM [Categories] WHERE [ID] = ?;""",
                (
                    category[0][0],
                )
            )

            if parent[0][1] == -1:
                self.edit_component['category'] = parent[0][0]
                self.edit_component['subcategory'] = -1
            else:
                self.edit_component['category'] = parent[0][1]
                self.edit_component['subcategory'] = parent[0][0]

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

        # Combobox Category selector
        catSizer = wx.BoxSizer(wx.HORIZONTAL)
        catSizer.AddSpacer(self.padding)
        self.catCombo = wx.ComboBox(self.panel, choices = [], style=wx.CB_READONLY|wx.CB_SORT|wx.CB_DROPDOWN)
        cats = self.parent.database_temp.query(
            """SELECT [ID], [Name] FROM [Categories] WHERE [Parent] = -1 AND ID <> -1;"""
        )
        for item in cats:
            self.catCombo.Append(item[1], item[0])
        self.catCombo.Bind(wx.EVT_COMBOBOX, self._onCategorySelection)
        catSizer.Add(self.catCombo, 1, wx.EXPAND)
        catSizer.AddSpacer(self.padding)

        # Combobox Subcategory selector
        subCatSizer = wx.BoxSizer(wx.HORIZONTAL)
        subCatSizer.AddSpacer(self.padding)
        self.subCatCombo = wx.ComboBox(self.panel, choices = [], style=wx.CB_READONLY|wx.CB_SORT|wx.CB_DROPDOWN)
        self.subCatCombo.Bind(wx.EVT_COMBOBOX, self._onCategorySelection)
        subCatSizer.Add(self.subCatCombo, 1, wx.EXPAND)
        subCatSizer.AddSpacer(self.padding)

        # Combobox Component kind selector
        compSizer = wx.BoxSizer(wx.HORIZONTAL)
        compSizer.AddSpacer(self.padding)
        self.compCombo = wx.ComboBox(self.panel, choices = [], style=wx.CB_READONLY|wx.CB_SORT|wx.CB_DROPDOWN)
        self.compCombo.Bind(wx.EVT_COMBOBOX, self._onComponentSelection)
        compSizer.Add(self.compCombo, 1, wx.EXPAND)
        compSizer.AddSpacer(self.padding)

        # Final BoxSizer
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.AddSpacer(self.padding)
        panelSizer.Add(catSizer, 0, wx.EXPAND)
        panelSizer.AddSpacer(self.padding)
        panelSizer.Add(subCatSizer, 0, wx.EXPAND)
        panelSizer.AddSpacer(self.padding)
        panelSizer.Add(compSizer, 0, wx.EXPAND)
        panelSizer.AddSpacer(self.padding)
        panelSizer.Add(self.scrolled_panel, 1, wx.EXPAND)
        panelSizer.AddSpacer(20)
        panelSizer.Add(btn_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
        panelSizer.AddSpacer(20)

        self.catCombo.SetSelection(0)
        if self.component_id or self.default_template:
            for comboid in range(0, self.catCombo.GetCount()):
                tID = self.catCombo.GetClientData(comboid)
                if (tID == self.edit_component['category']):
                    self.catCombo.SetSelection(comboid)
                    break
            if self.component_id:
                self.catCombo.Disable()
            self._onCategorySelection(None)
        else:
            self._onCategorySelection(None)
        self.panel.SetSizer(panelSizer)


    def _getComponentControl(self, data, value = None):
        control = None
        field_type = data.get('field_type', -1)

        if globals.field_kind[field_type] == "Input":
            control = PlaceholderTextCtrl.PlaceholderTextCtrl(
                self.scrolled_panel, 
                value = value or data['field_data'].get('default', ""),
                placeholder = data['field_data'].get('placeholder', ""),
                name = 'input',
                size=(
                    strToValue.strToValue(
                        data['field_data'].get('width'), 
                        'int'
                    ),
                    25
                ),
            )

        elif globals.field_kind[field_type] == "ComboBox":
            if data['field_data'].get('width', None):
                style = wx.CB_READONLY|wx.CB_SORT|wx.CB_DROPDOWN
                if not data['field_data'].get('sort', False):
                    style = wx.CB_READONLY|wx.CB_DROPDOWN
                control = wx.ComboBox(
                    self.scrolled_panel, 
                    size=(
                        strToValue.strToValue(
                            data['field_data'].get('width'), 
                            'int'
                        ),
                        25
                    ),
                    style=style,
                    name = 'combobox'
                )
            else:
                style = wx.CB_READONLY|wx.CB_SORT|wx.CB_DROPDOWN
                if not data['field_data'].get('sorted', False):
                    style = wx.CB_READONLY|wx.CB_DROPDOWN
                control = wx.ComboBox(
                    self.scrolled_panel, 
                    style=style,
                    name = 'combobox'
                )

            if data['field_data'].get('from_values', False):
                for item in self.parent.database_temp.query(
                    """SELECT [ID], [Value] FROM [Values] WHERE [Group] = ? ORDER BY [Order];""",
                    (data['field_data']['from_values'],)
                ):
                    control.Append(item[1], item[0])

            toFind = strToValue.strToValue(
                value or data['field_data'].get('default', False),
                "int"
            )
            if toFind:
                for comboid in range(0, control.GetCount()):
                    tID = control.GetClientData(comboid)
                    if (tID == toFind):
                        control.SetSelection(comboid)
                        break

        elif globals.field_kind[field_type] == "CheckBox":
            control = wx.CheckBox(self.scrolled_panel, id=wx.ID_ANY, name = 'checkbox')
            control.SetValue(
                strToValue.strToValue(
                    value or data['field_data'].get('default', False),
                    "bool"
                )
            )

        else:
            self.parent.log.warning("The component input type is not correct {}".format(field_type))

        return control


    def _onCategorySelection(self, event):
        cat = None
        if event == True:
            cat = False
        elif event == None or event == False or event.GetEventObject() == self.catCombo:
            cat = True
        else:
            cat = False

        if cat:
            self.parent.log.debug("Seleccionada categoría")
            self.subCatCombo.Clear()
            self.compCombo.Clear()
            catSel = self.catCombo.GetSelection()
            if catSel == -1:
                self.parent.log.warning("Combo selection -1")
                return
            id = self.catCombo.GetClientData(catSel)
            subCats = self.parent.database_temp.query(
                """SELECT [ID], [Name] FROM [Categories] WHERE [Parent] = ?;""",
                (id,)
            )
            self.subCatCombo.Append("-- Sin subcategoría --", -1)
            self.subCatCombo.SetSelection(0)
            for item in subCats:
                self.subCatCombo.Append(item[1], item[0])
            temps = self.parent.database_temp.query(
                """SELECT [ID], [Name] FROM [Templates] WHERE [Category] = ?;""",
                (id,)
            )
            for item in temps:
                self.compCombo.Append(item[1], item[0])
            if self.compCombo.GetCount() == 0:
                self.compCombo.Append("-- No hay componentes en la categoría seleccionada --", -1)
            self.compCombo.SetSelection(0)
            if self.component_id or self.default_template:
                for comboid in range(0, self.subCatCombo.GetCount()):
                    tID = self.subCatCombo.GetClientData(comboid)
                    if (tID == self.edit_component['subcategory']):
                        self.subCatCombo.SetSelection(comboid)
                        break
                if self.component_id:
                    self.subCatCombo.Disable()
                if self.edit_component['subcategory'] != -1:
                    self._onCategorySelection(True)
                else:
                    for comboid in range(0, self.compCombo.GetCount()):
                        tID = self.compCombo.GetClientData(comboid)
                        if (tID == self.edit_component["template"]):
                            self.compCombo.SetSelection(comboid)
                            break
                    if self.component_id:
                        self.compCombo.Disable()
                    self._onComponentSelection(None)

            else:
                self._onComponentSelection(None)

        else:
            self.parent.log.debug("Seleccionada subcategoría")
            subCatSel = self.subCatCombo.GetSelection()
            if subCatSel == -1:
                self.parent.log.warning("Combo selection -1")
                return
            id = self.subCatCombo.GetClientData(subCatSel)
            if id == -1:
                self.parent.log.debug("No subcategory selected")
                self._onCategorySelection(None)
                return

            self.compCombo.Clear()
            temps = self.parent.database_temp.query(
                """SELECT [ID], [Name] FROM [Templates] WHERE [Category] = ?;""",
                (id,)
            )
            for item in temps:
                self.compCombo.Append(item[1], item[0])
            if self.compCombo.GetCount() == 0:
                self.compCombo.Append("-- No hay componentes en la subcategoría seleccionada --", -1)
            self.compCombo.SetSelection(0)
            if self.component_id or self.default_template:
                for comboid in range(0, self.compCombo.GetCount()):
                    tID = self.compCombo.GetClientData(comboid)
                    if (tID == self.edit_component["template"]):
                        self.compCombo.SetSelection(comboid)
                        break
                if self.component_id:
                    self.compCombo.Disable()
                self._onComponentSelection(None)

            else:
                self._onComponentSelection(None)


    def _onComponentSelection(self, event):
        # Freezing the panel to speed up the change
        # Also avoid the bad looking of the process
        self.scrolled_panel.Freeze()
        self.scrolled_panel.SetupScrolling()
        self.spSizer.Clear(True)
        try:
            del self.inputs
        except:
            pass

        self.inputs = {}

        template = self.compCombo.GetClientData(self.compCombo.GetSelection())
        self.inputs["template"] = template

        self.spSizer.AddSpacer(self.items_spacing)
        iDataBox = wx.BoxSizer(wx.HORIZONTAL)
        iDataBox.AddSpacer(self.padding)
        first_item = True

        for item in self.parent.database_temp.query(
            """SELECT [ID] FROM [Fields] WHERE [Template] = ? ORDER BY [Order]""",
            (template, )
        ):
            field_data = self.parent.database_temp.field_get_data(item[0])

            if not strToValue.strToValue(
                field_data['field_data'].get('join_previous', 'false'), 
                'bool'
            ) and not first_item:
                iDataBox.AddSpacer(self.padding)
                self.spSizer.Add(iDataBox, 0, wx.EXPAND)
                self.spSizer.AddSpacer(self.items_spacing)
                iDataBox = wx.BoxSizer(wx.HORIZONTAL)
                iDataBox.AddSpacer(self.padding)
                first_item = True

            label_text = ""
            if strToValue.strToValue(
                field_data['field_data'].get('show_label', 'true'), 
                'bool'
            ):
                label_text = " {}".format(field_data['label'])

            if first_item or strToValue.strToValue(
                field_data['field_data'].get('show_label', 'true'), 
                'bool'
            ):
                label = wx.StaticText(
                    self.scrolled_panel,
                    id=wx.ID_ANY,
                    label=label_text,
                    size=(
                        self.left_collumn_size if first_item else -1, 
                        15
                    ),
                    style=0,
                )
                if not first_item:
                    iDataBox.AddSpacer(5)
                iDataBox.Add(label, 0, wx.TOP, 7)
                first_item = False

            self.inputs[item[0]] = self._getComponentControl(
                field_data,
                value = self.edit_component.get(item[0], None)
            )
            iDataBox.AddSpacer(5)
            iDataBox.Add(
                self.inputs[item[0]], 
                0 if field_data['field_data'].get('width', False) else -1, 
                wx.TOP, 
                5
            )

        if not first_item:
            iDataBox.AddSpacer(self.padding)
            self.spSizer.Add(iDataBox, 0, wx.EXPAND)

        # Draw the Layout and Unfreeze
        self.scrolled_panel.Layout()
        self.scrolled_panel.Thaw()


    def add_component(self, event):
        categoryData = self.parent.tree.GetItemData(self.parent.tree.GetSelection())

        try:
            componentID = self.parent.database_comp.query(
                """INSERT INTO [Components] ([Category], [Template]) VALUES (?, ?);""",
                (
                    categoryData['id'],
                    self.inputs['template']
                )
            )

            for item, data in self.inputs.items():
                if item in ["template"]:
                    continue
                value = ""
                self.parent.log.debug("Control name: {}".format(data.GetName()))
                if data.GetName() == "input":
                    value = data.GetRealValue()
                elif data.GetName() == "combobox":
                    value = str(data.GetClientData(data.GetSelection()))
                elif data.GetName() == "checkbox":
                    value = str(data.GetValue())
                else:
                    self.parent.log.warning("Wrong control name: {}".format(data.GetName()))
                    continue

                required = self.parent.database_temp.query(
                    """SELECT [value] FROM [Fields_data] WHERE [Field] = ? and [Key] = 'required';""",
                    (
                        item,
                    )
                )
                if len(required) > 0:
                    if required[0][0].lower() == 'true' and value == "":
                        label = self.parent.database_temp.query(
                            """SELECT [Label] FROM [Fields] WHERE [ID] = ?;""",
                            (
                                item,
                            )
                        )
                        dlg = wx.MessageDialog(
                            None, 
                            "El campo {} es obligatorio.".format(label[0][0]),
                            'ERROR',
                            wx.OK | wx.ICON_ERROR
                        )
                        dlg.ShowModal()
                        dlg.Destroy()
                        return False

            for item, data in self.inputs.items():
                if item in ["template"]:
                    continue
                value = ""
                self.parent.log.debug("Control name: {}".format(data.GetName()))
                if data.GetName() == "input":
                    value = data.GetRealValue()
                elif data.GetName() == "combobox":
                    value = str(data.GetClientData(data.GetSelection()))
                elif data.GetName() == "checkbox":
                    value = str(data.GetValue())
                else:
                    self.parent.log.warning("Wrong control name: {}".format(data.GetName()))
                    continue

                self.parent.database_comp.query(
                    """INSERT INTO [Components_data] ([Component], [Field_ID], [Value]) VALUES (?, ?, ?);""",
                    (
                        componentID[0],
                        item,
                        value
                    )
                )

            self.component_id = componentID[0]
            self.parent.database_comp.conn.commit()
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

        except Exception as e:
            self.parent.log.error("There was an error adding the component: {}".format(e))
            self.parent.database_comp.conn.rollback()
            dlg = wx.MessageDialog(
                None, 
                "Ocurrió un error al añadir el componente: {}".format(e),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()


    def update_component(self, event):
        categoryData = self.parent.tree.GetItemData(self.parent.tree.GetSelection())

        try:
            for item, data in self.inputs.items():
                if item in ["template"]:
                    continue
                value = ""
                self.parent.log.debug("Control name: {}".format(data.GetName()))
                if data.GetName() == "input":
                    value = data.GetRealValue()
                elif data.GetName() == "combobox":
                    value = str(data.GetClientData(data.GetSelection()))
                elif data.GetName() == "checkbox":
                    value = str(data.GetValue())
                else:
                    self.parent.log.warning("Wrong control name: {}".format(data.GetName()))
                    continue
                self.parent.database_comp.query(
                    """INSERT INTO [Components_data] ([Component], [Field_ID], [Value]) VALUES (?, ?, ?)
                       ON CONFLICT([Component], [Field_ID]) DO UPDATE SET [Value] = ?;
                    """,
                    (
                        self.component_id,
                        item,
                        value,
                        value,
                    )
                )

            self.parent.database_comp.conn.commit()
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

        except Exception as e:
            self.parent.log.error("There was an error updating the component: {}".format(e))
            self.parent.database_comp.conn.rollback()
            dlg = wx.MessageDialog(
                None, 
                "Ocurrió un error al actualizar el componente: {}".format(e),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()