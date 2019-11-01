# -*- coding: utf-8 -*-

# globals.py
from logging import getLogger, DEBUG
from wx import (
    Font,
    FONTFAMILY_SWISS,
    FONTSTYLE_SLANT,
    FONTWEIGHT_BOLD,
    FONTENCODING_DEFAULT,
    FONTWEIGHT_NORMAL
)
from os import path
import sys
from screeninfo import get_monitors
from modules import iniReader

log = getLogger()


def init():
    global field_kind
    field_kind = [
        "CheckBox",
        "ComboBox",
        "Input"
    ]

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
        },
        "main_window": {
            "maximized": 0,
            "size_w": 800,
            "size_h": 900,
            "pos_x":  (get_monitors()[0].width/2) - 400,
            "pos_y":  (get_monitors()[0].height/2) - 450
        },
        "components_db": {
            "mode": 0,
            "sqlite_file": "components.sqlite3",
            "mysql_host": "127.0.0.1",
            "mysql_port": "3306",
            "mysql_user": "root",
            "mysql_pass": "",
            "mysql_dbase": "Components"
        },
        "templates_db": {
            "mode": 0,
            "sqlite_file": "templates.sqlite3",
            "mysql_host": "127.0.0.1",
            "mysql_port": "3306",
            "mysql_user": "root",
            "mysql_pass": "",
            "mysql_dbase": "Templates"
        }
    }
    config = iniReader.LoadConfigToDict("config.ini", _defaultConfig)

    # Fix to avoid the window to be out of the screen.
    # (usefull when the new screen is smaler)
    if not config:
        log.error("There was an error loading config file")
        exit(1)

    if (
        config["main_window"]["pos_x"] +
        config["main_window"]["size_w"] > get_monitors()[0].width
    ):
        config["main_window"]["pos_x"] = (
            get_monitors()[0].width - config["main_window"]["size_w"]
        )

    if (
        config["main_window"]["pos_y"] +
        config["main_window"]["size_h"] > get_monitors()[0].height
    ):
        config["main_window"]["pos_y"] = (
            get_monitors()[0].height - config["main_window"]["size_h"]
        )

    global rootPath
    if getattr(sys, 'frozen', False):
        # The application is frozen
        rootPath = path.dirname(path.realpath(sys.executable))
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        rootPath = path.dirname(path.realpath(__file__))

    # Create a real database path values
    if (
        not config['components_db']['sqlite_file'][0] == '/'
        and ":" not in config['components_db']['sqlite_file']
    ):
        config['components_db']['sqlite_file_real'] = path.join(
            rootPath,
            config['components_db']['sqlite_file']
        )
    else:
        config['components_db']['sqlite_file_real'] = config['components_db']['sqlite_file']

    if (
        not config['templates_db']['sqlite_file'][0] == '/'
        and ":" not in config['templates_db']['sqlite_file']
    ):
        config['templates_db']['sqlite_file_real'] = path.join(
            rootPath,
            config['templates_db']['sqlite_file']
        )
    else:
        config['templates_db']['sqlite_file_real'] = config['templates_db']['sqlite_file']

    # Data from DB
    global options
    options = {
        "logLevel": DEBUG,
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
    labelFormat = Font(10, FONTFAMILY_SWISS, FONTSTYLE_SLANT,
                       FONTWEIGHT_BOLD, underline=False, faceName="Segoe UI",
                       encoding=FONTENCODING_DEFAULT)
    global textBoxFormat
    textBoxFormat = Font(10, FONTFAMILY_SWISS, FONTSTYLE_SLANT,
                         FONTWEIGHT_NORMAL, underline=False,
                         faceName="Segoe UI", encoding=FONTENCODING_DEFAULT)
