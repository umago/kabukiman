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
import sys

try:
    from Xlib.display import Display
    from Xlib import X, protocol
    import Xlib.Xatom
except ImportError:
    print >> sys.stderr, _("Xlib packaged not found")
    sys.exit(1)

from threading import Thread

from kabukiman.core.shortcut_manager import ShortcutManager

def get_primary_selection():
    """Get the word selected in the primary selection."""
    display = Display()
    xsel_data_atom = display.intern_atom("XSEL_DATA")
    UTF8_STRING = display.intern_atom("UTF8_STRING")
    screen = display.screen()
    w = screen.root.create_window(0, 0, 2, 2, 0, screen.root_depth)
    w.convert_selection(Xlib.Xatom.PRIMARY,  # selection
                        UTF8_STRING,         # target
                        xsel_data_atom,      # property
                        Xlib.X.CurrentTime)  # time

    while True:
        e = display.next_event()
        if e.type == X.SelectionNotify:
            break

    if e.property != xsel_data_atom or \
       e.target != UTF8_STRING:
        return ''

    reply = w.get_full_property(xsel_data_atom, X.AnyPropertyType)
    reply = reply.value.strip()
    return reply

class X11(ShortcutManager, Thread):
    def __init__(self):
        ShortcutManager.__init__(self)
        Thread.__init__(self)
        self.setDaemon(True)

        self.display = Display ()
        self.screen = self.display.screen ()
        self.root = self.screen.root

        self.root.change_attributes(event_mask=X.KeyPress|X.KeyRelease|X.PropertyChangeMask)

        self.key_conf_to_key = dict()

        self.active = False

    def init(self):
        """Start the main loop."""
        self.active = True
        self.start()

    def run(self):
        """Main loop
        
        It will handle the user combination key,
        check if its associated to a pre-configured shortcut
        and then execute the right action to that shortcut.

        """
        while self.active:
            event = self.root.display.next_event()
            if event.type == X.KeyPress:
                for key_conf in self.key_conf_to_key.keys():
                    key, mask = self.key_conf_to_key[key_conf]
                    if event.detail == key and \
                       event.state == mask:
                        if key_conf == "quick_search":
                            gtk.gdk.threads_enter()
                            self.emit("quick_search")
                            gtk.gdk.threads_leave()
                        elif key_conf == "scan_selection":
                            word = get_primary_selection()
                            if word:
                                gtk.gdk.threads_enter()
                                self.emit("scan_selection", word)
                                gtk.gdk.threads_leave()

    def set_shortcut(self, key_conf, key, mask):
        """  """
        key = self.display.keysym_to_keycode(key)
        self.root.grab_key(key, mask, 1, X.GrabModeAsync, X.GrabModeAsync)

        self.key_conf_to_key[key_conf] = (key, mask)

    def unset_shortcut(self, key, mask):
        """ """
        key = self.display.keysym_to_keycode(key)
        self.root.ungrab_key(key, mask)

    def stop(self):
        """Stop the main loop"""
        self.active = False
        self.unset_keys()

    def unset_keys(self):
        """Unset all shortcuts."""
        for key_conf in self.key_conf_to_key.keys():
            key, mask = self.key_conf_to_key[key_conf]
            self.unset_shortcut(key, mask)
