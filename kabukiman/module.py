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

class Module(object):
    """The base class of all modules"""
    
    def _load_informations(self, module, name, module_path, author='', \
                        version='', website='', description=''):
        self._name = name
        self._module = module
        self._author = author
        self._version = version
        self._website = website
        self._description = description
        self.my_path = module_path

    def is_configurable(self):
        # To be overrided
        return False

    def look_up(self, word):
        # To be overrided
        return ''

    def show_config_dialog(self, parent):
        # To be overrided
        pass
