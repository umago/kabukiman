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

import sys
import gobject

__all__ = ["ShortcutManager", "get_instance"]

# Make a method to check the display server
# wayland is coming :) hurray o/!
DISPLAY_SERVER = "X11"

class ShortcutManager(gobject.GObject):
    """The base class of all shortcut managers"""
    __gsignals__ = {
        "quick_search": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "scan_selection": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          (gobject.TYPE_GSTRING,)),
        }
    def __init__(self):
        self.__gobject_init__()

    def set_shortcut(self, key_conf, key, mask):
        pass

    def unset_shortcut(self, key, mask):
        pass

    def stop(self):
        pass

# Register signals
gobject.type_register(ShortcutManager)

def _get_shortcut_manager():
    """Check the plataform and instantiates the correct shortcut manager"""
    global DISPLAY_SERVER
    if DISPLAY_SERVER == "X11":
        from kabukiman.core.shortcut.x11 import X11
        manager = X11()
    else:
        manager = ShortcutManager()
    return manager

def _singleton(value):
    """A decorator to handle an instance"""
    def decorate(func):
        setattr(func, "manager", value)
        return func
    return decorate

@_singleton(_get_shortcut_manager())
def get_instance():
    """Return the shortcut manager instance (singleton)"""
    return get_instance.manager
