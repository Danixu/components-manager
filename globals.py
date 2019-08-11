# -*- coding: utf-8 -*-

# globals.py
from io import BytesIO
from PIL import Image
import datetime
import logging
import wx
import os
import sys

log = logging.getLogger("cManager")

def _(str):
  return str

def init():
        global dataFolder
        dataFolder = {
            "images": "images/",
            "audio": "audio/",
            "plugins": "plugins/",
        }
        
        global rootPath
        if getattr(sys, 'frozen', False):
                # The application is frozen
                rootPath = os.path.dirname(os.path.realpath(sys.executable))
        else:
                # The application is not frozen
                # Change this bit to match where you store your data files:
                rootPath = os.path.dirname(os.path.realpath(__file__))
        
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

        
def strToValue(str, kind):
    if kind == "bool":
        if str.lower() == "true":
            return True
        else:
            return False
            
    if kind == "int":
        return int(str)
        
    return str  

            
def fullPath(path):
    if ":" in path or path[0] == "/":
        return path
    else:
        return os.path.join(rootPath, path)

        
def relativePath(path):
    if ":" in path or path[0] == "/":
        return path.replace("{}\\".format(rootPath.rstrip("\\")), "")
    else:
        return path

        
def folderToWindowsVariable(folder):
    for variable, value in CSIDL_Values.items():
        folder = folder.replace(
            shell.SHGetFolderPath(0, value, None, 0),
            "%{}%".format(variable)
        )
    return folder


def windowsVariableToFolder(folder):
    for variable, value in CSIDL_Values.items():
        folder = folder.replace(
            "%{}%".format(variable),
            shell.SHGetFolderPath(0, value, None, 0)
        )
        
    return folder

    
def remove_transparency(im, bg_colour=(255, 255, 255)):
    try:
        # Only process if image has transparency (http://stackoverflow.com/a/1963146)
        if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
            # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
            alpha = im.convert('RGBA').split()[-1]
            # Create a new background image of our matt color.
            # Must be RGBA because paste requires both images have the same format
            # (http://stackoverflow.com/a/8720632    and    http://stackoverflow.com/a/9459208)
            bg = Image.new("RGBA", im.size, bg_colour + (255,))
            bg.paste(im, mask=alpha)
            return bg

        else:
            return im
    except Exception as e:
        log.error(
            "There was an error removing the transparency from the image:" +
            " {}".format(e)
        )
        dlg = wx.MessageDialog(
            None,
            _("There was an error. Please go to log for more info."),
            style=wx.OK | wx.ICON_ERROR
        )
        dlg.ShowModal()
        return False
                
def imageResize(fName, nWidth=44, nHeight=44, centered=True, color=(255, 255, 255, 255)):
    log = logging.getLogger("SavegameLinker")
    if not fName == None and os.path.isfile(fName):
        # The file is saved to BytesIO and reopened because
        # if not, some ico files are not resized correctly
        try:
            log.debug("Creating BytesIO data")
            tmp_data = BytesIO()
            log.debug("Opening source image file")
            tmp_image = Image.open(fName)
            log.debug("Creating temporal data in memory to allow resize")
            tmp_image.save(tmp_data, "PNG", compress_level = 1)
            log.debug("Closing the source image")
            tmp_image.close()
        except Exception as e:
            log.error("There was an error opening the image: {}".format(e))
            dlg = wx.MessageDialog(
                None,
                _("There was an error. Please go to log for more info."),
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            return False
        
        try:
            tmp_image = Image.open(tmp_data)
        except Exception as e:
            log.error("There was an error opening the image: {}".format(e))
            dlg = wx.MessageDialog(
                None,
                _("There was an error. Please go to log for more info."),
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            return False
        
        try:
            if tmp_image.size[0] < nWidth and tmp_image.size[1] < nHeight:
                log.debug("Size is smaller than indicated size")
                width, height = tmp_image.size
            
                if width > height:
                    factor = nWidth / width
                    width = nWidth
                    height = int(height * factor)
                    
                    # if height%2 > 0:
                        # height += 1
                    
                    log.debug("Resizing image...")
                    tmp_image = tmp_image.resize((width, height), Image.LANCZOS)
                else:
                    factor = nHeight / height
                    width = int(width * factor)
                    height = nHeight
                    
                    # if width%2 > 0:
                        # height += 1
                    
                    log.debug("Resizing image...")
                    tmp_image = tmp_image.resize((width, height), Image.LANCZOS)

            else:
                log.debug("The image is bigger than indicated size...")
                log.info("Creating thumbnail.")
                tmp_image.thumbnail((nWidth, nHeight), Image.LANCZOS)
        except Exception as e:
            log.error("There was an error resizing the image: {}".format(e))
            dlg = wx.MessageDialog(
                None,
                _("There was an error. Please go to log for more info."),
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            return False

        try:
            log.debug("Centering image...")
            if centered and tmp_image.size[0] != tmp_image.size[1]:
                new_image = Image.new("RGBA", (nWidth, nHeight), color)
                new_image.paste(
                        tmp_image,
                        (
                            int((nWidth-tmp_image.size[0])/2),
                            int((nHeight-tmp_image.size[1])/2)
                        )
                    )
                tmp_image.close()
                icon_data = BytesIO()
                new_image.save(icon_data, "PNG", optimize=True)
                new_image.close()
                tmp_data.close()
                return icon_data
            else:
                icon_data = BytesIO()
                tmp_image.save(icon_data, "PNG", optimize=True)
                tmp_image.close()
                tmp_data.close()
                return icon_data
        except Exception as e:
            log.error("There was an error centering the image: {}".format(e))
            dlg = wx.MessageDialog(
                None,
                _("There was an error. Please go to log for more info."),
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            return False
            
    else:
        return None