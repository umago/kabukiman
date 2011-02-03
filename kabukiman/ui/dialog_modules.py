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
import traceback

from kabukiman.config import *
from kabukiman.core.module_manager import ModuleManager

class DialogModules(gtk.Dialog):
    """A dialog to configure the modules"""

    def __init__(self, parent=None):
        gtk.Dialog.__init__(self, parent=parent)

        self.module_manager = ModuleManager(MODULES_DIRS)

        # Module treeview widgets
        self.add_button(gtk.STOCK_CLOSE, 0)
        self.set_size_request(350, 400)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_title(_("Modules"))

        self.liststore = gtk.ListStore(bool, str, object)
        self.treeview = gtk.TreeView()
        self.treeview.set_rules_hint(True)

        toggle_cell = gtk.CellRendererToggle()
        toggle_cell.set_property("activatable", True)
        toggle_cell.connect("toggled", self.module_enable_toggled)
        column_check = gtk.TreeViewColumn(_("Enabled"), toggle_cell)
        column_check.set_sort_column_id(0)
        column_check.add_attribute(toggle_cell, "active", 0)
        self.treeview.append_column(column_check)

        render_name = gtk.CellRendererText()
        column_name = gtk.TreeViewColumn(_("Name"), render_name, markup=1)
        column_name.set_sort_column_id(1)
        self.treeview.append_column(column_name)
        self.treeview.set_model(self.liststore)

        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow.set_shadow_type(gtk.SHADOW_IN)
        scrolledwindow.add(self.treeview)

        # Module information widgets
        table = gtk.Table(4, 2, False)
        table.set_col_spacings(10)

        self.label_module = gtk.Label()
        self.label_module.set_alignment(0, 0.50)
        self.label_module.set_padding(0, 10)
        table.attach(self.label_module, 0, 2, 0, 1, xoptions=gtk.FILL, yoptions=gtk.FILL)

        label = gtk.Label(_("<b>Author:</b>"))
        label.set_use_markup(True)
        label.set_alignment(0, 0.50)
        table.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=gtk.FILL)
        self.label_author = gtk.Label()
        self.label_author.set_alignment(0, 0.50)
        table.attach(self.label_author, 1, 2, 1, 2)

        label = gtk.Label(_("<b>Version:</b>"))
        label.set_use_markup(True)
        label.set_alignment(0, 0.50)
        table.attach(label, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=gtk.FILL)
        self.label_version = gtk.Label()
        self.label_version.set_alignment(0, 0.50)
        table.attach(self.label_version, 1, 2, 2, 3)

        label = gtk.Label(_("<b>Website:</b>"))
        label.set_use_markup(True)
        label.set_alignment(0, 0.50)
        table.attach(label, 0, 1, 3, 4, xoptions=gtk.FILL, yoptions=gtk.FILL)
        self.label_website = gtk.Label()
        self.label_website.set_alignment(0, 0.50)
        self.label_website.set_selectable(True)
        table.attach(self.label_website, 1, 2, 3, 4)

        alignment = gtk.Alignment()
        alignment.set_padding(0, 5, 5, 5)
        alignment.add(table)

        self.expander = gtk.Expander()
        self.expander.set_use_markup(True)
        self.expander.set_label(_("<b>Module Information</b>"))
        self.expander.set_sensitive(False)
        self.expander.add(alignment)

        self.button_configure = gtk.Button()
        self.button_configure.connect("clicked", self.show_module_config)
        self.button_configure.set_use_underline(True)
        self.button_configure.set_label(_("Configure _Module"))
        self.button_configure.set_sensitive(False)

        hbuttonbox = gtk.HButtonBox()
        hbuttonbox.set_layout(gtk.BUTTONBOX_START)
        hbuttonbox.set_border_width(5)
        hbuttonbox.add(self.button_configure)

        self.vbox.pack_start(scrolledwindow, True)
        self.vbox.pack_start(self.expander, False)
        self.vbox.pack_start(hbuttonbox, False)
        self.vbox.show_all()

        # Cursor changed cause we want a 1 click treeview, activate method
        # requires two clicks
        self.treeview.connect("cursor-changed", self.select_module)
        self.refresh()

    def refresh(self):
        """Refresh the treeview modules"""
        pattern = "<b>%s</b> %s\n%s"
        modules = self.module_manager.get_modules()

        self.liststore.clear()
        for module in modules:
            string = pattern % (module._name, module._version, module._description)
            enabled = self.module_manager.module_is_enabled(module._module)
            self.liststore.append((enabled, string, module))

    def module_enable_toggled(self, widget, path):
        """Enable and Disable a module"""
        model = self.treeview.get_model()
        giter = model.get_iter(path)
        enabled = not model.get_value(giter, 0)
        self.liststore.set_value(giter, 0, enabled)

        # Save status
        module = model.get_value(giter, 2)
        self.module_manager.set_module_enabled(module._module, enabled)

    def select_module(self, widget):
        """ """
        selection = self.treeview.get_selection()
        (model, giter) = selection.get_selected()
        try:
            instance = model.get_value(giter, 2)
        except TypeError:
            return False

        self.expander.set_sensitive(True)
        self.label_module.set_markup("<b><big>%s</big></b>" % (instance._name))
        self.label_author.set_text(instance._author)
        self.label_version.set_text(instance._version)
        self.label_website.set_text(instance._website)
        
        if instance.is_configurable():
            self.button_configure.set_sensitive(True)
        else:
            self.button_configure.set_sensitive(False)

    def show_module_config(self, widget):
        """Show the configuration dialog of a module (if exists)"""
        selection = self.treeview.get_selection()
        (model, giter) = selection.get_selected()
        try:
            instance = model.get_value(giter, 2)
        except TypeError:
            return False

        try:
            instance.show_config_dialog(parent=self)
        except Exception, e:
            print >> sys.stderr, traceback.format_exc() 
