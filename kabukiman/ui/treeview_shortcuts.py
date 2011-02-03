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
import sys

from kabukiman.config import *
from kabukiman.preferences import *
from kabukiman.core.shortcut_manager import get_instance

class KeyEntry(object):
    def __init__(self, keycode, mask):
        assert isinstance(keycode, int)
        assert isinstance(mask, int)

        self.keycode = keycode
        self.mask = mask

class TreeviewShortcuts(gtk.TreeView): 
    def __init__(self, main_window):
        gtk.TreeView.__init__(self)

        # Main window instance
        self.main_window = main_window

        self.connect("row-activated", self.edit_shortcut)

        self.model = gtk.ListStore(str, object, str)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Action", renderer, text=0)
        column.set_property("expand", True)
        self.append_column(column)

        renderer = gtk.CellRendererAccel()
        renderer.set_property("editable", True)
        renderer.connect("accel-edited", self.try_set_shortcut)
        renderer.connect("accel-cleared", self.clean_shortcut)

        column = gtk.TreeViewColumn("Shortcut", renderer)
        column.set_cell_data_func(renderer, self._cell_data_func)
        column.set_property("expand", False)
        self.append_column(column)

        # Shortcut Manager
        self.shortcut_manager = get_instance()

        self._setup()
        self.set_model(self.model)
        self.show_all()

    def _setup(self):
        """  """
        stfs = get_shortcut("scan_selection")
        qs = get_shortcut("quick_search")
        qs_keyentry = KeyEntry(0, 0)
        stfs_keyentry = KeyEntry(0, 0)

        if stfs:
            try:
                key, mask = stfs
                stfs_keyentry = KeyEntry(key, mask)
                self.shortcut_manager.set_shortcut("scan_selection", key, mask)
            except (ValueError, AssertionError):
                stfs_keyentry = KeyEntry(0, 0)
        else:
            # If no there's no value setted then set the default
            stfs_keyentry = KeyEntry(120, 5) # Ctrl + Shift + X
            self.shortcut_manager.set_shortcut("scan_selection", 120, 5)

        if qs:
            try:
                key, mask = qs
                qs_keyentry = KeyEntry(key, mask)
                self.shortcut_manager.set_shortcut("quick_search", key, mask)
            except (ValueError, AssertionError):
                stfs_keyentry = KeyEntry(0, 0)
        else:
            # If no there's no value setted then set the default
            qs_keyentry = KeyEntry(65477, 0) # F8
            self.shortcut_manager.set_shortcut("quick_search", 65477, 0)

        self.model.append((_("Scan selection"), stfs_keyentry, "scan_selection"))
        self.model.append((_("Quick search"), qs_keyentry, "quick_search"))

    def edit_shortcut(self, widget, path, view_column):
        """  """
        columns = self.get_columns()
        self.set_cursor(path, columns[1], True)

    def try_set_shortcut(self, renderer, path, keycode, mask, keyval):
        """  """
        def each_key(model, path, giter):
            """Check redundance"""
            obj = model.get_value(giter, 1)
            if obj.keycode == keycode and obj.mask == mask:
                raise Exception

        def check_modifier(mod):
            """Dont allow weird modifiers"""
            _unallowed_modifier = ('Super', 'Hyper', 'Meta')
            if mod:
                labels = gtk.accelerator_get_label(0, mod)
                mod_list = labels.replace('+', ' ').split()
                for m in mod_list:
                    if m in _unallowed_modifier:
                        return False
            return True

        if not check_modifier(mask.real):
            print >> sys.stderr, "Unallowed modifier"
            return False

        try:
            self.model.foreach(each_key)
        except:
            return False

        keycode = int(keycode)
        giter = self.model.get_iter(path)

        conf_key = self.model.get_value(giter, 2)

        # Unset the old shortcut
        old = self.model.get_value(giter, 1)
        if old.keycode != 0:
            self.shortcut_manager.unset_shortcut(old.keycode, old.mask)

        # Set the new shortcut
        self.shortcut_manager.set_shortcut(conf_key, keycode, mask.real)

        #Save preferences
        set_shortcut(conf_key, keycode, mask.real)

        self.model.set_value(giter, 1, KeyEntry(keycode, mask.real))

    def clean_shortcut(self, renderer, path):
        """  """
        giter = self.model.get_iter(path)

        # Unset the old shortcut
        old = self.model.get_value(giter, 1)
        if old.keycode != 0:
            self.shortcut_manager.unset_shortcut(old.keycode, old.mask)

        #Save preferences
        conf_key = self.model.get_value(giter, 2)
        set_shortcut(conf_key, 0, 0)

        self.model.set_value(giter, 1, KeyEntry(0, 0))

    def _cell_data_func(self, column, renderer, model, giter):
        obj = model.get_value(giter, 1)
        renderer.set_property("accel-key", obj.keycode)
        renderer.set_property("accel-mods", obj.mask)
