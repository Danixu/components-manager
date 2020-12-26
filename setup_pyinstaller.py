#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
17 Aug 2019
@autor: Daniel Carrasco
'''

import PyInstaller.__main__
from os import path, makedirs, remove
import glob
import shutil

# Package Options
package_name = "Components Manager"
package_file = "manager.py"
onefile = True
console = False
icon = "images/icon.ico"
# Encryption Key must have 16 characters.
encryption_key = None
# Compression options
upx = False
upx_excluded = [
    "vcruntime140.dll",
]
# Included/Excluded modules and files
included_data = [
    (
        "images/*.*",
        "images/"
    ),
    (
        "images/filetypes/*.*",
        "images/filetypes/"
    ),
    (
        "plugins/database/sqlite/sqlite_components.sql",
        "plugins/database/sqlite/"
    ),
    (
        "plugins/database/sqlite/sqlite_templates.sql",
        "plugins/database/sqlite/"
    )
]
included_binary = []
included_external = []
included_modules = [
    "screeninfo.enumerators.cygwin",
    "screeninfo.enumerators.drm",
    "screeninfo.enumerators.osx",
    "screeninfo.enumerators.windows",
    "screeninfo.enumerators.xinerama",
    "screeninfo.enumerators.xrandr"
]
excluded_modules = [
    "OpenGL",
    "email",
    "html",
    "pydoc_data",
    "unittest",
    "http",
    "xml",
    "pkg_resources",
    "numpy"
]
# Compile Options
noconfirm = True
clean = True
log_level = "DEBUG"
version = (1, 3, 1, 0)


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

for item in included_modules:
    pyInstaller_cmd.append("--hidden-import={}".format(item))

for item in excluded_modules:
    pyInstaller_cmd.append("--exclude-module={}".format(item))

if noconfirm:
    pyInstaller_cmd.append("--noconfirm")

if clean:
    pyInstaller_cmd.append("--clean")

if log_level:
    pyInstaller_cmd.append("--log-level={}".format(log_level))

pyInstaller_cmd.append(package_file)

# Creating Version file
version_data = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({0}, {1}, {2}, {3}),
    prodvers=({0}, {1}, {2}, {3}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Danixu'),
        StringStruct(u'FileDescription', u'{4}'),
        StringStruct(u'FileVersion', u'{0}.{1}.{2}.{3}'),
        StringStruct(u'InternalName', u'{4}'),
        StringStruct(u'LegalCopyright', u'\xa9 Danixu'),
        StringStruct(u'OriginalFilename', u'{4}'),
        StringStruct(u'ProductName', u'{4}'),
        StringStruct(u'ProductVersion', u'{0}.{1}.{2}.{3}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)""".format(
    version[0],
    version[1],
    version[2],
    version[3],
    package_name
)

with open("version", "w", encoding='utf8') as version_file:
    version_file.write(version_data)

pyInstaller_cmd.append("--version-file=version")

print(pyInstaller_cmd)

PyInstaller.__main__.run(pyInstaller_cmd)

remove("version")

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
