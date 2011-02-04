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

import gtk
import os

from operator import itemgetter
from ConfigParser import ConfigParser

from global_ import *

from kabukiman.utils import *

class TreeviewLanguages(gtk.TreeView):
    def __init__(self, config_path):
        gtk.TreeView.__init__(self)

        self.config = ConfigParser()
        self.config_path = config_path

        self.model_from_lang = gtk.ListStore(str, str)
        self.model_to_lang = gtk.ListStore(str, str)

        # Sort the LANGUAGUES by the value
        languages = sorted(LANGUAGES.items(), key=itemgetter(1))

        # The * means that google will try to guess the source language
        self.model_from_lang.append(['*', ''])
        for code, name in languages:
            self.model_from_lang.append([name, code])

        for code, name in languages:
            self.model_to_lang.append([name, code])

        render_from_lang = gtk.CellRendererCombo()
        render_from_lang.set_property("text-column", 0)
        render_from_lang.set_property("editable", True)
        render_from_lang.set_property("has-entry", False)
        render_from_lang.set_property("model", self.model_from_lang)
        render_from_lang.connect("changed", self.set_from_language)

        render_to_lang = gtk.CellRendererCombo()
        render_to_lang.set_property("text-column", 0)
        render_to_lang.set_property("editable", True)
        render_to_lang.set_property("has-entry", False)
        render_to_lang.set_property("model", self.model_to_lang)
        render_to_lang.connect("changed", self.set_to_language)

        column_from_lang = gtk.TreeViewColumn(_("From language"), render_from_lang, text=0)
        column_from_lang.set_expand(True)
        column_to_lang = gtk.TreeViewColumn(_("To language"), render_to_lang, text=1)
        column_to_lang.set_expand(True)
        self.append_column(column_from_lang)
        self.append_column(column_to_lang)

        self.treeview_model = gtk.ListStore(str, str, str, str)
        self.set_model(self.treeview_model)

        self._load_config()

    def _load_config(self):
        # Fill the treeview with old configs (if its exists)
        self.config.read(self.config_path)
        if self.config.has_option("GoogleTranslate", "languages"):
            languages = self.config.get("GoogleTranslate", "languages")
            try:
                languages = eval(languages)
            except Exception, e:
                # TODO: Message
                return
            for from_lang_code, to_lang_code in languages:
                if not from_lang_code:
                    from_lang = "*"
                else:
                    from_lang = LANGUAGES[from_lang_code]
                
                to_lang = LANGUAGES[to_lang_code]

                model = self.get_model()
                model.append([from_lang, to_lang, from_lang_code, to_lang_code])

    def set_from_language(self, combo, path, new_iter):
        """  """
        language = self.model_from_lang.get_value(new_iter, 0)
        language_code = self.model_from_lang.get_value(new_iter, 1)

        treeviewmodel = self.get_model()
        giter = treeviewmodel.get_iter(path)
        treeviewmodel.set_value(giter, 0, language)
        treeviewmodel.set_value(giter, 2, language_code)
        
        self.save_config() # Save changes

    def set_to_language(self, combo, path, new_iter):
        """  """
        language = self.model_to_lang.get_value(new_iter, 0)
        language_code = self.model_to_lang.get_value(new_iter, 1)

        treeviewmodel = self.get_model()
        giter = treeviewmodel.get_iter(path)
        treeviewmodel.set_value(giter, 1, language)
        treeviewmodel.set_value(giter, 3, language_code)
        
        self.save_config() # Save changes

    def delete_line(self, widget):
        """ Delete the selected row """
        path = self.get_cursor()[0]
        selection = self.get_selection()
        (model, iter) = selection.get_selected()
        try:
            model.remove(iter)
            path = path[0]
            if path != 0:
                path -= 1
            self.set_cursor(path)
        except TypeError, e:
            return -1

        self.save_config() # Save changes

    def new_line(self, widget):
        """ Insert a row in the current treeview and select it"""
        language_name = LANGUAGES["en"]
        model = self.get_model()
        model.append(["*", language_name, '', "en"])
        self.grab_focus()
        path = self.get_cursor()[0]
        path = path[0]
        columns = self.get_columns()
        model = self.get_model()
        iter = model.iter_next(model.get_iter(path))
        while iter != None:
            iter = model.iter_next(model.get_iter(path))
            path += 1

        if path >= 1:
            iter = model.iter_next(model.get_iter(path-2))
        else:
            iter = model.get_iter_first()

        path = model.get_path(iter)
        next_column = columns[0]
        self.set_cursor(path, next_column, False)

        self.save_config() # Save changes

    def get_languages_list(self):
        """  """
        languages_list = list()
        model = self.get_model()
        iter = model.get_iter_first()
        while iter != None:
            from_lang_code = model.get_value(iter, 2)
            to_lang_code = model.get_value(iter, 3)
            languages_list.append((from_lang_code, to_lang_code))
            iter = model.iter_next(iter)
        return languages_list

    def save_config(self):
        """  """
        if not self.config.has_section("GoogleTranslate"):
            self.config.add_section("GoogleTranslate")

        languages = repr(self.get_languages_list())
        self.config.set("GoogleTranslate", "languages", languages)

        with open(self.config_path, 'wb') as configfile:
            self.config.write(configfile)

class DialogConfig(gtk.Dialog):
    def __init__(self, parent=None):
        gtk.Dialog.__init__(self, parent=parent)

        self.add_button(gtk.STOCK_CLOSE, 0)
        self.set_size_request(300, 300)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_title("Google Translate")

        # Treeview
        config_path = os.sep.join((get_home_dir(), ".kabukiman", "googletranslate.cfg"))
        self.treeview = TreeviewLanguages(config_path)
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow.set_shadow_type(gtk.SHADOW_IN)
        scrolledwindow.add(self.treeview)

        # Add and Remove buttons
        add_button = gtk.Button()
        add_image = gtk.Image()
        add_image.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON)
        add_button.set_image(add_image)
        add_button.connect("clicked", self.treeview.new_line)

        remove_button = gtk.Button()
        remove_image = gtk.Image()
        remove_image.set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_BUTTON)
        remove_button.set_image(remove_image)
        remove_button.connect("clicked", self.treeview.delete_line)

        hbuttonbox = gtk.HButtonBox()
        hbuttonbox.set_layout(gtk.BUTTONBOX_CENTER)
        hbuttonbox.add(add_button)
        hbuttonbox.add(remove_button)

        # Pack all
        self.vbox.set_spacing(5)
        self.vbox.pack_start(scrolledwindow, True)
        self.vbox.pack_start(hbuttonbox, False)
        self.vbox.show_all()
