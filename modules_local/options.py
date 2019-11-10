# -*- coding: utf-8 -*-

'''
22 Aug 2019
@autor: Daniel Carrasco
'''
import base64
import copy
import wx
import globals
from os import urandom, path
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from hashlib import sha256

from modules import iniReader, strToValue
# import wx.lib.scrolledpanel as scrolled
from widgets import PlaceholderTextCtrl
from plugins.database.sqlite import dbase
from plugins.database.mysql import dbase as MySQL

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

    def _get_relative_path(self, filename):
        filename = filename.replace(globals.rootPath, "")
        filename = filename.lstrip('/')
        filename = filename.lstrip('\\')
        return filename

    def _get_full_path(self, filename):
        if not filename[1] == '/' and not filename[1] == '\\' and ":" not in filename:
            filename = path.join(
                globals.rootPath,
                filename
            )
        return filename

    def _db_file_select_comp(self, event):
        filename = self._get_full_path(self.comp_sqlite_file.GetRealValue())
        with wx.FileDialog(
            self,
            "Abrir fichero de imagen",
            wildcard="Base de datos (*.sqlite3)|*.sqlite3",
            defaultDir=path.dirname(filename),
            defaultFile=path.basename(filename),
            style=wx.FD_OPEN
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.comp_sqlite_file.SetValue(self._get_relative_path(fileDialog.GetPath()))

    def _db_file_select_temp(self, event):
        filename = self._get_full_path(self.temp_sqlite_file.GetRealValue())
        with wx.FileDialog(
            self,
            "Abrir fichero de imagen",
            wildcard="Base de datos (*.sqlite3)|*.sqlite3",
            defaultDir=path.dirname(filename),
            defaultFile=path.basename(filename),
            style=wx.FD_OPEN
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.temp_sqlite_file.SetValue(self._get_relative_path(fileDialog.GetPath()))

    def _db_file_select_log(self, event):
        filename = self._get_full_path(self.log_file.GetRealValue())
        with wx.FileDialog(
            self,
            "Seleccione fichero de log",
            wildcard="Fichero de Log (*.log)|*.log",
            defaultDir=path.dirname(filename),
            defaultFile=path.basename(filename),
            style=wx.FD_OPEN
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.log_file.SetValue(self._get_relative_path(fileDialog.GetPath()))

    def _load_options(self):
        self.log_file.SetValue(
            str(globals.config["general"]["log_file"])
        )
        self.generalLogLevel.SetSelection(
            5 - (globals.config["general"]["log_level"] / 10)
        )
        self.automaticSearch.SetValue(
            strToValue.strToValue(globals.config["general"]["automatic_search"], 'bool')
        )
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
            self.parent.dbase_config["components_db"]["mysql_host"]
        )
        self.comp_mysql_port.SetValue(
            str(self.parent.dbase_config["components_db"]["mysql_port"])
        )
        self.comp_mysql_user.SetValue(
            self.parent.dbase_config["components_db"]["mysql_user"]
        )
        self.comp_mysql_pass.SetValue(
            self.parent.dbase_config["components_db"]["mysql_pass"]
        )
        self.comp_mysql_dbase.SetValue(
            self.parent.dbase_config["components_db"]["mysql_dbase"]
        )
        # Templates DB
        self._dbPageTemplates.SetSelection(
            globals.config["templates_db"]["mode"]
        )
        self.temp_sqlite_file.SetValue(
            globals.config["templates_db"]["sqlite_file"]
        )
        self.temp_mysql_host.SetValue(
            self.parent.dbase_config["templates_db"]["mysql_host"]
        )
        self.temp_mysql_port.SetValue(
            str(self.parent.dbase_config["templates_db"]["mysql_port"])
        )
        self.temp_mysql_user.SetValue(
            self.parent.dbase_config["templates_db"]["mysql_user"]
        )
        self.temp_mysql_pass.SetValue(
            self.parent.dbase_config["templates_db"]["mysql_pass"]
        )
        self.temp_mysql_dbase.SetValue(
            self.parent.dbase_config["templates_db"]["mysql_dbase"]
        )

    def _save(self, file, data):
        return iniReader.SaveConfigFromDict(file, data)

    def _save_options(self, event):
        # We copy the options to new dict to only update if there's no errors
        new_config = copy.deepcopy(globals.config)
        new_dbase_config = copy.deepcopy(self.parent.dbase_config)
        try:
            new_config["attachments"]["max_size"] = int(self.atmMaxSize.GetRealValue())
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

        if (new_dbase_config['pass'] is None
                and (self._dbPageComponents.GetSelection() == 1
                     or self._dbPageTemplates.GetSelection() == 1)):
            dlg = wx.MessageDialog(
                None,
                "¿Desea encriptar los datos de conexión a la Base de Datos?",
                'Encriptar',
                wx.YES_NO | wx.ICON_QUESTION
            )
            ret = dlg.ShowModal()
            dlg.Destroy()
            if ret == wx.ID_NO:
                new_config["general"]['enc_key'] = 'False'
            else:
                while True:
                    pass1 = None
                    pass2 = None
                    dlg = wx.PasswordEntryDialog(
                        self,
                        'Introduzca la contraseña para proteger los datos de conexión',
                        'Encriptar datos'
                    )
                    dlg.SetValue("")
                    if dlg.ShowModal() == wx.ID_OK:
                        pass1 = dlg.GetValue()
                        dlg.Destroy()
                    else:
                        dlg.Destroy()
                        return False

                    dlg = wx.PasswordEntryDialog(
                        self,
                        'Introduzca la contraseña de nuevo para confirmar',
                        'Encriptar datos'
                    )
                    dlg.SetValue("")
                    if dlg.ShowModal() == wx.ID_OK:
                        pass2 = dlg.GetValue()
                        dlg.Destroy()
                    else:
                        dlg.Destroy()
                        return False

                    if pass1 == pass2:
                        new_dbase_config['pass'] = pass1.encode()
                        break
                    else:
                        dlg = wx.MessageDialog(
                            None,
                            "Las contraseñas no coinciden. Inténtelo de nuevo.",
                            'Error',
                            wx.OK | wx.ICON_ERROR
                        )
                        dlg.ShowModal()
                        dlg.Destroy()

        if not new_dbase_config['pass']:
            # Don't encrypt config data
            # Components database
            try:
                new_config["components_db"]["mysql_port"] = (
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

            new_config["components_db"]["mode"] = self._dbPageComponents.GetSelection()
            new_config["components_db"]["mysql_host"] = self.comp_mysql_host.GetRealValue()
            new_config["components_db"]["mysql_user"] = self.comp_mysql_user.GetRealValue()
            new_config["components_db"]["mysql_pass"] = self.comp_mysql_pass.GetRealValue()
            new_config["components_db"]["mysql_dbase"] = self.comp_mysql_dbase.GetRealValue()

            # Templates database
            try:
                new_config["templates_db"]["mysql_port"] = int(
                    self.temp_mysql_port.GetRealValue()
                )
            except Exception as e:
                dlg = wx.MessageDialog(
                    None,
                    "El puerto de la BBDD de templates no es correcto: {}.".format(e),
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()
                return False

            new_config["templates_db"]["mode"] = self._dbPageTemplates.GetSelection()
            new_config["templates_db"]["mysql_host"] = self.temp_mysql_host.GetRealValue()
            new_config["templates_db"]["mysql_user"] = self.temp_mysql_user.GetRealValue()
            new_config["templates_db"]["mysql_pass"] = self.temp_mysql_pass.GetRealValue()
            new_config["templates_db"]["mysql_dbase"] = self.temp_mysql_dbase.GetRealValue()

        else:
            # Encrypt config data
            if not new_dbase_config['salt']:
                new_dbase_config['salt'] = urandom(16)

            # Generating enc_key
            if not new_config.get("general", False):
                new_config["general"] = {}
            new_config["general"]['enc_key'] = "${}${}".format(
                base64.b64encode(new_dbase_config['salt']).decode(),
                sha256(new_dbase_config['pass']).hexdigest()
            )

            # Generating encrypt function
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=new_dbase_config['salt'],
                iterations=100000,
                backend=default_backend()
            )
            encryption_key = base64.urlsafe_b64encode(
                kdf.derive(new_dbase_config['pass'])
            )

            # Encrypting data
            enc = Fernet(encryption_key)

            # Components database
            try:
                new_config["components_db"]["mysql_port"] = enc.encrypt(
                    self.comp_mysql_port.GetRealValue().encode()
                ).decode()
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

            new_config["components_db"]["mode"] = self._dbPageComponents.GetSelection()
            new_config["components_db"]["mysql_host"] = enc.encrypt(
                self.comp_mysql_host.GetRealValue().encode()
            ).decode()
            new_config["components_db"]["mysql_user"] = enc.encrypt(
                self.comp_mysql_user.GetRealValue().encode()
            ).decode()
            new_config["components_db"]["mysql_pass"] = enc.encrypt(
                self.comp_mysql_pass.GetRealValue().encode()
            ).decode()
            new_config["components_db"]["mysql_dbase"] = enc.encrypt(
                self.comp_mysql_dbase.GetRealValue().encode()
            ).decode()

            # Templates database
            try:
                new_config["templates_db"]["mysql_port"] = enc.encrypt(
                    self.temp_mysql_port.GetRealValue().encode()
                ).decode()
            except Exception as e:
                dlg = wx.MessageDialog(
                    None,
                    "El puerto de la BBDD de templates no es correcto: {}.".format(e),
                    'Error',
                    wx.OK | wx.ICON_ERROR
                )
                dlg.ShowModal()
                dlg.Destroy()
                return False

            new_config["templates_db"]["mode"] = self._dbPageTemplates.GetSelection()
            new_config["templates_db"]["mysql_host"] = enc.encrypt(
                self.temp_mysql_host.GetRealValue().encode()
            ).decode()
            new_config["templates_db"]["mysql_user"] = enc.encrypt(
                self.temp_mysql_user.GetRealValue().encode()
            ).decode()
            new_config["templates_db"]["mysql_pass"] = enc.encrypt(
                self.temp_mysql_pass.GetRealValue().encode()
            ).decode()
            new_config["templates_db"]["mysql_dbase"] = enc.encrypt(
                self.temp_mysql_dbase.GetRealValue().encode()
            ).decode()

        # SQLite configuration
        new_config["components_db"]["sqlite_file"] = (
            self.comp_sqlite_file.GetRealValue()
        )
        new_config["templates_db"]["sqlite_file"] = (
            self.temp_sqlite_file.GetRealValue()
        )

        # Running config
        new_dbase_config["components_db"]["sqlite_file"] = (
            self.comp_sqlite_file.GetRealValue()
        )
        new_dbase_config["components_db"]["mysql_host"] = (
            self.comp_mysql_host.GetRealValue()
        )
        new_dbase_config["components_db"]["mysql_port"] = int(
            self.comp_mysql_port.GetRealValue()
        )
        new_dbase_config["components_db"]["mysql_user"] = (
            self.comp_mysql_user.GetRealValue()
        )
        new_dbase_config["components_db"]["mysql_pass"] = (
            self.comp_mysql_pass.GetRealValue()
        )
        new_dbase_config["components_db"]["mysql_dbase"] = (
            self.comp_mysql_dbase.GetRealValue()
        )
        new_dbase_config["templates_db"]["sqlite_file"] = (
            self.temp_sqlite_file.GetRealValue()
        )
        new_dbase_config["templates_db"]["mysql_host"] = (
            self.temp_mysql_host.GetRealValue()
        )
        new_dbase_config["templates_db"]["mysql_port"] = int(
            self.temp_mysql_port.GetRealValue()
        )
        new_dbase_config["templates_db"]["mysql_user"] = (
            self.temp_mysql_user.GetRealValue()
        )
        new_dbase_config["templates_db"]["mysql_pass"] = (
            self.temp_mysql_pass.GetRealValue()
        )
        new_dbase_config["templates_db"]["mysql_dbase"] = (
            self.temp_mysql_dbase.GetRealValue()
        )

        # We try to open/connect to new databases
        new_comp_dbase = None
        new_temp_dbase = None
        print(globals.config["components_db"]["mode"])
        if self._dbPageComponents.GetSelection() == 1:
            if (
                globals.config["components_db"]["mode"] != 1
                or self.comp_mysql_host.IsModified()
                or self.comp_mysql_port.IsModified()
                or self.comp_mysql_user.IsModified()
                or self.comp_mysql_pass.IsModified()
                or self.comp_mysql_dbase.IsModified()
            ):
                try:
                    new_comp_dbase = MySQL(
                        new_dbase_config['components_db']['mysql_host'],
                        new_dbase_config['components_db']['mysql_user'],
                        new_dbase_config['components_db']['mysql_pass'],
                        new_dbase_config['components_db']['mysql_dbase'],
                        auto_commit=False,
                        parent=self.parent
                    )
                    self.changed_components_db = True

                except Exception as e:
                    self.log.error("There was an error connecting to components DB: {}".format(e))
                    dlg = wx.MessageDialog(
                        None,
                        "Ocurrió un error al conectar a la BBDD de componentes: {}.".format(e),
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
        else:
            if self.comp_sqlite_file.IsModified():
                try:
                    new_dbase_config['components_db']['sqlite_file_real'] = path.join(
                        globals.rootPath,
                        new_dbase_config["components_db"]["sqlite_file"]
                    )
                    new_comp_dbase = dbase(
                        new_dbase_config["components_db"]["sqlite_file_real"],
                        auto_commit=False,
                        parent=self.parent
                    )
                except Exception as e:
                    self.log.error("There was an error opening components DB: {}".format(e))
                    dlg = wx.MessageDialog(
                        None,
                        "Ocurrió un error al abrir la BBDD de components: {}.".format(e),
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        if self._dbPageTemplates.GetSelection() == 1:
            if (
                globals.config["templates_db"]["mode"] != 1
                or self.temp_mysql_host.IsModified()
                or self.temp_mysql_port.IsModified()
                or self.temp_mysql_user.IsModified()
                or self.temp_mysql_pass.IsModified()
                or self.temp_mysql_dbase.IsModified()
            ):
                try:
                    new_temp_dbase = MySQL(
                        new_dbase_config['templates_db']['mysql_host'],
                        new_dbase_config['templates_db']['mysql_user'],
                        new_dbase_config['templates_db']['mysql_pass'],
                        new_dbase_config['templates_db']['mysql_dbase'],
                        auto_commit=False,
                        templates=True,
                        parent=self.parent
                    )

                except Exception as e:
                    self.log.error("There was an error connecting to templates DB: {}".format(e))
                    dlg = wx.MessageDialog(
                        None,
                        "Ocurrió un error al conectar a la BBDD de plantillas: {}.".format(e),
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
        else:
            if self.temp_sqlite_file.IsModified():
                try:
                    new_dbase_config['templates_db']['sqlite_file_real'] = path.join(
                        globals.rootPath,
                        new_dbase_config["templates_db"]["sqlite_file"]
                    )
                    new_temp_dbase = dbase(
                        new_dbase_config["templates_db"]["sqlite_file_real"],
                        auto_commit=False,
                        templates=True,
                        parent=self.parent
                    )

                except Exception as e:
                    self.log.error("There was an error opening templates DB: {}".format(e))
                    dlg = wx.MessageDialog(
                        None,
                        "Ocurrió un error al abrir la BBDD de plantillas: {}.".format(e),
                        'Error',
                        wx.OK | wx.ICON_ERROR
                    )
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        new_config["general"]["log_file"] = self.log_file.GetRealValue()
        new_config["general"]["log_level"] = 50 - (self.generalLogLevel.GetSelection() * 10)
        new_config["general"]["automatic_search"] = (
            str(self.automaticSearch.GetValue())
        )
        new_config["images"]["format"] = self.imgFMTCombo.GetSelection()
        new_config["images"]["size"] = self.imgSizeCombo.GetSelection()
        new_config["images"]["compression"] = self.imgCOMPCombo.GetSelection()
        new_config["attachments"]["compression"] = self.atmCOMPCombo.GetSelection()
        if self.imgFMTCombo.GetSelection() == 0:
            new_config["images"]["jpeg_quality"] = self.imgSliderQ.GetValue()
        elif self.imgFMTCombo.GetSelection() == 1:
            new_config["images"]["png_compression"] = self.imgSliderQ.GetValue()

        try:
            if self._save('config.ini', new_config):
                globals.config = new_config
                self.parent.dbase_config = new_dbase_config
                if new_comp_dbase:
                    try:
                        self.parent.database_comp.close()

                    except Exception as e:
                        self.log.warning(
                            "There was an error closing old components database: {}".format(e)
                        )

                    self.parent.database_comp = new_comp_dbase
                    self.changed_components_db = True

                if new_temp_dbase:
                    try:
                        self.parent.database_temp.close()

                    except Exception as e:
                        self.log.warning(
                            "There was an error closing old templates database: {}".format(e)
                        )

                    self.parent.database_temp = new_temp_dbase

                dlg = wx.MessageDialog(
                    None,
                    "Se ha guardado la configuración correctamente.",
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
        self.parent = parent
        self.changed_components_db = False

        self.default_label_w = 75
        self.default_selector_w = 140

        panel = wx.Panel(self)
        panelBox = wx.BoxSizer(wx.VERTICAL)

        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.close_dialog)

        # #--------------------------------------------------# #
        nb = wx.Notebook(panel)
        _generalPage = wx.Panel(nb)
        _generalPage.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)
        )
        nb.AddPage(_generalPage, "Generales")
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
        # Program general options
        _generalOPTSizer = wx.BoxSizer(wx.VERTICAL)
        _generalPage.SetSizer(_generalOPTSizer)
        _generalOPTSizer.AddSpacer(10)

        horSizer = wx.BoxSizer(wx.HORIZONTAL)
        labelFMT = wx.StaticText(
            _generalPage,
            id=wx.ID_ANY,
            label="Fichero log:",
            size=(self.default_label_w, 15),
            style=0,
        )
        horSizer.Add(labelFMT, 0, wx.TOP, 4)
        horSizer.AddSpacer(5)
        self.log_file = PlaceholderTextCtrl.PlaceholderTextCtrl(
            _generalPage,
            value="",
            placeholder="Ruta de fichero de log",
            size=(-1, 23),
        )
        horSizer.Add(self.log_file, 1, wx.EXPAND)
        horSizer.AddSpacer(5)
        btn_exp = wx.Button(_generalPage, label="Examinar")
        btn_exp.Bind(wx.EVT_BUTTON, self._db_file_select_log)
        horSizer.Add(btn_exp, 0, wx.EXPAND)
        _generalOPTSizer.Add(
            horSizer,
            0,
            wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT,
            10
        )
        _generalOPT_LLBox = wx.BoxSizer(wx.HORIZONTAL)
        labelFMT = wx.StaticText(
            _generalPage,
            id=wx.ID_ANY,
            label="Nivel de Log:",
            size=(self.default_label_w, 15),
            style=0,
        )
        _generalOPT_LLBox.Add(labelFMT, 0, wx.TOP, 4)
        _generalOPT_LLBox.AddSpacer(5)
        self.generalLogLevel = wx.ComboBox(
            _generalPage,
            choices=[
                "Critical",
                "Error",
                "Warning",
                "Information",
                "Debug"
            ],
            size=(self.default_selector_w, 25),
            style=wx.CB_READONLY | wx.CB_DROPDOWN
        )
        _generalOPT_LLBox.Add(self.generalLogLevel, 1, wx.EXPAND)
        _generalOPTSizer.Add(
            _generalOPT_LLBox,
            0,
            wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT,
            10
        )
        horBox = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(
            _generalPage,
            id=wx.ID_ANY,
            label="",
            size=(self.default_label_w, 15),
            style=0,
        )
        horBox.Add(label, 0, wx.TOP, 4)
        horBox.AddSpacer(5)
        self.automaticSearch = wx.CheckBox(
            _generalPage,
            id=wx.ID_ANY,
            label="Búsqueda automática de componentes",
            style=0
        )
        self.automaticSearch.SetToolTip(
            wx.ToolTip(
                "Filtra automáticamente los componentes al terminar de escribir"
            )
        )
        horBox.Add(self.automaticSearch, 0, wx.TOP, 4)
        _generalOPTSizer.Add(
            horBox,
            0,
            wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT,
            10
        )
        _generalOPTSizer.AddSpacer(10)

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
        btn_exp.Bind(wx.EVT_BUTTON, self._db_file_select_comp)
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
        btn_exp.Bind(wx.EVT_BUTTON, self._db_file_select_temp)
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
