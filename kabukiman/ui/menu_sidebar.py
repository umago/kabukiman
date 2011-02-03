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

class MenuSidebar(gtk.Menu):
    def __init__(self):
        gtk.Menu.__init__(self)

        self.menu_results = gtk.MenuItem(_("Results"))
        #self.menu_search_in = gtk.MenuItem(_("Search In"))

        self.append(self.menu_results)
        #self.append(self.menu_search_in)
