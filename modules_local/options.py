# -*- coding: utf-8 -*-

'''
22 Aug 2019
@autor: Daniel Carrasco
'''
import wx
import globals
from modules import iniReader
# import wx.lib.scrolledpanel as scrolled
from widgets import PlaceholderTextCtrl

# Load main data
app = wx.App()
globals.init()


class options(wx.Dialog):
    # ##=== Exit Function ===## #
    def close_dialog(self, event):
        self.closed = True
        self.Destroy()

    def _format_change(self, event):
        format = self.imgFMTCombo.GetSelection()

        if format == 0:
            self.labelQ.Enable()
            self.labelQ.SetLabel("Calidad:")
            self.imgSliderQ.Enable()
            self.sliderLabel.Enable()
            self.imgSliderQ.SetMin(1)
            self.imgSliderQ.SetMax(100)
            self.imgSliderQ.SetValue(
                globals.config["images"]["jpeg_quality"]
            )
            self._slider_change(None)
        elif format == 1:
            self.labelQ.Enable()
            self.labelQ.SetLabel("Compresión:")
            self.imgSliderQ.Enable()
            self.sliderLabel.Enable()
            self.imgSliderQ.SetMin(0)
            self.imgSliderQ.SetMax(9)
            self.imgSliderQ.SetValue(
                globals.config["images"]["png_compression"]
            )
            self._slider_change(None)
        else:
            self.labelQ.Disable()
            self.imgSliderQ.Disable()
            self.sliderLabel.Disable()

    def _slider_change(self, event):
        actual = self.imgSliderQ.GetValue()
        self.sliderLabel.SetLabel(str(actual))

    def _load_options(self):
        self.imgFMTCombo.SetSelection(
            globals.config["images"]["format"]
        )
        self.imgSizeCombo.SetSelection(
            globals.config["images"]["size"]
        )
        self.imgCOMPCombo.SetSelection(
            globals.config["images"]["compression"]
        )
        self.atmMaxSize.SetValue(
            str(globals.config["attachments"]["max_size"])
        )
        self.atmCOMPCombo.SetSelection(
            globals.config["attachments"]["compression"]
        )
        self._format_change(None)
        # Components DB
        self._dbPageComponents.SetSelection(
            globals.config["components_db"]["mode"]
        )
        self.comp_sqlite_file.SetValue(
            globals.config["components_db"]["sqlite_file"]
        )
        self.comp_mysql_host.SetValue(
            globals.config["components_db"]["mysql_host"]
        )
        self.comp_mysql_port.SetValue(
            str(globals.config["components_db"]["mysql_port"])
        )
        self.comp_mysql_user.SetValue(
            globals.config["components_db"]["mysql_user"]
        )
        self.comp_mysql_pass.SetValue(
            globals.config["components_db"]["mysql_pass"]
        )
        self.comp_mysql_dbase.SetValue(
            globals.config["components_db"]["mysql_dbase"]
        )
        # Templates DB
        self._dbPageTemplates.SetSelection(
            globals.config["templates_db"]["mode"]
        )
        self.temp_sqlite_file.SetValue(
            globals.config["templates_db"]["sqlite_file"]
        )
        self.temp_mysql_host.SetValue(
            globals.config["templates_db"]["mysql_host"]
        )
        self.temp_mysql_port.SetValue(
            str(globals.config["templates_db"]["mysql_port"])
        )
        self.temp_mysql_user.SetValue(
            globals.config["templates_db"]["mysql_user"]
        )
        self.temp_mysql_pass.SetValue(
            globals.config["templates_db"]["mysql_pass"]
        )
        self.temp_mysql_dbase.SetValue(
            globals.config["templates_db"]["mysql_dbase"]
        )

    def _save(self, file, data):
        return iniReader.SaveConfigFromDict(file, data)

    def _save_options(self, event):
        try:
            globals.config["attachments"]["max_size"] = int(self.atmMaxSize.GetRealValue())
        except Exception as e:
            dlg = wx.MessageDialog(
                None,
                "El tamaño indicado no es correcto: {}.".format(e),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Components database
        try:
            globals.config["components_db"]["mysql_port"] = (
                int(self.comp_mysql_port.GetRealValue())
            )
        except Exception as e:
            dlg = wx.MessageDialog(
                None,
                "El puerto de la BBDD de componentes no es correcto: {}.".format(e),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        globals.config["components_db"]["mode"] = self._dbPageComponents.GetSelection()
        globals.config["components_db"]["mysql_host"] = self.comp_mysql_host.GetRealValue()
        globals.config["components_db"]["mysql_user"] = self.comp_mysql_user.GetRealValue()
        globals.config["components_db"]["mysql_pass"] = self.comp_mysql_pass.GetRealValue()
        globals.config["components_db"]["mysql_dbase"] = self.comp_mysql_dbase.GetRealValue()

        # Templates database
        try:
            globals.config["templates_db"]["mysql_port"] = int(self.temp_mysql_port.GetRealValue())
        except Exception as e:
            dlg = wx.MessageDialog(
                None,
                "El puerto de la BBDD de componentes no es correcto: {}.".format(e),
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        globals.config["templates_db"]["mode"] = self._dbPageTemplates.GetSelection()
        globals.config["templates_db"]["mysql_host"] = self.temp_mysql_host.GetRealValue()
        globals.config["templates_db"]["mysql_user"] = self.temp_mysql_user.GetRealValue()
        globals.config["templates_db"]["mysql_pass"] = self.temp_mysql_pass.GetRealValue()
        globals.config["templates_db"]["mysql_dbase"] = self.temp_mysql_dbase.GetRealValue()

        globals.config["images"]["format"] = self.imgFMTCombo.GetSelection()
        globals.config["images"]["size"] = self.imgSizeCombo.GetSelection()
        globals.config["images"]["compression"] = self.imgCOMPCombo.GetSelection()
        globals.config["attachments"]["compression"] = self.atmCOMPCombo.GetSelection()
        if self.imgFMTCombo.GetSelection() == 0:
            globals.config["images"]["jpeg_quality"] = self.imgSliderQ.GetValue()
        elif self.imgFMTCombo.GetSelection() == 1:
            globals.config["images"]["png_compression"] = self.imgSliderQ.GetValue()

        try:
            if self._save('config.ini', globals.config):
                dlg = wx.MessageDialog(
                    None,
                    "Se ha guardado la configuración correctamente.\n\n" +
                    "NOTA: Deberá reiniciar el programa para hacer efectivos los " +
                    "cambios en las Bases de Dataos",
                    'Guardado',
                    wx.OK | wx.ICON_INFORMATION
                )
                dlg.ShowModal()
                dlg.Destroy()
            else:
                dlg = wx.MessageDialog(
                    None,
                    "Ocurrió un error al guardar la configuración.",
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()
        except Exception as e:
            self.log.error(
                "There was an error writing config.ini file: {}".format(e)
            )
            dlg = wx.MessageDialog(
                None,
                "Ocurrió un error al guardar el fichero de configuración.",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False

        self.close_dialog(None)

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        super(options, self).__init__(
            parent,
            wx.ID_ANY,
            "Plantilla por defecto",
            size=(500, 300),
            style=wx.DEFAULT_DIALOG_STYLE
        )

        self.log = parent.log

        self.default_label_w = 75
        self.default_selector_w = 140

        panel = wx.Panel(self)
        panelBox = wx.BoxSizer(wx.VERTICAL)

        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.close_dialog)

        # #--------------------------------------------------# #
        nb = wx.Notebook(panel)
        _imgPage = wx.Panel(nb)
        _imgPage.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)
        )
        nb.AddPage(_imgPage, "Imágenes")
        _atmPage = wx.Panel(nb)
        _atmPage.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)
        )
        nb.AddPage(_atmPage, "Adjuntos")
        self._dbPageComponents = wx.Choicebook(nb)
        self._dbPageComponents.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)
        )
        nb.AddPage(self._dbPageComponents, "BBDD Componentes")
        self._dbPageTemplates = wx.Choicebook(nb)
        self._dbPageTemplates.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)
        )
        nb.AddPage(self._dbPageTemplates, "BBDD Plantillas")

        # #--------------------------------------------------# #
        # Image Format Options
        _imgOPTSizer = wx.BoxSizer(wx.VERTICAL)
        _imgPage.SetSizer(_imgOPTSizer)
        _imgOPTSizer.AddSpacer(10)
        _imgOPT_FMTBox = wx.BoxSizer(wx.HORIZONTAL)
        labelFMT = wx.StaticText(
            _imgPage,
            id=wx.ID_ANY,
            label="Formato:",
            size=(self.default_label_w, 15),
            style=0,
        )
        self.imgFMTCombo = wx.ComboBox(
            _imgPage,
            choices=[
                "JPEG (Menor tamaño)",
                "PNG",
                "BMP",
                "TIFF (Mayor tamaño)"
            ],
            size=(self.default_selector_w, 15),
            style=wx.CB_READONLY | wx.CB_DROPDOWN
        )
        self.imgFMTCombo.Bind(wx.EVT_COMBOBOX, self._format_change)
        self.labelQ = wx.StaticText(
            _imgPage,
            id=wx.ID_ANY,
            label="Calidad:",
            size=(self.default_label_w, 15),
            style=0,
        )
        self.imgSliderQ = wx.Slider(
            _imgPage,
            wx.ID_ANY,
            0,
            0,
            100,
            size=(self.default_selector_w - 35, 23)
        )
        self.sliderLabel = wx.StaticText(
            _imgPage,
            id=wx.ID_ANY,
            label="100",
            size=(20, 15),
            style=0 | wx.RIGHT,
        )
        self.imgSliderQ.Bind(wx.EVT_SLIDER, self._slider_change)
        _imgOPT_FMTBox.Add(labelFMT, 0, wx.TOP, 4)
        _imgOPT_FMTBox.Add(self.imgFMTCombo, 0, wx.EXPAND)
        _imgOPT_FMTBox.AddSpacer(30)
        _imgOPT_FMTBox.Add(self.labelQ, 0, wx.TOP, 4)
        _imgOPT_FMTBox.Add(self.imgSliderQ, 0, wx.EXPAND)
        _imgOPT_FMTBox.Add(self.sliderLabel, 0, wx.TOP, 4)
        _imgOPTSizer.Add(
            _imgOPT_FMTBox,
            0,
            wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT,
            10
        )

        _imgOPT_CMPBox = wx.BoxSizer(wx.HORIZONTAL)
        labelSize = wx.StaticText(
            _imgPage,
            id=wx.ID_ANY,
            label="Tamaño:",
            size=(self.default_label_w, 15),
            style=0,
        )
        self.imgSizeCombo = wx.ComboBox(
            _imgPage,
            choices=[
                "100 x 100",
                "200 x 200",
                "300 x 300",
                "400 x 400",
                "500 x 500",
                "600 x 600",
                "700 x 700",
                "800 x 800",
                "900 x 900",
                "1000 x 1000",
            ],
            size=(self.default_selector_w, 25),
            style=wx.CB_READONLY | wx.CB_DROPDOWN
        )
        labelComp = wx.StaticText(
            _imgPage,
            id=wx.ID_ANY,
            label="Compresión:",
            size=(self.default_label_w, 15),
            style=0,
        )
        self.imgCOMPCombo = wx.ComboBox(
            _imgPage,
            choices=[
                "Ninguna",
                "LZ4",
                "GZIP",
                "BZIP",
                "LZMA"
            ],
            size=(self.default_selector_w, 25),
            style=wx.CB_READONLY | wx.CB_DROPDOWN
        )
        _imgOPT_CMPBox.Add(labelSize, 0, wx.TOP, 4)
        _imgOPT_CMPBox.Add(self.imgSizeCombo, 0, wx.EXPAND)
        _imgOPT_CMPBox.AddSpacer(30)
        _imgOPT_CMPBox.Add(labelComp, 0, wx.TOP, 4)
        _imgOPT_CMPBox.Add(self.imgCOMPCombo, 0, wx.EXPAND)
        _imgOPTSizer.Add(
            _imgOPT_CMPBox,
            0,
            wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT,
            10
        )
        # #--------------------------------------------------# #

        # #--------------------------------------------------# #
        # Atachment Options
        _atmOPTSizer = wx.BoxSizer(wx.VERTICAL)
        _atmPage.SetSizer(_atmOPTSizer)
        _atmOPT_FMTBox = wx.BoxSizer(wx.HORIZONTAL)
        _atmOPTSizer.AddSpacer(10)

        labelSize = wx.StaticText(
            _atmPage,
            id=wx.ID_ANY,
            label="Tam. Máx:",
            size=(self.default_label_w, 15),
            style=0,
        )
        self.atmMaxSize = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _atmPage,
            value="",
            placeholder="Tam. máx. adjuntos",
            size=(self.default_selector_w - 20, 23),
        )
        labelMB = wx.StaticText(
            _atmPage,
            id=wx.ID_ANY,
            label="MB",
            size=(20, 15),
            style=0 | wx.ALIGN_RIGHT,
        )
        labelComp = wx.StaticText(
            _atmPage,
            id=wx.ID_ANY,
            label="Compresión:",
            size=(self.default_label_w, 15),
            style=0,
        )
        self.atmCOMPCombo = wx.ComboBox(
            _atmPage,
            choices=[
                "Ninguna",
                "LZ4",
                "GZIP",
                "BZIP",
                "LZMA"
            ],
            size=(self.default_selector_w, 23),
            style=wx.CB_READONLY | wx.CB_DROPDOWN
        )
        _atmOPT_FMTBox.Add(labelSize, 0, wx.TOP, 4)
        _atmOPT_FMTBox.Add(self.atmMaxSize, 0, wx.EXPAND)
        _atmOPT_FMTBox.Add(labelMB, 0, wx.TOP, 3)
        _atmOPT_FMTBox.AddSpacer(30)
        _atmOPT_FMTBox.Add(labelComp, 0, wx.TOP, 4)
        _atmOPT_FMTBox.Add(self.atmCOMPCombo, 0, wx.EXPAND)
        _atmOPTSizer.Add(
            _atmOPT_FMTBox,
            0,
            wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT,
            10
        )
        # #--------------------------------------------------# #

        # #--------------------------------------------------# #
        # Components Database Options
        _db_sqlite_panel = wx.Panel(self._dbPageComponents)
        _db_sqlite_Sizer = wx.BoxSizer(wx.VERTICAL)
        _db_sqlite_panel.SetSizer(_db_sqlite_Sizer)
        _db_sqlite_Sizer.AddSpacer(5)
        self._dbPageComponents.AddPage(_db_sqlite_panel, "Opciones SQLite")
        _db_mysql_panel = wx.Panel(self._dbPageComponents)
        _db_mysql_Sizer = wx.BoxSizer(wx.VERTICAL)
        _db_mysql_panel.SetSizer(_db_mysql_Sizer)
        _db_mysql_Sizer.AddSpacer(5)
        self._dbPageComponents.AddPage(_db_mysql_panel, "Opciones MySQL")

        horSizer = wx.BoxSizer(wx.HORIZONTAL)
        horSizer.AddSpacer(10)
        label = wx.StaticText(
            _db_sqlite_panel,
            id=wx.ID_ANY,
            label="Fichero:",
            size=(self.default_label_w, 15),
            style=0 | wx.ALIGN_LEFT,
        )
        horSizer.Add(label, 0, wx.TOP, 4)
        horSizer.AddSpacer(5)
        self.comp_sqlite_file = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _db_sqlite_panel,
            value="",
            placeholder="Ruta de fichero sqlite",
            size=(self.default_selector_w - 20, 23),
        )
        horSizer.Add(self.comp_sqlite_file, 1, wx.EXPAND)
        horSizer.AddSpacer(5)
        btn_exp = wx.Button(_db_sqlite_panel, label="Examinar")
        btn_exp.Bind(wx.EVT_BUTTON, self._save_options)
        horSizer.Add(btn_exp, 0, wx.EXPAND)
        horSizer.AddSpacer(10)
        _db_sqlite_Sizer.Add(horSizer, 0, wx.EXPAND)
        _db_sqlite_Sizer.AddSpacer(10)

        horSizer = wx.BoxSizer(wx.HORIZONTAL)
        horSizer.AddSpacer(10)
        label = wx.StaticText(
            _db_mysql_panel,
            id=wx.ID_ANY,
            label="Host:",
            size=(self.default_label_w, 15),
            style=0 | wx.ALIGN_LEFT,
        )
        horSizer.Add(label, 0, wx.TOP, 4)
        horSizer.AddSpacer(5)
        self.comp_mysql_host = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _db_mysql_panel,
            value="",
            placeholder="127.0.0.1",
            size=(self.default_selector_w - 20, 23),
        )
        horSizer.Add(self.comp_mysql_host, 1, wx.EXPAND)
        horSizer.AddSpacer(30)
        label = wx.StaticText(
            _db_mysql_panel,
            id=wx.ID_ANY,
            label="Puerto:",
            size=(self.default_label_w, 15),
            style=0 | wx.ALIGN_LEFT,
        )
        horSizer.Add(label, 0, wx.TOP, 4)
        horSizer.AddSpacer(5)
        self.comp_mysql_port = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _db_mysql_panel,
            value="",
            placeholder="3306",
            size=(self.default_selector_w - 20, 23),
        )
        horSizer.Add(self.comp_mysql_port, 1, wx.EXPAND)
        horSizer.AddSpacer(10)
        _db_mysql_Sizer.Add(horSizer, 0, wx.EXPAND)
        _db_mysql_Sizer.AddSpacer(10)

        horSizer = wx.BoxSizer(wx.HORIZONTAL)
        horSizer.AddSpacer(10)
        label = wx.StaticText(
            _db_mysql_panel,
            id=wx.ID_ANY,
            label="User:",
            size=(self.default_label_w, 15),
            style=0 | wx.ALIGN_LEFT,
        )
        horSizer.Add(label, 0, wx.TOP, 4)
        horSizer.AddSpacer(5)
        self.comp_mysql_user = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _db_mysql_panel,
            value="",
            placeholder="root",
            size=(self.default_selector_w - 20, 23),
        )
        horSizer.Add(self.comp_mysql_user, 1, wx.EXPAND)
        horSizer.AddSpacer(30)
        label = wx.StaticText(
            _db_mysql_panel,
            id=wx.ID_ANY,
            label="Password:",
            size=(self.default_label_w, 15),
            style=0 | wx.ALIGN_LEFT,
        )
        horSizer.Add(label, 0, wx.TOP, 4)
        horSizer.AddSpacer(5)
        self.comp_mysql_pass = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _db_mysql_panel,
            value="",
            placeholder="",
            size=(self.default_selector_w - 20, 23),
        )
        horSizer.Add(self.comp_mysql_pass, 1, wx.EXPAND)
        horSizer.AddSpacer(10)
        _db_mysql_Sizer.Add(horSizer, 0, wx.EXPAND)
        _db_mysql_Sizer.AddSpacer(10)

        horSizer = wx.BoxSizer(wx.HORIZONTAL)
        horSizer.AddSpacer(10)
        label = wx.StaticText(
            _db_mysql_panel,
            id=wx.ID_ANY,
            label="Database:",
            size=(self.default_label_w, 15),
            style=0 | wx.ALIGN_LEFT,
        )
        horSizer.Add(label, 0, wx.TOP, 4)
        horSizer.AddSpacer(5)
        self.comp_mysql_dbase = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _db_mysql_panel,
            value="",
            placeholder="Components",
            size=(self.default_selector_w - 20, 23),
        )
        horSizer.Add(self.comp_mysql_dbase, 1, wx.EXPAND)
        horSizer.AddSpacer(10)
        _db_mysql_Sizer.Add(horSizer, 0, wx.EXPAND)
        _db_mysql_Sizer.AddSpacer(10)
        # #--------------------------------------------------# #

        # #--------------------------------------------------# #
        # Components Database Templates
        _db_sqlite_panel = wx.Panel(self._dbPageTemplates)
        _db_sqlite_Sizer = wx.BoxSizer(wx.VERTICAL)
        _db_sqlite_panel.SetSizer(_db_sqlite_Sizer)
        _db_sqlite_Sizer.AddSpacer(5)
        self._dbPageTemplates.AddPage(_db_sqlite_panel, "Opciones SQLite")
        _db_mysql_panel = wx.Panel(self._dbPageTemplates)
        _db_mysql_Sizer = wx.BoxSizer(wx.VERTICAL)
        _db_mysql_panel.SetSizer(_db_mysql_Sizer)
        _db_mysql_Sizer.AddSpacer(5)
        self._dbPageTemplates.AddPage(_db_mysql_panel, "Opciones MySQL")

        horSizer = wx.BoxSizer(wx.HORIZONTAL)
        horSizer.AddSpacer(10)
        label = wx.StaticText(
            _db_sqlite_panel,
            id=wx.ID_ANY,
            label="Fichero:",
            size=(self.default_label_w, 15),
            style=0 | wx.ALIGN_LEFT,
        )
        horSizer.Add(label, 0, wx.TOP, 4)
        horSizer.AddSpacer(5)
        self.temp_sqlite_file = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _db_sqlite_panel,
            value="",
            placeholder="Ruta de fichero sqlite",
            size=(self.default_selector_w - 20, 23),
        )
        horSizer.Add(self.temp_sqlite_file, 1, wx.EXPAND)
        horSizer.AddSpacer(5)
        btn_exp = wx.Button(_db_sqlite_panel, label="Examinar")
        btn_exp.Bind(wx.EVT_BUTTON, self._save_options)
        horSizer.Add(btn_exp, 0, wx.EXPAND)
        horSizer.AddSpacer(10)
        _db_sqlite_Sizer.Add(horSizer, 0, wx.EXPAND)
        _db_sqlite_Sizer.AddSpacer(10)

        horSizer = wx.BoxSizer(wx.HORIZONTAL)
        horSizer.AddSpacer(10)
        label = wx.StaticText(
            _db_mysql_panel,
            id=wx.ID_ANY,
            label="Host:",
            size=(self.default_label_w, 15),
            style=0 | wx.ALIGN_LEFT,
        )
        horSizer.Add(label, 0, wx.TOP, 4)
        horSizer.AddSpacer(5)
        self.temp_mysql_host = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _db_mysql_panel,
            value="",
            placeholder="127.0.0.1",
            size=(self.default_selector_w - 20, 23),
        )
        horSizer.Add(self.temp_mysql_host, 1, wx.EXPAND)
        horSizer.AddSpacer(30)
        label = wx.StaticText(
            _db_mysql_panel,
            id=wx.ID_ANY,
            label="Puerto:",
            size=(self.default_label_w, 15),
            style=0 | wx.ALIGN_LEFT,
        )
        horSizer.Add(label, 0, wx.TOP, 4)
        horSizer.AddSpacer(5)
        self.temp_mysql_port = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _db_mysql_panel,
            value="",
            placeholder="3306",
            size=(self.default_selector_w - 20, 23),
        )
        horSizer.Add(self.temp_mysql_port, 1, wx.EXPAND)
        horSizer.AddSpacer(10)
        _db_mysql_Sizer.Add(horSizer, 0, wx.EXPAND)
        _db_mysql_Sizer.AddSpacer(10)

        horSizer = wx.BoxSizer(wx.HORIZONTAL)
        horSizer.AddSpacer(10)
        label = wx.StaticText(
            _db_mysql_panel,
            id=wx.ID_ANY,
            label="User:",
            size=(self.default_label_w, 15),
            style=0 | wx.ALIGN_LEFT,
        )
        horSizer.Add(label, 0, wx.TOP, 4)
        horSizer.AddSpacer(5)
        self.temp_mysql_user = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _db_mysql_panel,
            value="",
            placeholder="root",
            size=(self.default_selector_w - 20, 23),
        )
        horSizer.Add(self.temp_mysql_user, 1, wx.EXPAND)
        horSizer.AddSpacer(30)
        label = wx.StaticText(
            _db_mysql_panel,
            id=wx.ID_ANY,
            label="Password:",
            size=(self.default_label_w, 15),
            style=0 | wx.ALIGN_LEFT,
        )
        horSizer.Add(label, 0, wx.TOP, 4)
        horSizer.AddSpacer(5)
        self.temp_mysql_pass = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _db_mysql_panel,
            value="",
            placeholder="",
            size=(self.default_selector_w - 20, 23),
        )
        horSizer.Add(self.temp_mysql_pass, 1, wx.EXPAND)
        horSizer.AddSpacer(10)
        _db_mysql_Sizer.Add(horSizer, 0, wx.EXPAND)
        _db_mysql_Sizer.AddSpacer(10)

        horSizer = wx.BoxSizer(wx.HORIZONTAL)
        horSizer.AddSpacer(10)
        label = wx.StaticText(
            _db_mysql_panel,
            id=wx.ID_ANY,
            label="Database:",
            size=(self.default_label_w, 15),
            style=0 | wx.ALIGN_LEFT,
        )
        horSizer.Add(label, 0, wx.TOP, 4)
        horSizer.AddSpacer(5)
        self.temp_mysql_dbase = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _db_mysql_panel,
            value="",
            placeholder="Templates",
            size=(self.default_selector_w - 20, 23),
        )
        horSizer.Add(self.temp_mysql_dbase, 1, wx.EXPAND)
        horSizer.AddSpacer(10)
        _db_mysql_Sizer.Add(horSizer, 0, wx.EXPAND)
        _db_mysql_Sizer.AddSpacer(10)

        # #--------------------------------------------------# #
        panelBox.Add(nb, 1, wx.EXPAND)

        # #--------------------------------------------------# #
        # Buttons BoxSizer
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_add = wx.Button(panel, label="Aceptar")
        btn_add.Bind(wx.EVT_BUTTON, self._save_options)
        btn_cancel = wx.Button(panel, label="Cancelar")
        btn_cancel.Bind(wx.EVT_BUTTON, self.close_dialog)
        btn_sizer.AddSpacer(10)
        btn_sizer.Add(btn_add)
        btn_sizer.AddSpacer(40)
        btn_sizer.Add(btn_cancel)
        btn_sizer.AddSpacer(10)

        panelBox.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        # #--------------------------------------------------# #

        panel.SetSizer(panelBox)
        self._load_options()
        _imgPage.Layout()


# options(None).Show()
# app.MainLoop()
