# setup.py
import sys
import os
from cx_Freeze import setup, Executable

__version__ = "1.3.2"

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

include_files = [
    'images'
]

# packages to include/exclude
includes = {
    "external": [
        "screeninfo",
        "screeninfo.enumerators.cygwin",
        "screeninfo.enumerators.drm",
        "screeninfo.enumerators.osx",
        "screeninfo.enumerators.windows",
        "screeninfo.enumerators.xinerama",
        "screeninfo.enumerators.xrandr"
    ],
    "zip": [
        "io",
        "json",
        "logging",
        "platform",
        "playsound",
        "sqlite3",
        "subprocess",
        "sys",
        "urllib",
        "widgets.ShapedButton",
        "windows",
        "win32com",
        "wx",
        "wx.html2",
        "lz4"
    ]
}
excludes = {
    "external": [
        "OpenGL",
        "email",
        "html",
        "pydoc_data",
        "unittest",
        "http",
        "xml",
        "pkg_resources"
    ],
    "zip": []
}

setup(
    name="Components Manager",
    description='Program that allow you to keep a list of your components',
    version=__version__,
    options={
        'build_exe': {
            'include_files': include_files,
            'includes': includes['external'],
            'excludes': excludes['external'],
            'include_msvcr': True,
            'zip_include_packages': includes['zip'],
            'zip_exclude_packages': excludes['zip'],
            "optimize": 2,
        }
    },
    executables=[
        Executable(
            "manager.py",
            base="Win32GUI",
            icon="images/icon.ico",
        )
    ]
)
