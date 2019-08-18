#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
17 Aug 2019
@autor: Daniel Carrasco
'''

import PyInstaller.__main__
from os import path, makedirs
import sys
import glob
import shutil

#Package Options
package_name = "Components Manager"
package_file = "manager.py"
onefile = True
console = False
icon = "images/icon.ico"
# Encryption Key must have 16 characters.
encryption_key = None
#Compression options
upx = False
upx_excluded = [
    "vcruntime140.dll",
]
# Included/Excluded modules and files
included_data = [
    ("images/*.*", "images/"),
    ("plugins/database/sqlite.sql", "plugins/database/")
]
included_binary = []
included_external = [
    ("templates/components/*.*", "templates/components"),
    ("templates/values/*.*", "templates/values")
]
excluded_modules = ["OpenGL", "email", "html", "pydoc_data", "unittest", "http", "xml", "pkg_resources", "socket", "numpy"]
#Compile Options
noconfirm = True
clean = True
log_level = "DEBUG"


# Build the command
pyInstaller_cmd = [
    '--name=%s' % package_name
]

if onefile:
    pyInstaller_cmd.append("--onefile")

if console:
    pyInstaller_cmd.append("--console")
else:
    pyInstaller_cmd.append("--windowed")
    
if icon:
    pyInstaller_cmd.append("--icon={}".format(icon))
    
if encryption_key:
    pyInstaller_cmd.append("--key={}".format(encryption_key))
    
if not upx:
    pyInstaller_cmd.append("--noupx")
else:
    for item in upx_excluded:
        pyInstaller_cmd.append("--upx-exclude={}".format(item))
    
for item in included_data:
    pyInstaller_cmd.append("--add-data={};{}".format(item[0], item[1]))
    
for item in included_binary:
    pyInstaller_cmd.append("--add-binary={};{}".format(item[0], item[1]))
    
for item in excluded_modules:
    pyInstaller_cmd.append("--exclude-module={}".format(item))
    
if noconfirm:
    pyInstaller_cmd.append("--noconfirm")
    
if clean:
    pyInstaller_cmd.append("--clean")
    
if log_level:
    pyInstaller_cmd.append("--log-level={}".format(log_level))

pyInstaller_cmd.append(package_file)

print(pyInstaller_cmd)

PyInstaller.__main__.run(pyInstaller_cmd)

# copying external files to output folder
output = "dist/"
if not onefile:
    output = path.join(output, package_name)

for toCopy in included_external:
    dest_dir = path.join(output, toCopy[1])
    if not path.isdir(dest_dir):
        makedirs(dest_dir)
        
    for file in glob.glob(toCopy[0]):
        print("Copying file {} to folder {}".format(file, dest_dir))
        try:
            shutil.copy(file, dest_dir)
        except Exception as e:
            print("There was an error copying the file: {}".format(e))