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

from kabukiman.core.config_client import get_config_client

__all__ = ["set_max_words_history", "set_statusbar_active", "set_sidebar_active",
           "set_show_win_startup", "set_shortcut", "set_module_enabled",
           "set_save_history", "get_max_words_history", "get_statusbar_active",
           "get_sidebar_active", "get_show_win_startup", "get_shortcut", 
           "get_save_history", "get_module_enabled"]

_CONFIG_CLIENT = get_config_client()

# Setters
#
def set_max_words_history(value):
    assert isinstance(value, int)
    _CONFIG_CLIENT.set_int("max_words_history", value)

def set_statusbar_active(value):
    assert isinstance(value, bool)
    _CONFIG_CLIENT.set_bool("statusbar", value)

def set_sidebar_active(value):
    assert isinstance(value, bool)
    _CONFIG_CLIENT.set_bool("sidebar", value)

def set_show_win_startup(value):
    assert isinstance(value, bool)
    _CONFIG_CLIENT.set_bool("show_win_startup", value)

def set_shortcut(conf_key, key, mask):
    assert isinstance(key, int)
    assert isinstance(mask, int)
    _CONFIG_CLIENT.set_int_list("shortcuts/%s" % conf_key, (key, mask))

def set_module_enabled(module, value):
    assert isinstance(module, str)
    assert isinstance(value, bool)
    _CONFIG_CLIENT.set_bool("modules/%s" % module, value)

def set_save_history(value):
    assert isinstance(value, bool)
    _CONFIG_CLIENT.set_bool("save_history", value)

# Getters
#
def get_max_words_history():
    if _CONFIG_CLIENT.key_exists("max_words_history"):
        return _CONFIG_CLIENT.get_int("max_words_history")
    return 10

def get_statusbar_active():
    if _CONFIG_CLIENT.key_exists("statusbar"):
        return _CONFIG_CLIENT.get_bool("statusbar")
    return True

def get_sidebar_active():
    if _CONFIG_CLIENT.key_exists("sidebar"):
        return _CONFIG_CLIENT.get_bool("sidebar")
    return True

def get_show_win_startup():
    if _CONFIG_CLIENT.key_exists("show_win_startup"):
        return _CONFIG_CLIENT.get_bool("show_win_startup")
    return False

def get_shortcut(conf_key):
    return _CONFIG_CLIENT.get_int_list("shortcuts/%s" % conf_key)

def get_module_enabled(module):
    if _CONFIG_CLIENT.key_exists("modules/%s" % module):
        return _CONFIG_CLIENT.get_bool("modules/%s" % module)
    return True

def get_save_history():
    if _CONFIG_CLIENT.key_exists("save_history"):
        return _CONFIG_CLIENT.get_bool("save_history")
    return True
