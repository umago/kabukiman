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

import os
import ConfigParser

from kabukiman.config import *

try:
    import gconf
    HAS_GCONF = True
except ImportError:
    HAS_GCONF = False

def get_config_client():
    """  """
    if HAS_GCONF:
        config_client = GConfClient()
    else:
        config_client = ConfClient()
    return config_client

class GConfClient:
    def __init__(self):
        self.client = gconf.client_get_default()
        if not self.client.dir_exists("/apps/kabukiman"):
            self.client.add_dir("/apps/kabukiman", gconf.CLIENT_PRELOAD_NONE)

        if not self.client.dir_exists("/apps/kabukiman/shortcuts"):
            self.client.add_dir("/apps/kabukiman/shortcuts", gconf.CLIENT_PRELOAD_NONE)

        if not self.client.dir_exists("/apps/kabukiman/modules"):
            self.client.add_dir("/apps/kabukiman/modules", gconf.CLIENT_PRELOAD_NONE)


    def parse_key(self, key):
        path = "/apps/kabukiman/%s" % key
        return path

    def key_exists(self, key):
        k = self.parse_key(key)
        out = self.client.get(k)
        if out:
            return True
        return False

    # Setters
    #
    def set_string(self, key, value):
        k = self.parse_key(key)
        self.client.set_string(k, value)

    def set_bool(self, key, value):
        k = self.parse_key(key)
        self.client.set_bool(k, value)

    def set_int(self, key, value):
        k = self.parse_key(key)
        self.client.set_int(k, value)

    def set_int_list(self, key, value):
        k = self.parse_key(key)
        self.client.set_list(k, gconf.VALUE_INT, value)

    # Getters
    #
    def get_string(self, key):
        k = self.parse_key(key)
        return self.client.get_string(k)

    def get_bool(self, key):
        k = self.parse_key(key)
        return self.client.get_bool(k)

    def get_int(self, key):
        k = self.parse_key(key)
        return self.client.get_int(k)

    def get_int_list(self, key):
        k = self.parse_key(key)
        return self.client.get_list(k, gconf.VALUE_INT)

class ConfClient:
    def __init__(self):
        self.client = ConfigParser.ConfigParser()
        self.config_file = os.sep.join((CONFIGDIR, "kabukiman.conf"))

        if not os.path.exists(self.config_file):
            self.client.add_section("Kabukiman")
        
        self.client.read(self.config_file)

    def setter(self, key, value):
        value = repr(value)
        self.client.set("Kabukiman", key, value)
        with open(self.config_file, 'w') as cf:
            self.client.write(cf)

    def getter(self, key):
        try:
            value = eval(self.client.get("Kabukiman", key))
        except ConfigParser.NoOptionError:
            value = None
        return value

    def key_exists(self, key):
        return self.client.has_option("Kabukiman", key)

    # Setters
    #
    def set_string(self, key, value):
        self.setter(key, value)

    def set_bool(self, key, value):
        self.setter(key, value)
        
    def set_int(self, key, value):
        self.setter(key, value)

    def set_int_list(self, key, value):
        self.setter(key, value)

    # Getters
    #
    def get_string(self, key):
        value = self.getter(key)
        if value is None:
            value = ''
        return value

    def get_bool(self, key):
        value = self.getter(key)
        if value is None:
            value = False
        return value

    def get_int(self, key):
        value = self.getter(key)
        if value is None:
            value = 0
        return value

    def get_int_list(self, key):
        value = self.getter(key)
        if value is None:
            value = []
        return value
