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

import pango
import gtk
from HTMLParser import HTMLParser

# Thanks to José Alexandre Nalon
# for the pygtk html render snippet
# http://www.python.org.br/wiki/RenderizadorHtmlPyGtk
class ResultView(gtk.TextView, HTMLParser):
    _formats = {
         'b': {'weight': pango.WEIGHT_BOLD},

         'i': {'style': pango.STYLE_ITALIC},

         'quote': {'left-margin': 20,
                   'right-margin': 20,
                   'pixels-above-lines': 2,
                   'pixels-below-lines': 2,
                   'justification': gtk.JUSTIFY_FILL},

         'header': {'size': 14 * pango.SCALE,
                    'weight': pango.WEIGHT_BOLD,
                    'foreground': "#8b0000"},

         'source': {'scale': pango.SCALE_X_SMALL,
                    'foreground': "gray",
                    'justification': gtk.JUSTIFY_CENTER}
    }

    def __init__(self):
        gtk.TextView.__init__(self)
        HTMLParser.__init__(self)

        self.set_editable(False)
        self.set_cursor_visible(False)
        self.buffer = self.get_buffer()
        self.set_wrap_mode(gtk.WRAP_WORD)
        self.set_left_margin(5)
        self._tags = {}
        self._marks = list()
        self.show_all()

        for tag in self._formats:
            self.buffer.create_tag(tag, **self._formats[tag])

    def handle_starttag(self, tag, attr):
        """Handles the opening tags. When a tag is opened the
        position is registered so the formatting is applied
        later, at closing
        
        """ 
        iter = self.buffer.get_end_iter()
        mark = self.buffer.create_mark(None, iter, True)
        if tag in self._tags:
            self._tags[tag].append(mark)
        else:
            self._tags[tag] = [mark]


    def handle_data(self, data):
        """Receives the tag content and inserts in the result area"""
        iter = self.buffer.get_end_iter()
        self.buffer.insert(iter, data)

    def handle_endtag(self, tag):
        """Close the tag. Finds the final position of a tag, get
        the tag content and then apply the formatting to that content

        """
        # Ignore tags that dont exists
        if tag not in self._formats.keys():
            return

        try:
            start_mark = self._tags[tag].pop()
            start = self.buffer.get_iter_at_mark(start_mark)
            iter = self.buffer.get_end_iter()
            self.buffer.apply_tag_by_name(tag, start, iter)
            return
        except KeyError:
            pass
    
    def copy(self):
        """Copy the selected text to the clipboard"""
        clipboard = gtk.Clipboard()
        buffer = self.get_buffer()
        buffer.copy_clipboard(clipboard)

    def select_all(self):
        """Select all the text"""
        buffer = self.get_buffer()
        start, end = buffer.get_bounds()
        buffer.select_range(end, start)

    def scroll_to_result(self, mark):
        """  """
        if mark in self._marks:
            self.scroll_to_mark(mark, 0, True, 0, 0)

    def insert_header(self, header):
        """  """
        header = header.lower()
        iter = self.buffer.get_end_iter()
        self.buffer.insert_with_tags_by_name(iter, header + "\n\n", "header")

    def insert_result(self, result):
        """  """
        result = result.lower()
        iter = self.buffer.get_end_iter()
        mark = self.buffer.create_mark(None, iter, True)
        self._marks.append(mark)
        self.feed(result)
        return mark

    def insert_source(self, source):
        """  """
        iter = self.buffer.get_end_iter()
        self.buffer.insert_with_tags_by_name(iter, "\n\n" + source + "\n\n", "source")
    
    def clear(self):
        """Clears the result area"""
        self.buffer.set_text('')
        for m in self._marks:
            self.buffer.delete_mark(m)
            self._marks.remove(m)
