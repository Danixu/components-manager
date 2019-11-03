# Components Manager

A simple program to manage your electronic components stock

## Getting Started

### Prerequisites
* Python 3
* ~~Python 3.7.4 or at least sqlite 3.24.0 libraries (3.7.3 uses older libraries)~~ Removed function, so is not required anymore.
* Modules from requirements.txt (wxpython takes a long time to install)

### Installation
* Install gtk+ on Linux (needed for WX module) ```sudo apt-get install libgtk-3-dev```
* Install python modules in requirements.txt

## ToDO
* ~~PEP8~~
* ~~Add support for MySQL~~
* ~~Separate options in tabs~~
* ~~Add BBDD Options to configure MySQL and SQLite~~
* ~~Move the image buttons to new bar on bottom of image box~~
* ~~Export images~~
* ~~Show image with external program on double click~~
* Check if DB options are rigth and can connect to MySQL
* ~~Encrypt the dbase password in ini file~~
* Add Random PBKDF2HMAC iterations number
* Add Support for linux (just a few fixes to make it work)
* ~~Better integration between databases~~
* Optimize the code

## Authors
* **Daniel Carrasco**

# Notes
* Using pycparser v2.19 make pyinstaller to fail. You have to downgrade to v2.14
```
pip uninstall pycparser
pip install pycparser==2.14
```
