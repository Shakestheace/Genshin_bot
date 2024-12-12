import os
import shutil
import sys
from pathlib import Path
from subprocess import run as bashrun

from bot import version_file

from .log_utils import log

if not os.path.isdir("downloads/"):
    os.mkdir("downloads/")
if not os.path.isdir("enka/"):
    os.mkdir("enka/")


def qclean():
    try:
        os.system("rm -rf downloads/*")
    except Exception:
        pass


def re_x(i, msg):
    qclean()
    os.execl(sys.executable, sys.executable, "-m", "bot", i, msg)


def updater(msg=None):
    try:
        with open(version_file, "r") as file:
            ver = file.read()
        qclean()
        Path("update").touch()
        bashrun(["python3", "update.py"])
        with open(version_file, "r") as file:
            ver2 = file.read()

        if ver != ver2:
            vmsg = True
        else:
            vmsg = False

        if msg:
            message = str(msg.chat.id) + ":" + str(msg.id)
            os.execl(
                sys.executable, sys.executable, "-m", "bot", f"update {vmsg}", message
            )
        else:
            os.execl(sys.executable, sys.executable, "-m", "bot")
    except Exception:
        log(Exception)


def s_remove(*filenames, folders=False):
    """Deletes a single or tuple of files silently and return no errors if not found"""
    if folders:
        for _dir in filenames:
            try:
                shutil.rmtree(_dir)
            except Exception:
                pass
        return
    for filename in filenames:
        try:
            os.remove(filename)
        except OSError:
            pass


def read_n_to_last_line(filename, n=1):
    """Returns the nth before last line of a file (n=1 gives last line)"""
    num_newlines = 0
    with open(filename, "rb") as f:
        try:
            f.seek(-2, os.SEEK_END)
            while num_newlines < n:
                f.seek(-2, os.SEEK_CUR)
                if f.read(1) == b"\n":
                    num_newlines += 1
        except OSError:
            f.seek(0)
        last_line = f.readline().decode()
    return last_line


def file_exists(file):
    return Path(file).is_file()
