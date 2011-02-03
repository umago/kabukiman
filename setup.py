#!/usr/bin/python
# coding: utf-8
# Copyright (C) 2010 Lucas Alvares Gomes <lucasagomes@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
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
import sys
from distutils.core import setup
from distutils import cmd
from distutils.command.install_data import install_data as _install_data
from distutils.command.build import build as _build

from extern import msgfmt

from kabukiman.version import get_version

# I tried >.<, but idk why ubuntu ignore the sys.prefix
# in fedora it works out-of-the-box!!!!
# http://ubuntuforums.org/showthread.php?t=1121501
for arg in sys.argv:
    if arg.startswith("--prefix="):
        print >> sys.stderr, "Prefix not supported"
        sys.exit(-1)

# Thanks to http://wiki.maemo.org/How_to_Internationalize_python_apps
class build_trans(cmd.Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
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

setup(name = "kabukiman",
      version = get_version(),
      author = "Lucas Alvares Gomes",
      author_email = "lucasagomes@gmail.com",
      url = "http://umago.info",
      description = "A simple dictionary application",
      license = "GNU GPLv3",
      cmdclass = cmdclass,
      packages = ["kabukiman","kabukiman.core", 
                  "kabukiman.core.shortcut",
                  "kabukiman.ui"],
      data_files = data_files,
      scripts = [os.sep.join(("scripts", "kabukiman"))],
      )
