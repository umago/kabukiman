#!/usr/bin/python
# coding: utf-8
# Copyright (C) 2011 Lucas Alvares Gomes <lucasagomes@gmail.com>
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

import shelve

class DataBase:

    def __init__(self):
        self.opened = False

    def open(self, path):
        """ """
        if not self.opened:
            self.fd = shelve.open(path)
        self.opened = True

    def add_word(self, word, definition):
        """  """
        if not self.opened: return False
        word = word.lower()
        self.fd[word] = definition
        return True

    def close(self):
        """  """
        if not self.opened: return False
        self.fd.close()
        return True

    def look_up(self, word):
        """  """
        if self.fd.has_key(word):
            return self.fd[word]
        return ''

