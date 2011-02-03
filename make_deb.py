#!/usr/bin/python
# coding: utf-8

import os
import shutil
import sys
import errno
from distutils.dir_util import copy_tree

from kabukiman.version import get_version

def mkdir_p(path):
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


DEBNAME = "kabukiman"
DEBVERSION = get_version()
DEBMAINT = "Lucas Alvares Gomes [lucasagomes@gmail.com]"
DEBARCH = "i386"
DEBDEPENDS = "python2.6, python-gtk2, python-xlib"
DEBDESC = "A simple dictionary application"

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

DEBFILES = [
    ("kabukiman", "usr/local/lib/python2.6/dist-packages/kabukiman"),
    ("scripts/kabukiman", "usr/local/bin/kabukiman"),
    ("glade", "usr/local/share/kabukiman/glade"),
    ("icons", "usr/local/share/kabukiman/icons"), 
    ("modules", "usr/local/lib/kabukiman/modules"),
    ("kabukiman.desktop", "usr/share/applications/kabukiman.desktop"),
    ("icons/kabukiman.png", "usr/share/pixmaps/kabukiman.png"),
]

if os.path.exists("build"): shutil.rmtree("build")
BUILD_DIR = "build/deb/%s/" % DEBNAME
mkdir_p(BUILD_DIR)

DEBCONTROLFILE = os.path.join(DEBNAME, "DEBIAN/control")

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

# Creating the control file
mkdir_p(BUILD_DIR + "DEBIAN")
installed_size = get_folder_size(BUILD_DIR)/1024 #kb

control_info = CONTROL_TEMPLATE % (
    DEBNAME, installed_size, DEBMAINT, DEBARCH,
    get_version(), DEBDEPENDS, DEBDESC
    )

with open(BUILD_DIR + "DEBIAN" + "/control", 'w') as f:
    f.write(control_info)

# Create the deb file
mkdir_p("dist")
debpkg = "%s_%s-%s.deb" % (DEBNAME, DEBVERSION, DEBARCH)
os.system("fakeroot dpkg-deb -b %s %s" % (BUILD_DIR, "dist/" + debpkg))

