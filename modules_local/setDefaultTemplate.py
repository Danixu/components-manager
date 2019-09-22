# -*- coding: utf-8 -*-

'''
18 Aug 2019
@autor: Daniel Carrasco
'''
import wx


class setDefaultTemplate(wx.Dialog):
    # ##=== Exit Function ===## #
    def close_dialog(self, event):
        self.closed = True
        self.Destroy()

    def _save(self, event):
        component = self.comboComp.GetClientData(self.comboComp.GetSelection())

        try:
            self.log.debug(
                "Setting the category template to {}".format(component)
            )
            self.parent.database_comp.query(
                """UPDATE [Categories] SET [Template] = ? WHERE [ID] = ?""",
                (
                    component,
                    self.category_id
                )
            )
            self.parent.database_comp.conn.commit()

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
            self.log.error(
                "There was an error updating category " +
                "default template. {}".format(e)
            )
            dlg = wx.MessageDialog(
                None,
                "Ocurrió un error al guardar la plantilla por " +
                "defecto de la categoría.",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()

    def _onCategorySelection(self, event):
        cat = None
        if event is True:
            cat = False
        elif (event is None
              or event is False
              or event.GetEventObject() == self.comboCat):
            cat = True
        else:
            cat = False

        if cat:
            self.log.debug("Seleccionada categoría")
            self.comboSubCat.Clear()
            self.comboComp.Clear()
            catSel = self.comboCat.GetSelection()
            if catSel == -1:
                self.log.warning("Combo selection -1")
                return
            id = self.comboCat.GetClientData(catSel)
            subCats = self.parent.database_temp.query(
                """
                SELECT
                  [ID],
                  [Name]
                FROM
                  [Categories]
                WHERE
                  [Parent] = ?;
                """,
                (id,)
            )
            self.comboSubCat.Append("-- Sin subcategoría --", -1)
            self.comboSubCat.SetSelection(0)
            for item in subCats:
                self.comboSubCat.Append(item[1], item[0])
            temps = self.parent.database_temp.query(
                """
                SELECT
                  [ID],
                  [Name]
                FROM
                  [Templates]
                WHERE
                  [Category] = ?;
                """,
                (id,)
            )
            for item in temps:
                self.comboComp.Append(item[1], item[0])
            if self.comboComp.GetCount() == 0:
                self.comboComp.Append(
                    "-- No hay componentes en la categoría seleccionada --",
                    -1
                )
            self.comboComp.SetSelection(0)
            if self.edit_component['template']:
                for comboid in range(0, self.comboSubCat.GetCount()):
                    tID = self.comboSubCat.GetClientData(comboid)
                    if (tID == self.edit_component['subcategory']):
                        self.comboSubCat.SetSelection(comboid)
                        break
                if self.edit_component['subcategory'] != -1:
                    self._onCategorySelection(True)
                else:
                    for comboid in range(0, self.comboComp.GetCount()):
                        tID = self.comboComp.GetClientData(comboid)
                        if (tID == self.edit_component["template"]):
                            self.comboComp.SetSelection(comboid)
                            break
        else:
            self.log.debug("Seleccionada subcategoría")
            subCatSel = self.comboSubCat.GetSelection()
            if subCatSel == -1:
                self.log.warning("Combo selection -1")
                return
            id = self.comboSubCat.GetClientData(subCatSel)
            if id == -1:
                self.log.debug("No subcategory selected")
                self._onCategorySelection(None)
                return

            self.comboComp.Clear()
            self.comboComp.Append("_Sin plantilla por defecto", None)
            temps = self.parent.database_temp.query(
                """
                SELECT
                  [ID],
                  [Name]
                FROM
                  [Templates]
                WHERE
                  [Category] = ?;
                """,
                (id,)
            )
            for item in temps:
                self.comboComp.Append(item[1], item[0])
            if self.comboComp.GetCount() == 0:
                self.comboComp.Append(
                    "-- No hay componentes en la subcategoría seleccionada --",
                    -1
                )
            self.comboComp.SetSelection(0)
            if self.edit_component['template']:
                for comboid in range(0, self.comboComp.GetCount()):
                    tID = self.comboComp.GetClientData(comboid)
                    if (tID == self.edit_component["template"]):
                        self.comboComp.SetSelection(comboid)
                        break

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            wx.ID_ANY,
            "Plantilla por defecto",
            size=(400, 240),
            style=wx.DEFAULT_DIALOG_STYLE
        )

        self.log = parent.log

        # Add a panel so it looks the correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.parent = parent

        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.close_dialog)

        # Variables
        self.inputs = {}
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.AddSpacer(20)

        label = wx.StaticText(
            self.panel,
            id=wx.ID_ANY,
            label="Seleccione la plantilla por defecto para la categoría",
            style=0,
        )
        vsizer.Add(label, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vsizer.AddSpacer(10)
        self.comboCat = wx.ComboBox(
            self.panel,
            style=wx.CB_READONLY | wx.CB_SORT | wx.CB_DROPDOWN
        )
        self.comboCat.Bind(wx.EVT_COMBOBOX, self._onCategorySelection)
        cats = self.parent.database_temp.query(
            """
            SELECT
              [ID],
              [Name]
            FROM
              [Categories]
            WHERE
              [Parent] = -1
            AND
              [ID] <> -1;"""
        )
        for item in cats:
            self.comboCat.Append(item[1], item[0])
        vsizer.Add(self.comboCat, 0, wx.EXPAND)
        vsizer.AddSpacer(10)
        self.comboSubCat = wx.ComboBox(
            self.panel,
            style=wx.CB_READONLY | wx.CB_SORT | wx.CB_DROPDOWN
        )
        self.comboSubCat.Bind(wx.EVT_COMBOBOX, self._onCategorySelection)
        vsizer.Add(self.comboSubCat, 0, wx.EXPAND)
        vsizer.AddSpacer(10)
        self.comboComp = wx.ComboBox(
            self.panel,
            style=wx.CB_READONLY | wx.CB_SORT | wx.CB_DROPDOWN
        )
        vsizer.Add(self.comboComp, 0, wx.EXPAND)
        self.comboComp.Append("_Sin plantilla por defecto", None)
        vsizer.AddSpacer(20)

        # Buttons BoxSizer
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_add = wx.Button(self.panel, label="Guardar")
        btn_add.Bind(wx.EVT_BUTTON, self._save)
        btn_cancel = wx.Button(self.panel, label="Cancelar")
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
        self.edit_component = {}

        self.edit_component['template'] = self.parent.database_comp.query(
            """SELECT [Template] FROM [Categories] WHERE [ID] = ?;""",
            (
                itemData['id'],
            )
        )

        if (
            self.edit_component['template']
            and len(self.edit_component['template']) > 0
        ):
            self.edit_component['template'] = self.edit_component['template'][0][0]
        else:
            self.edit_component['template'] = None

        if self.edit_component['template']:
            category = self.parent.database_temp.query(
                """SELECT [Category] FROM [Templates] WHERE [ID] = ?;""",
                (
                    self.edit_component['template'],
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

            for comboid in range(0, self.comboCat.GetCount()):
                tID = self.comboCat.GetClientData(comboid)
                if (tID == self.edit_component["category"]):
                    self.comboCat.SetSelection(comboid)
                    break

            self._onCategorySelection(None)
        else:
            self.comboCat.SetSelection(0)
            self._onCategorySelection(None)
