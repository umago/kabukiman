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


import gtk

class TreeviewResults(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)
        self.liststore = gtk.ListStore(str, object)
        self.set_headers_visible(False)

        render_name = gtk.CellRendererText()
        column_name = gtk.TreeViewColumn(_("Name"), render_name, text=0)
        self.append_column(column_name)
        self.set_model(self.liststore)

        self.show_all()

    def add_result(self, name, mark):
        """  """
        self.liststore.append((name, mark))

    def clear(self):
        """  """
        self.liststore.clear()
