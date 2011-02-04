#!/usr/bin/python
# coding: utf-8
# Copyright (C) 2010 Lucas Alvares Gomes <lucasagomes@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import os
import glob
import platform
import sys
import shutil
import errno
import py_compile
from distutils.dir_util import copy_tree
from distutils.core import setup
from distutils import cmd
from distutils.command.install_data import install_data as _install_data
from distutils.command.build import build as _build

from extern import msgfmt
from kabukiman.version import get_version


if "--prefix=" in sys.argv:
    print >> sys.stderr, "Prefix not supported"
    sys.exit(-1)


### Globals
NAME = "kabukiman"
VERSION = get_version()
MAINT = "Lucas Alvares Gomes [lucasagomes@gmail.com]"
ARCH = "all"
DEPENDS = "python2.6, python-gtk2, python-xlib"
DESC = "A simple dictionary application"

### Utils
def mkdir_p(path):
    """mkdir -p in python"""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise

def get_folder_size(folder):
    folder_size = 0
    for (path, dirs, files) in os.walk(folder):
        for file in files:
            filename = os.path.join(path, file)
            folder_size += os.path.getsize(filename)

    return folder_size

def build_mo():
    """ Build .po in .mo """
    po_dir = os.path.join(os.path.dirname(os.curdir), "po")
    for path, names, filenames in os.walk(po_dir):
        for f in filenames:
            if f.endswith(".po"):
                lang = f[:len(f) - 3]
                src = os.path.join(path, f)
                dest_path = os.path.join("build", "locale", lang, "LC_MESSAGES")
                dest = os.path.join(dest_path, "kabukiman.mo")
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)
                if not os.path.exists(dest):
                    msgfmt.make(src, dest)
                else:
                    src_mtime = os.stat(src)[8]
                    dest_mtime = os.stat(dest)[8]
                    if src_mtime > dest_mtime:
                        msgfmt.make(src, dest)

def compile_py(path):
    # Importance of .pyc:
    # https://fedoraproject.org/wiki/Packaging:Python#Files_to_include
    for path, names, filenames in os.walk(path):
        for f in filenames:
            if f.endswith(".py"):
                src = os.path.join(path, f)
                py_compile.compile(src)

### Debian File
# TODO: Compile .po's file
if "--deb" in sys.argv:

    py_version = platform.python_version_tuple()
    py_version = "%s.%s" % (py_version[0], py_version[1])

    DEBFILES = [
        ("build/locale", "usr/share/locale"),
        ("kabukiman", "usr/local/lib/python%s/dist-packages/kabukiman" % py_version),
        ("scripts/kabukiman", "usr/local/bin/kabukiman"),
        ("glade", "usr/local/share/kabukiman/glade"),
        ("icons", "usr/local/share/kabukiman/icons"), 
        ("modules", "usr/local/lib/kabukiman/modules"),
        ("kabukiman.desktop", "usr/share/applications/kabukiman.desktop"),
        ("icons/kabukiman.png", "usr/share/pixmaps/kabukiman.png"),
    ]

    if os.path.exists("build"): shutil.rmtree("build")
    BUILD_DIR = "build/deb/%s/" % NAME
    mkdir_p(BUILD_DIR)

    build_mo()

    DEBCONTROLFILE = os.path.join(NAME, "DEBIAN/control")

    for f in DEBFILES:
        dest = os.path.join(BUILD_DIR, f[0])
        if os.path.isdir(f[0]):
            dest = BUILD_DIR + f[1]
            mkdir_p(dest)
            copy_tree(f[0], dest) 
        else:
            basedir = os.path.dirname(f[1])
            dest = BUILD_DIR + basedir
            mkdir_p(dest)
            shutil.copy2(f[0], dest)

    compile_py(BUILD_DIR)

    # Creating the control file
    CONTROL_TEMPLATE = """\
Package: %s
Priority: optional
Section: misc
Installed-Size: %d
Maintainer: %s
Architecture: %s
Version: %s
Depends: %s
Description: %s

"""

    mkdir_p(BUILD_DIR + "DEBIAN")
    installed_size = get_folder_size(BUILD_DIR)/1024 #kb

    control_info = CONTROL_TEMPLATE % (
        NAME, installed_size, MAINT, ARCH,
        VERSION, DEPENDS, DESC)

    with open(BUILD_DIR + "DEBIAN" + "/control", 'w') as f:
        f.write(control_info)

    # Create the deb file
    mkdir_p("dist")
    debpkg = "%s_%s-%s.deb" % (NAME, VERSION, ARCH)
    os.system("fakeroot dpkg-deb -b %s %s" % (BUILD_DIR, "dist/" + debpkg))
    sys.exit(0)


### Distutils
# Thanks to http://wiki.maemo.org/How_to_Internationalize_python_apps
class build_trans(cmd.Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        build_mo()

class build(_build):
    sub_commands = _build.sub_commands + [("build_trans", None)]
    def run(self):
        _build.run(self)

class install_data(_install_data):
    def run(self):
        for lang in os.listdir(os.sep.join(("build","locale"))):
            lang_dir = os.path.join("/usr", "share", "locale", lang, "LC_MESSAGES")
            lang_file = os.path.join("build", "locale", lang, "LC_MESSAGES", "kabukiman.mo")
            self.data_files.append((lang_dir, [lang_file]))
        _install_data.run(self)


# Fill data_file
data_files = list()
data_files.append(("/usr/local/share/kabukiman/glade", glob.glob("glade/*.glade")))

for (path, dirs, files) in os.walk("modules"):
    p = "/usr/local/lib/kabukiman/" + path
    f = map(lambda x: path + os.sep + x, files)
    data_files.append((p, f))

for (path, dirs, files) in os.walk("icons"):
    p = "/usr/local/share/kabukiman/" + path
    f = map(lambda x: path + os.sep + x, files)
    data_files.append((p, f))

data_files.append(("/usr/share/applications", ["kabukiman.desktop"]))
data_files.append(("/usr/share/pixmaps", ["icons/kabukiman.png"]))

cmdclass = {
    "build": build,
    "build_trans": build_trans,
    "install_data": install_data,
}

setup(name = NAME,
      version = VERSION,
      author = "Lucas Alvares Gomes",
      author_email = "lucasagomes@gmail.com",
      url = "http://umago.info",
      description = DESC,
      license = "GNU GPLv3",
      cmdclass = cmdclass,
      packages = ["kabukiman","kabukiman.core", 
                  "kabukiman.core.shortcut",
                  "kabukiman.ui"],
      data_files = data_files,
      scripts = [os.sep.join(("scripts", "kabukiman"))],
      )
