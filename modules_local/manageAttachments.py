# -*- coding: utf-8 -*-

'''
18 Aug 2019
@autor: Daniel Carrasco
'''

import globals
from os import path, listdir, stat
from modules_local.startfile import open_file as startfile
import wx
import wx.lib.agw.ribbon as RB
from modules import getResourcePath

# Load main data
app = wx.App()
globals.init()

# ID de los botones
ID_FILE_ADD = wx.ID_HIGHEST + 1
ID_FILE_VIEW = ID_FILE_ADD + 1
ID_FILE_EXPORT = ID_FILE_VIEW + 1
ID_FILE_DEL = ID_FILE_EXPORT + 1
ID_FILE_SET_DS = ID_FILE_DEL + 1
ID_FILE_CLEAR_DS = ID_FILE_SET_DS + 1


class manageAttachments(wx.Dialog):
    # ##=== Exit Function ===## #
    def close_dialog(self, event):
        self.closed = True
        self.Destroy()

    def _itemListRefresh(self):
        self.log.info("Cleaning the list")
        self.itemList.DeleteAllItems()
        files = self._database._select(
            "Files",
            items=[
                "ID",
                "Filename",
                "Datasheet"
            ],
            where=[
                {'key': 'Component', 'value': self._component_id}
            ],
            order=[
                {'key': 'Filename'}
            ]
        )
        has_datasheet = False
        for item in files:
            filename, extension = path.splitext(item[1])
            extension = extension.lstrip(".")
            ext_id = 2
            for idx, ext in enumerate(self.il_ext):
                if extension == ext:
                    ext_id = idx
            index = self.itemList.InsertItem(920863821570964096, "")
            self.itemList.SetItemColumnImage(index, 1, ext_id)
            self.itemList.SetItem(index, 1, item[1])
            self.itemList.SetItemData(index, item[0])
            if item[2]:
                self.itemList.SetItemColumnImage(index, 0, 1)
                has_datasheet = True
            else:
                self.itemList.SetItemColumnImage(index, 0, 0)

        self.bbar_ds.EnableButton(ID_FILE_CLEAR_DS, has_datasheet)

    def _file_add(self, event):
        with wx.FileDialog(
            self,
            "Abrir fichero",
            wildcard=(
                "Ficheros reconocidos (*.jpg, *.jpeg, *.png, *.gif, *.bmp, "
                "*.pdf, *.doc, *.docx, *.xls, *.xlsx, *.odt, *.ods)|"
                "*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.pdf;*.doc;*.docx;*.xls;*.xlsx;*.odt;*.ods|"
                "Imágenes (*.jpg, *.jpeg, *.png, *.gif, *.bmp)|*.jpg;*.jpeg;*.png;*.gif;*.bmp|"
                "Documentos (*.pdf, *.doc, *.docx, *.xls, *.xlsx, *.odt, *.ods)|"
                "*.pdf;*.doc;*.docx;*.xls;*.xlsx;*.odt;*.ods|"
                "Todos los ficheros (*.*)|*.*"),
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            filename, extension = path.splitext(pathname)

            max_size = globals.config["attachments"]["max_size"] * 1024 * 1024
            if stat(pathname).st_size > max_size:
                error = wx.MessageDialog(
                    None,
                    "El fichero excede el tamaño máximo permitido: {}MB".format(
                        globals.config["attachments"]["max_size"]
                    ) +
                    "\n\nSi lo desea, puede cambiar el tamaño en las opciones.",
                    'Tamaño excedido',
                    wx.OK | wx.ICON_ERROR
                )
                error.ShowModal()
                error.Destroy()
                return False

            datasheet = False
            exists = self._database._select(
                "Files",
                items=["ID"],
                where=[
                    {'key': 'Component', 'value': self._component_id},
                    {'key': 'Datasheet', 'value': 1}
                ]
            )
            if len(exists) == 0 and extension.lower() == ".pdf":
                dlg = wx.MessageDialog(
                    None,
                    ("El componente no tiene Datasheet. \n"
                     "¿Desea marcar el PDF seleccionado como Datasheet?."),
                    'Marcar como Datasheet',
                    wx.YES_NO | wx.ICON_QUESTION
                )

                if dlg.ShowModal() == wx.ID_YES:
                    datasheet = True

                dlg.Destroy()

            savedFile = self._database.file_add(
                fileDialog.GetPath(),
                self._component_id,
                datasheet,
                globals.config["attachments"]["compression"]
            )
            if savedFile:
                self._itemListRefresh()
                ok = wx.MessageDialog(
                    None,
                    "Fichero añadido correctamente",
                    'Correcto',
                    wx.OK | wx.ICON_INFORMATION
                )
                ok.ShowModal()
                ok.Destroy()
        if event:
            event.Skip()

    def _file_delete(self, event):
        dlg = wx.MessageDialog(
            None,
            "¿Seguro que desea eliminar los ficheros seleccionados?.\n\n" +
            "AVISO: Dichos ficheros no se podrán recuperar.",
            'Eliminar',
            wx.YES_NO | wx.ICON_QUESTION
        )

        if dlg.ShowModal() == wx.ID_YES:
            selected = self.itemList.GetFirstSelected()

            while selected != -1:
                file_id = self.itemList.GetItemData(selected)
                self._database.file_del(file_id)
                selected = self.itemList.GetNextSelected(selected)

            self._itemListRefresh()

        dlg.Destroy()

    def _file_view(self, event):
        selected = self.itemList.GetFirstSelected()
        file_id = self.itemList.GetItemData(selected)
        tempFile = self._database.file_export(file_id)
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

    def _file_export(self, event):
        selected = self.itemList.GetFirstSelected()
        file_id = self.itemList.GetItemData(selected)
        exists = self._database._select(
            "Files",
            items=["Filename"],
            where=[
                {'key': "ID", 'value': file_id}
            ]
        )
        filename, extension = path.splitext(exists[0][0])
        extension = extension.lstrip(".")
        with wx.FileDialog(
            self,
            "Guardar fichero",
            defaultFile=exists[0][0],
            wildcard="Ficheros {0} (*.{0})|*.{0}".format(extension),
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        ) as fileDialog:
            if fileDialog.ShowModal() != wx.ID_CANCEL:
                if self._database.file_export(file_id, fileDialog.GetPath()):
                    dlg = wx.MessageDialog(
                        None,
                        "Fichero guardado correctamente.",
                        'Correcto',
                        wx.OK | wx.ICON_INFORMATION
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                else:
                    dlg = wx.MessageDialog(
                        None,
                        "Ocurrió un error al guardar el fichero",
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()

    def _datasheet_set(self, event):
        selected = self.itemList.GetFirstSelected()
        file_id = self.itemList.GetItemData(selected)
        self._database.datasheet_set(self._component_id, file_id)
        self._itemListRefresh()

    def _datasheet_clear(self, event):
        self._database.datasheet_clear(self._component_id)
        self._itemListRefresh()

    def _onResizeList(self, event):
        last_column_size = self.itemList.GetClientRect()[2]
        for column in range(0, self.itemList.GetColumnCount()-1):
            last_column_size -= self.itemList.GetColumnWidth(column)

        self.itemList.SetColumnWidth(1, last_column_size)
        if event:
            event.Skip()

    def _onChangeSelection(self, event):
        selected = self.itemList.GetFirstSelected()
        if selected == -1:
            self.bbar_adj.EnableButton(ID_FILE_VIEW, False)
            self.bbar_adj.EnableButton(ID_FILE_EXPORT, False)
            self.bbar_adj.EnableButton(ID_FILE_DEL, False)
            self.bbar_ds.EnableButton(ID_FILE_SET_DS, False)
        else:
            self.bbar_adj.EnableButton(ID_FILE_DEL, True)
            if self.itemList.GetNextSelected(selected) == -1:
                self.bbar_adj.EnableButton(ID_FILE_VIEW, True)
                self.bbar_adj.EnableButton(ID_FILE_EXPORT, True)

                file_id = self.itemList.GetItemData(selected)
                is_ds = self._database._select(
                    "Files",
                    items=["Datasheet"],
                    where=[
                        {'key': "ID", 'value': file_id}
                    ]
                )
                if not is_ds[0][0]:
                    self.bbar_ds.EnableButton(ID_FILE_SET_DS, True)
            else:
                self.bbar_adj.EnableButton(ID_FILE_VIEW, False)
                self.bbar_adj.EnableButton(ID_FILE_EXPORT, False)
                self.bbar_ds.EnableButton(ID_FILE_SET_DS, False)

    def __init__(self, database, parent=None, component_id=None):
        wx.Dialog.__init__(
            self,
            parent,
            wx.ID_ANY,
            "Gestionar Adjuntos",
            size=(500, 500),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )

        self._database = database
        self._component_id = component_id
        self._parent = parent
        self.log = parent.log

        # Add a panel so it looks the correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)

        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.close_dialog)

        # Variables
        self.parent = parent

        # iconList
        self.log.debug("Creating image list")
        self.il_ext = []
        self.il = wx.ImageList(48, 48, wx.IMAGE_LIST_SMALL)
        self.log.debug("Adding filetype icons")

        image = wx.Image(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                "empty.png"
            ),
            wx.BITMAP_TYPE_ANY
        )
        self.il.Add(image.ConvertToBitmap())
        self.il_ext.append("___")
        image = wx.Image(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                "tick.png"
            ),
            wx.BITMAP_TYPE_ANY
        )
        self.il.Add(image.ConvertToBitmap())
        self.il_ext.append("___")
        image = wx.Image(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                "file_unknown.png"
            ),
            wx.BITMAP_TYPE_ANY
        )
        self.il.Add(image.ConvertToBitmap())
        self.il_ext.append("unk")

        for file in listdir(
            getResourcePath.getResourcePath(
                globals.config["folders"]["images"],
                "filetypes"
            )
        ):
            if file.endswith(".png"):
                filename, extension = path.splitext(file)
                image = wx.Image(
                    getResourcePath.getResourcePath(
                        path.join(
                            globals.config["folders"]["images"],
                            "filetypes"
                        ),
                        file
                    ),
                    wx.BITMAP_TYPE_ANY
                )
                self.il.Add(image.ConvertToBitmap())
                self.il_ext.append(filename)

        # Ribbon Bar
        ribbon = RB.RibbonBar(self, -1)
        page = RB.RibbonPage(ribbon, wx.ID_ANY, "Page")

        # #--------------------# #
        # ## Panel Adjuntos ## #
        pAdj = RB.RibbonPanel(page, wx.ID_ANY, "Adjuntos")
        self.bbar_adj = RB.RibbonButtonBar(pAdj)
        # Add File
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'add_files.png'
            )
        )
        self.bbar_adj.AddSimpleButton(
            ID_FILE_ADD,
            "Añadir Adjunto",
            image,
            'Añade un adjunto nuevo'
        )

        # View File
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'view_files.png'
            )
        )
        self.bbar_adj.AddSimpleButton(
            ID_FILE_VIEW,
            "Ver Adjunto",
            image,
            'Visualiza el adjunto seleccionado'
        )

        # Export File
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'file_export.png'
            )
        )
        self.bbar_adj.AddSimpleButton(
            ID_FILE_EXPORT,
            "Exportar Adjunto",
            image,
            'Exporta el adjunto seleccionado'
        )

        # Del File
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'del_files.png'
            )
        )
        self.bbar_adj.AddSimpleButton(
            ID_FILE_DEL,
            "Eliminar Adjunto",
            image,
            'Elimina el adjunto seleccionado'
        )

        # #--------------------# #
        # ## Panel Datasheet ## #
        pDs = RB.RibbonPanel(page, wx.ID_ANY, "Datasheet")
        self.bbar_ds = RB.RibbonButtonBar(pDs)
        # Set as Datasheet
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'set_datasheet.png'
            )
        )
        self.bbar_ds.AddSimpleButton(
            ID_FILE_SET_DS,
            "Marcar como Datasheet",
            image,
            'Marca el fichero seleccionado como datasheet del componente'
        )

        # Clear Datasheet
        image = wx.Bitmap()
        image.LoadFile(
            getResourcePath.getResourcePath(
              globals.config["folders"]["images"],
              'clear_datasheet.png'
            )
        )
        self.bbar_ds.AddSimpleButton(
            ID_FILE_CLEAR_DS,
            "Limpiar Datasheet",
            image,
            'Elimina la marca de datasheet de cualquier fichero'
        )

        # Bind Buttons
        self.bbar_adj.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._file_add,
            id=ID_FILE_ADD
        )
        self.bbar_adj.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._file_view,
            id=ID_FILE_VIEW
        )
        self.bbar_adj.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._file_export,
            id=ID_FILE_EXPORT
        )
        self.bbar_adj.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._file_delete,
            id=ID_FILE_DEL
        )
        self.bbar_ds.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._datasheet_set,
            id=ID_FILE_SET_DS
        )
        self.bbar_ds.Bind(
            RB.EVT_RIBBONBUTTONBAR_CLICKED,
            self._datasheet_clear,
            id=ID_FILE_CLEAR_DS
        )

        # Default state
        self.bbar_adj.EnableButton(ID_FILE_VIEW, False)
        self.bbar_adj.EnableButton(ID_FILE_EXPORT, False)
        self.bbar_adj.EnableButton(ID_FILE_DEL, False)
        self.bbar_ds.EnableButton(ID_FILE_SET_DS, False)
        self.bbar_ds.EnableButton(ID_FILE_CLEAR_DS, False)

        # Widget items list
        self.log.debug("Creating item list")
        self.itemList = wx.ListCtrl(
            self,
            wx.ID_ANY,
            style=wx.LC_REPORT | wx.SUNKEN_BORDER,
        )
        self.itemList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
        self.itemList.Bind(
            wx.EVT_SIZE,
            self._onResizeList
        )
        self.itemList.Bind(
            wx.EVT_LIST_ITEM_SELECTED,
            self._onChangeSelection
        )
        self.itemList.Bind(
            wx.EVT_LIST_ITEM_DESELECTED,
            self._onChangeSelection
        )
        self.itemList.Bind(
            wx.EVT_LIST_ITEM_ACTIVATED,
            self._file_view
        )
        self.itemList.InsertColumn(0, 'DS', width=30)
        self.itemList.InsertColumn(1, 'Fichero', width=320)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(ribbon, 0, wx.EXPAND)
        vsizer.Add(self.itemList, 1, wx.EXPAND)
        self.SetSizer(vsizer)

        self.log.debug("Updating item list and painting Ribbon")
        # Actualizar CheckList
        self._itemListRefresh()
        # Pintar Ribbon
        ribbon.Realize()
