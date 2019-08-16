#setup.py
import sys, os
from cx_Freeze import setup, Executable

__version__ = "0.5.3"

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

include_files = [
    'images',
    'templates',
]

# packages to include/exclude
includes = {
    "external": [],
    "zip": ["io", "json", "logging", "platform", "playsound", "sqlite3", "subprocess", "sys", "urllib", "widgets.ShapedButton", "windows", "win32com", "wx", "wx.html2"]
}
excludes = {
    "external": ["OpenGL", "email", "html", "pydoc_data", "unittest", "http", "xml", "pkg_resources"],
    "zip": []
}

setup (
  name = "Components Manager",
  description='Program that allow you to keep a list of your components',
  version=__version__,
  options = {
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
  executables = [
    Executable(
      "manager.py",
      base="Win32GUI",
      icon="images/icon.ico",
    )
  ]
)