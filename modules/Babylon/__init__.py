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

import urllib
import simplejson
import gtk
import os
import cPickle

from dialog_config import DialogConfig
from db import DataBase

from kabukiman.module import Module
from kabukiman.utils import *

class Babylon(Module):
    """The Google Translate Module"""

    def __init__(self):
        Module.__init__(self)
        self.config_file = os.sep.join((get_home_dir(), ".kabukiman", "babylon", "babylon.cfg"))

    def is_configurable(self):
        """  """
        return True

    def look_up(self, word):
        """  """
        result = ''
        if os.path.exists(self.config_file):
            dicts = None
            with open(self.config_file, 'rb') as f:
                dicts = cPickle.load(f)

            for title, path in dicts:
                db = DataBase()
                db.open(path)
                definition = db.look_up(word)
                db.close()

                if definition:
                    if result: result += '\n'
                    result += "<b>[%s]</b>\n<quote>%s</quote>\n" % (title, definition)

        return result

    def show_config_dialog(self, parent):
        """  """
        dialog = DialogConfig(parent)
        dialog.run()
        dialog.destroy()
