from sys import platform
if platform == "win32":
    from os import startfile
else:
    from subprocess import call


def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])
