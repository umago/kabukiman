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

import gtk
import os
import cPickle
import errno
import gobject

from threading import Thread

from kabukiman.utils import *
from babylon import *
from dialog_progress import DialogProgress

class BglTreeview(gtk.TreeView):
    def __init__(self, config_path):
        gtk.TreeView.__init__(self)
        self.conf = os.path.join(config_path, "babylon.cfg")
        self.model = gtk.ListStore(str, str)
        rtext = gtk.CellRendererText()
        self.column = gtk.TreeViewColumn("Dictionaries", rtext, text=0)
        self.append_column(self.column)
        self.set_model(self.model)

        self.load_conf()

    def load_conf(self):
        if not os.path.exists(self.conf):
            return False

        f = open(self.conf, 'rb')
        l = cPickle.load(f)
        f.close()

        for title, path in l:
            self.add_dictionary(title, path)

    def save_conf(self):
        l = self.get_dictionary_list()
        f = open(self.conf, 'wb')
        cPickle.dump(l, f)
        f.close()

    def add_dictionary(self, title, path):
        """  """
        self.model.append([title, path])
        self.save_conf()

    def get_dictionary_list(self):
        """  """
        dictionary_list = list()
        model = self.get_model()
        iter = model.get_iter_first()
        while iter != None:
            dic = model.get_value(iter, 0)
            path = model.get_value(iter, 1)
            dictionary_list.append((dic, path))
            iter = model.iter_next(iter)
        return dictionary_list

    def delete_line(self):
        path = self.get_cursor()[0]
        selection = self.get_selection()
        (model, iter) = selection.get_selected()
        file_path = model.get_value(iter, 1)

        try:
            os.remove(file_path)
        except OSError, e:
            if e.errno == errno.ENOENT: # No such file or directory
                pass
            elif e.errno == errno.EACCES:
                self.error("Permission denied")
                return False
        try:
            model.remove(iter)
            path = path[0]
            if path != 0:
                path -= 1
            self.set_cursor(path)
        except TypeError, e:
            return -1

        self.save_conf()

class DialogConfig(gtk.Dialog):
    def __init__(self, parent=None):
        gtk.Dialog.__init__(self, parent=parent)

        self.add_button(gtk.STOCK_CLOSE, 0)
        self.set_size_request(300, 300)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_title("Babylon")

        self.config_path = os.sep.join((get_home_dir(), ".kabukiman", "babylon"))

        #FileChooser
        filechooser = gtk.FileChooserButton("Choose Babylon(.bgl) File")
        filechooser.connect("file-set", self.file_selected)
        filechooser.set_current_folder(get_home_dir())

        # Treeview
        self.treeview = BglTreeview(self.config_path)
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow.set_shadow_type(gtk.SHADOW_IN)
        scrolledwindow.add(self.treeview)

        remove_button = gtk.Button()
        remove_image = gtk.Image()
        remove_image.set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_BUTTON)
        remove_button.set_image(remove_image)
        remove_button.connect("clicked", self.delete_dictionary)

        hbuttonbox = gtk.HButtonBox()
        hbuttonbox.set_layout(gtk.BUTTONBOX_CENTER)
        hbuttonbox.add(remove_button)

        # Pack all
        self.vbox.set_spacing(5)
        self.vbox.pack_start(filechooser, False)
        self.vbox.pack_start(scrolledwindow, True)
        self.vbox.pack_start(hbuttonbox, False)
        self.vbox.show_all()

    def delete_dictionary(self, widget):
        self.treeview.delete_line()

    def file_selected(self, widget):
        """  """
        self.parsing_error = 0
        file_path = widget.get_filename()

        d = DialogProgress(parent=self)
        t = Thread(target=self._parse_dictionary, args=(file_path, d.destroy,))
        t.start()
        d.run()

        if self.parsing_error == 1:
            self.error("Its not a BGL file")
        elif self.parsing_error == 2:
            self.error("Cannt create the configuration dir")

        widget.set_current_folder(get_home_dir())

    def _parse_dictionary(self, file_path, finish_callback):
        """  """
        try:
            bp = BabylonParser(file_path)
        except NotBglFile:
            self.parsing_error = 1
            gobject.idle_add(finish_callback)
            return True

        if not os.path.exists(self.config_path):
            try:
                os.mkdir(self.config_path)
            except OSError:
                self.parsing_error = 2
                gobject.idle_add(finish_callback)
                return True

        title = bp.title
        dest_file = os.path.join(self.config_path, title)
        bp.save_to_file(dest_file)
        gobject.idle_add(self.treeview.add_dictionary, title, dest_file)

        gobject.idle_add(finish_callback)
        return True

    def error(self, msg):
        md = gtk.MessageDialog(self, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, 
            gtk.BUTTONS_CLOSE, msg)
        md.run()
        md.destroy()
