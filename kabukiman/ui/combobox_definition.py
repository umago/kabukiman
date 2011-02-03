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
import os
import sys
from xml.dom.minidom import Document, parse

from kabukiman.config import *
from kabukiman.preferences import *

class ComboBoxDefinition(gtk.ComboBoxEntry):
    def __init__(self):
        gtk.ComboBoxEntry.__init__(self)
        self.history = gtk.ListStore(str)
        self.completion = gtk.EntryCompletion()
        self.completion.set_text_column(0)
        self.set_text_column(0)
        self.connect("changed", self.on_changed)

        self._history_file = os.sep.join((CONFIGDIR, "history.xml"))

        self.show()

    def add_to_list(self, word):
        """Add the word to the history and completion lists"""
        if not self.check_redundancy(word):
            self.history.prepend([word])
            self.set_model(self.history)
            self.completion.set_model(self.history)
            self.child.set_completion(self.completion)
            self.check_max()

    def get_history(self):
        """ """
        history_list = list()
        giter = self.history.get_iter_first()
        while giter:
            history_list.append(self.history.get_value(giter, 0))
            giter = self.history.iter_next(giter)
        return history_list

    def load_history(self):
        """  """
        if os.path.exists(self._history_file):
            try:
                parser = parse(self._history_file)
            except IOError:
                print >> sys.stderr, "Error parsing the history file"
                return
            except ExpatError:
                print >> sys.stderr, "The history file is not well-formed"
                return

            words = parser.getElementsByTagName("word")
            for w in reversed(words):
                if w.hasChildNodes():
                    word = w.firstChild.data
                    self.add_to_list(word)
                

    def save_history(self):
        """Save the current history to a file"""
        words = self.get_history()
        doc = Document()
        history = doc.createElement("history")
        for w in words:
            word = doc.createElement("word")
            text = doc.createTextNode(w)
            word.appendChild(text)
            history.appendChild(word)
        doc.appendChild(history)
        xml = doc.toxml("utf-8")

        with open(self._history_file, 'w') as f:
            f.write(xml)

    def check_redundancy(self, word):
        """  """
        giter = self.history.get_iter_first()
        while giter:
            if word == self.history.get_value(giter, 0):
                return True
            giter = self.history.iter_next(giter)
        return False

    def on_changed(self, widget):
        """  """
        if self.child_focus(1):
            self.child.grab_focus()

    def check_max(self):
        """  """
        count = 0
        giter = self.history.get_iter_first()
        while giter:
            if count >= get_max_words_history():
                to_rm = giter
                giter = self.history.iter_next(giter)
                self.history.remove(to_rm)
                continue
            giter = self.history.iter_next(giter)
            count += 1
        return False
