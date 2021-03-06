# Components Manager

A simple program to manage your electronic components stock

## Getting Started

### Running it from source
If you don't want to use the precompiled binaries, you can run the manager.py file directy to use the application, but first you need to install the required modules. To do it, follow this steps, that also are required if you wants to build the binary from source.

#### Linux
* Install gtk+ on Linux (needed for WX module) ```sudo apt-get install libgtk-3-dev```
* Install python modules in requirements.txt

#### Windows
* Download and install Python 3.9: https://www.python.org/downloads/
* Download and install Visual Studio Build Tools: https://visualstudio.microsoft.com/es/visual-cpp-build-tools/
* Install the required modules in requirements.txt: `pip install -r requirements.txt`


### Compilation
First you have to follow the steps of the **Running it from source** section, and once the program can run from source, then is ready to start the compilation process.

#### Windows
* Install de required modules from the requirements.txt inside the tools folder
* Run the file build_pyInstaller.cmd located on tools folder to build the exe file. Once the process is finished, the exe file will be on dist folder.

## ToDO
* ~~PEP8~~
* ~~Add support for MySQL~~
* ~~Separate options in tabs~~
* ~~Add BBDD Options to configure MySQL and SQLite~~
* ~~Move the image buttons to new bar on bottom of image box~~
* ~~Export images~~
* ~~Show image with external program on double click~~
* ~~Check if DB options are rigth and can connect to MySQL~~
* ~~Encrypt the dbase password in ini file~~
* ~~Add Random PBKDF2HMAC iterations number~~
* Remove password hash from ini file because is less secure, and replace it by an encrypted PBKDF2HMAC known string
* Add Support for linux (just a few fixes to make it work)
* ~~Better integration between databases~~

## Authors
* **Daniel Carrasco**

# Notes
* Using pycparser v2.19 make pyinstaller to fail. You have to downgrade to v2.14
```
pip uninstall pycparser
pip install pycparser==2.14
```

## Changelog
1.3.2
* Fixed a bug in the search box that will cause to no refresh the item list when no items are found.

1.3.1
* Fixed a bug adding a component into a category with component template set, and then changing the category to another without subcategory.
* Changed license to GPL

1.3.0
* Updated modules to latest version on requirementes
* Fixed a bug in image resize that causes a resizing loop
* Fixed the program reposition if it is out of the screen
