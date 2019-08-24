# -*- coding: utf-8 -*-

'''
22 Aug 2019
@autor: Daniel Carrasco
'''

import logging
import wx
import globals
from modules import iniReader
from widgets import PlaceholderTextCtrl
import configparser


# Load main data
app = wx.App()
globals.init()

### Log Configuration ###
log = logging.getLogger("MainWindow")


class options(wx.Dialog):
###=== Exit Function ===###
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
            self.imgSliderQ.SetValue(globals.config["images"]["jpeg_quality"])
            self._slider_change(None)
        elif format == 1:
            self.labelQ.Enable()
            self.labelQ.SetLabel("Compresión:")
            self.imgSliderQ.Enable()
            self.sliderLabel.Enable()
            self.imgSliderQ.SetMin(0)
            self.imgSliderQ.SetMax(9)
            self.imgSliderQ.SetValue(globals.config["images"]["png_compression"])
            self._slider_change(None)
        else:
            self.labelQ.Disable()
            self.imgSliderQ.Disable()
            self.sliderLabel.Disable()


    def _slider_change(self, event):
        actual = self.imgSliderQ.GetValue()
        self.sliderLabel.SetLabel(str(actual))
        
    
    def _load_options(self):
        self.imgFMTCombo.SetSelection(globals.config["images"]["format"])
        self.imgSizeCombo.SetSelection(globals.config["images"]["size"])
        self.imgCOMPCombo.SetSelection(globals.config["images"]["compression"])
        self.atmMaxSize.SetValue(str(globals.config["attachments"]["max_size"]))
        self.atmCOMPCombo.SetSelection(globals.config["attachments"]["compression"])
        self._format_change(None)
        
    def _save(self, file, data):
        return iniReader.SaveConfigFromDict(file, data)
        
        
    def _save_options(self, event):
        try:
            globals.config["attachments"]["max_size"] = int(self.atmMaxSize.GetValue())
            
        except:
            dlg = wx.MessageDialog(
                None, 
                "El tamaño indicado no es correcto.",
                'Error',
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
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
            log.error("There was an error writing config.ini file: {}".format(e))
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
        
        
    
    #----------------------------------------------------------------------
    def __init__(self, parent):
        wx.Dialog.__init__(
            self, 
            parent, 
            wx.ID_ANY, 
            "Plantilla por defecto", 
            size=(500, 300),
            style=wx.DEFAULT_DIALOG_STYLE
        )
        
        self.default_label_w = 75
        self.default_selector_w = 140
        
        panel = wx.Panel(self)
        panelBox = wx.BoxSizer(wx.VERTICAL)
        
        ##--------------------------------------------------##
        # Image Format Options        
        _imgOPTSizerBox = wx.StaticBox(panel, -1, 'Opciones de Imágenes:')
        _imgOPTSizer = wx.StaticBoxSizer(_imgOPTSizerBox, wx.VERTICAL)
        _imgOPT_FMTBox = wx.BoxSizer(wx.HORIZONTAL)
        _imgOPT_CMPBox = wx.BoxSizer(wx.HORIZONTAL)
        _imgOPTSizer.Add(_imgOPT_FMTBox, 0, wx.ALL|wx.EXPAND, 5)
        _imgOPTSizer.Add(_imgOPT_CMPBox, 0, wx.ALL|wx.EXPAND, 5)
        _imgOPTSizer.AddSpacer(10)
        
        labelFMT = wx.StaticText(
            panel,
            id=wx.ID_ANY,
            label="Formato:",
            size=(self.default_label_w, 15),
            style=0,
        )
        self.imgFMTCombo = wx.ComboBox(
            panel, 
            choices = [
                "JPEG (Menor tamaño)",
                "PNG",
                "BMP",
                "TIFF (Mayor tamaño)"            
            ],
            size=(self.default_selector_w, 15),
            style=wx.CB_READONLY|wx.CB_DROPDOWN
        )
        self.imgFMTCombo.Bind(wx.EVT_COMBOBOX, self._format_change)
        self.labelQ = wx.StaticText(
            panel,
            id=wx.ID_ANY,
            label="Calidad:",
            size=(self.default_label_w, 15),
            style=0,
        )
        self.imgSliderQ = wx.Slider(panel, wx.ID_ANY, 0, 0, 100, size=(self.default_selector_w - 35, 30))
        self.sliderLabel = wx.StaticText(
            panel,
            id=wx.ID_ANY,
            label="100",
            size=(20, 15),
            style=0|wx.RIGHT,
        )
        self.imgSliderQ.Bind(wx.EVT_SLIDER, self._slider_change)
        _imgOPT_FMTBox.Add(labelFMT, 0, wx.TOP, 4)
        _imgOPT_FMTBox.Add(self.imgFMTCombo, 0, wx.EXPAND)
        _imgOPT_FMTBox.AddSpacer(30)
        _imgOPT_FMTBox.Add(self.labelQ, 0, wx.TOP, 4)
        _imgOPT_FMTBox.Add(self.imgSliderQ, 0, wx.EXPAND)
        _imgOPT_FMTBox.Add(self.sliderLabel, 0, wx.TOP, 4)
        
        labelSize = wx.StaticText(
            panel,
            id=wx.ID_ANY,
            label="Tamaño:",
            size=(self.default_label_w, 15),
            style=0,
        )
        self.imgSizeCombo = wx.ComboBox(
            panel, 
            choices = [
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
            size=(self.default_selector_w, 15),
            style=wx.CB_READONLY|wx.CB_DROPDOWN
        )
        labelComp = wx.StaticText(
            panel,
            id=wx.ID_ANY,
            label="Compresión:",
            size=(self.default_label_w, 15),
            style=0,
        )
        self.imgCOMPCombo = wx.ComboBox(
            panel, 
            choices = [
                "Ninguna",
                "LZ4",
                "GZIP",
                "BZIP",
                "LZMA"
            ],
            size=(self.default_selector_w, 15),
            style=wx.CB_READONLY|wx.CB_DROPDOWN
        )
        _imgOPT_CMPBox.Add(labelSize, 0, wx.TOP, 4)
        _imgOPT_CMPBox.Add(self.imgSizeCombo, 0, wx.EXPAND)
        _imgOPT_CMPBox.AddSpacer(30)
        _imgOPT_CMPBox.Add(labelComp, 0, wx.TOP, 4)
        _imgOPT_CMPBox.Add(self.imgCOMPCombo, 0, wx.EXPAND)

        panelBox.Add(_imgOPTSizer, 0, wx.EXPAND|wx.ALL, 10)
        ##--------------------------------------------------##
        
        ##--------------------------------------------------##
        # Atachment Options
        _atmOPTSizerBox = wx.StaticBox(panel, -1, 'Opciones de Adjuntos:')
        _atmOPTSizer = wx.StaticBoxSizer(_atmOPTSizerBox, wx.VERTICAL)
        _atmOPT_FMTBox = wx.BoxSizer(wx.HORIZONTAL)
        _atmOPTSizer.Add(_atmOPT_FMTBox, 0, wx.ALL|wx.EXPAND, 5)
        _atmOPTSizer.AddSpacer(10)
        
        labelSize = wx.StaticText(
            panel,
            id=wx.ID_ANY,
            label="T. Máx. MB:",
            size=(self.default_label_w, 15),
            style=0,
        )
        self.atmMaxSize = PlaceholderTextCtrl.PlaceholderTextCtrl(
            panel, 
            value = "",
            placeholder = "Tam. máximo adjuntos",
            size=(self.default_selector_w - 20, 15),
        )
        labelMB = wx.StaticText(
            panel,
            id=wx.ID_ANY,
            label="MB",
            size=(20, 15),
            style=0|wx.ALIGN_RIGHT,
        )
        labelComp = wx.StaticText(
            panel,
            id=wx.ID_ANY,
            label="Compresión:",
            size=(self.default_label_w, 15),
            style=0,
        )
        self.atmCOMPCombo = wx.ComboBox(
            panel, 
            choices = [
                "Ninguna",
                "LZ4",
                "GZIP",
                "BZIP",
                "LZMA"
            ],
            size=(self.default_selector_w, 15),
            style=wx.CB_READONLY|wx.CB_DROPDOWN
        )
        _atmOPT_FMTBox.Add(labelSize, 0, wx.TOP, 4)
        _atmOPT_FMTBox.Add(self.atmMaxSize, 0, wx.EXPAND)
        _atmOPT_FMTBox.Add(labelMB, 0, wx.TOP, 3)
        _atmOPT_FMTBox.AddSpacer(30)
        _atmOPT_FMTBox.Add(labelComp, 0, wx.TOP, 4)
        _atmOPT_FMTBox.Add(self.atmCOMPCombo, 0, wx.EXPAND)

        panelBox.Add(_atmOPTSizer, 0, wx.EXPAND|wx.ALL, 10)
        ##--------------------------------------------------##
        
        ##--------------------------------------------------##
        # Buttons BoxSizer
        btn_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        btn_add = wx.Button(panel, label="Aceptar")
        btn_add.Bind(wx.EVT_BUTTON, self._save_options)
        btn_cancel = wx.Button(panel, label="Cancelar")
        btn_cancel.Bind(wx.EVT_BUTTON, self.close_dialog)
        btn_sizer.AddSpacer(10)
        btn_sizer.Add(btn_add)
        btn_sizer.AddSpacer(40)
        btn_sizer.Add(btn_cancel)
        btn_sizer.AddSpacer(10)
        
        panelBox.Add(btn_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)
        ##--------------------------------------------------##
        
        panel.SetSizer(panelBox)
        self._load_options()
        
        


#options(None).Show()
#app.MainLoop()