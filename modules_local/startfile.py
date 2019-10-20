from sys import platform
if platform == "win32":
    from os import startfile
else:
    from subprocess import call


def open_file(filename):
    if platform == "win32":
        startfile(filename)
    else:
        opener ="open" if platform == "darwin" else "xdg-open"
        call([opener, filename])
