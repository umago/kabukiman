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

import sys
import os
import glob
import traceback

from ConfigParser import ConfigParser

from kabukiman.config import *
from kabukiman.preferences import *
from kabukiman.module import Module

class ModuleManager:
    config = ConfigParser()
    _instances = {}

    def __init__(self, paths):
        """Constructor

        @param paths: A list of paths to the modules folders

        """
        modules = list()
        for path in paths:
            print path
            if path[-1] != os.sep:
                path += os.sep
            if not path in sys.path:
                sys.path.insert(0, path)
            modules += glob.glob(path + "*.kabukiman")

        self.load_modules(modules)

    def load_modules(self, modules):
        """Load all modules

        @param modules: A list of .kabukiman files

        """
        for m in modules:
            module = ''
            name = ''
            author = ''
            version = ''
            website = ''
            description = ''
            module_path = ''
            self.config.read(m)

            # The Core section is required
            if self.config.has_option("Core", "Module") and \
               self.config.has_option("Core", "Name"):
                module = self.config.get("Core", "Module")
                name = self.config.get("Core", "Name")
            else:
                # TODO: Imprimir uma mensagem de erro
                continue

            # Load the information section
            if self.config.has_option("Information", "Author"):
                author = self.config.get("Information", "Author")
            if self.config.has_option("Information", "Version"):
                version = self.config.get("Information", "Version")
            if self.config.has_option("Information", "Website"):
                website = self.config.get("Information", "Website")
            if self.config.has_option("Information", "Description"):
                description = self.config.get("Information", "Description")

            module_path = os.sep.join((os.path.dirname(m), module))

            try:
                module_tmp = __import__("kabukiman.modules."+module, None, None, [], -1)
                module_obj = sys.modules["kabukiman.modules."+module]
                instance = getattr(module_obj, module)()
                assert isinstance(instance, Module)
                instance._load_informations(module, name, module_path, author,\
                                            version, website, description)
                self._instances[module] = instance
            except (AttributeError, ImportError, TypeError):
                print >> sys.stderr, traceback.format_exc()
                continue
            except AssertionError:
                print >> sys.stderr, traceback.format_exc()
                continue

    def get_modules(self):
        """Return a list with instances of the modules"""
        return self._instances.values()

    def get_enabled_modules(self):
        """Return a list with instances of enabled modules"""
        l = list()
        for module in self._instances.values():
            enabled = get_module_enabled(module._module)
            if enabled:
                l.append(module)
        return l

    def set_module_enabled(self, module, value):
        """  """
        assert isinstance(value, bool)

        if not module in self._instances.keys():
            return False

        set_module_enabled("%s" % module, value)
        return True

    def module_is_enabled(self, module):
        """Check if the module is enabled"""
        return get_module_enabled("%s" % module)
