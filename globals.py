# -*- coding: utf-8 -*-

# globals.py
import logging
import wx
from os import path
import sys

log = logging.getLogger("MainWindow")

from modules import iniReader

def init():
        global config
        _defaultConfig = {
            "folders": {
                "images": "images/",
                "audio": "audio/",
                "plugins": "plugins/",
                "components": "templates/components/",
                "values": "templates/values/"
            },
            "images": {
                "format": 0,
                "png_compression": 9,
                "jpeg_quality": 85,
                "size": 4,
                "compression": 4
            },
            "attachments": {
                "max_size": 25,
                "compression": 4
            }
        }
        config = iniReader.LoadConfigToDict("config.ini", _defaultConfig)
        
        global rootPath
        if getattr(sys, 'frozen', False):
                # The application is frozen
                rootPath = path.dirname(path.realpath(sys.executable))
        else:
                # The application is not frozen
                # Change this bit to match where you store your data files:
                rootPath = path.dirname(path.realpath(__file__))
        
        # Data from DB
        global options
        options = {
            "logLevel": logging.DEBUG,
            "logFile": "{}/main.log".format(rootPath),
            "savesFolder": "Saves",
            "lastDirIcon": "",
            "lastDirSaves": "",
            "moveOnAdd": False,
            "linkOnAdd": True,
            "generateJson": True,
            "backgroundColor": (0, 240, 240, 255)
        }

        # Formatos
        global labelFormat
        labelFormat = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_SLANT,
                wx.FONTWEIGHT_BOLD, underline=False, faceName="Segoe UI",
                encoding=wx.FONTENCODING_DEFAULT)
        global textBoxFormat
        textBoxFormat = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_SLANT,
                wx.FONTWEIGHT_NORMAL, underline=False, faceName="Segoe UI",
                encoding=wx.FONTENCODING_DEFAULT)