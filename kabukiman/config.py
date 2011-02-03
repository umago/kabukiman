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
import sys
import gettext
import locale

from kabukiman.utils import *

def init_gettext():
    try:
         locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
         pass
    gettext.install(APP_NAME, unicode=True)
    gettext.textdomain(APP_NAME)

    # Python 2.4 compatibility
    import __builtin__
    __builtin__.__dict__['gettext'] = __builtin__.__dict__['_']
    __builtin__.__dict__['ngettext'] = gettext.ngettext

APP_NAME = "kabukiman"
LOCALEDIR = ''
DATADIR = "/usr/local/share/kabukiman"
ICONS_DIR = os.path.join(DATADIR, "icons")
CONFIGDIR = os.path.join(get_home_dir(), '.' + APP_NAME)
CONFIG_FILE = os.path.join(CONFIGDIR, "kabukiman.conf")
MODULES_DIRS = list((os.path.join(CONFIGDIR, "modules"), \
             os.path.join(sys.prefix, "local", "lib", "kabukiman", "modules")))
GLADE_NAME = os.path.join(DATADIR, "glade", APP_NAME + ".glade")
COPYRIGHT = "(C) 2010 Lucas Alvares Gomes"
AUTHORS = (
    "Lucas Alvares Gomes <lucasagomes@gmail.com>",
    )
ARTISTS = (
    "Daniel Nardo Slaghenaufi <daniel.nardo@hotmail.com>",
    )
LICENSE = (
    "This program is free software; you can redistribute it and/or modify \n"
    "it under the terms of the GNU General Public License as published by \n"
    "the Free Software Foundation; either version 3 of the License, or \n"
    "(at your option) any later version.\n"
    "\n"
    "This program is distributed in the hope that it will be useful, \n"
    "but WITHOUT ANY WARRANTY; without even the implied warranty of \n"
    "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the \n"
    "GNU General Public License for more details.\n"
    "\n"
    "You should have received a copy of the GNU General Public License \n"
    "along with this program. If not, see <http://www.gnu.org/licenses/>.")
