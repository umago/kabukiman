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

# A Very special thanks to dictconv application
# http://sourceforge.net/projects/ktranslator/files/dictconv/0.2/

__all__ = ["BabylonParser", "NotBglFile"]

import sys
import os
import gzip
from StringIO import StringIO

from db import DataBase

charsets = (
	"ISO-8859-1", # Default
	"ISO-8859-1", # Latin
	"ISO-8859-2", # Eastern European
	"ISO-8859-5", # Cyriilic
	"ISO-8859-14", # Japanese
	"ISO-8859-14", # Traditional Chinese
	"ISO-8859-15", # Simplified Chinese
	"CP1257", # Baltic
	"CP1253", # Greek
	"ISO-8859-15",  # Korean
	"ISO-8859-9", # Turkish
	"ISO-8859-9", # Hebrew
	"CP1256", # Arabic
	"CP874"  # Thai
        )

languages = (
	"English", 
	"French",
	"Italian",
	"Spanish",
	"Dutch",
	"Portuguese",
	"German",
	"Russian",
	"Japanese",
	"Traditional Chinese",
	"Simplified Chinese",
	"Greek",
	"Korean",
	"Turkish",
	"Hebrew",
	"Arabic",
	"Thai",
	"Other",
	"Other Simplified Chinese dialects",
	"Other Traditional Chinese dialects",
	"Other Eastern-European languages",
	"Other Western-European languages",
	"Other Russian languages",
	"Other Japanese languages",
	"Other Baltic languages",
	"Other Greek languages",
	"Other Korean dialects",
	"Other Turkish dialects",
	"Other Thai dialects",
	"Polish",
	"Hungarian",
	"Czech",
	"Lithuanian",
	"Latvian",
	"Catalan",
	"Croatian",
	"Serbian",
	"Slovak",
	"Albanian",
	"Urdu",
	"Slovenian",
	"Estonian",
	"Bulgarian",
	"Danish",
	"Finnish",
	"Icelandic",
	"Norwegian",
	"Romanian",
	"Swedish",
	"Ukrainian",
	"Belarusian",
	"Farsi",
	"Basque",
	"Macedonian",
	"Afrikaans",
	"Faeroese",
	"Latin",
	"Esperanto",
	"Tamazight",
	"Armenian")

class NotBglFile(Exception):
    pass

class BabylonParser:

    def __init__(self, filename):
        self.filename = filename
        self.open()
        self.load_informations()
        self.db = DataBase()

    def open(self):
        """  """
        try:
            self.fd = open(self.filename, 'rb')
        except IOError:
            print >> sys.stderr, "No such file"

        if not self.fd: return False

        # Check if its a BGL file
        buf = self.fd.read(6)
        if len(buf) < 6 or buf[:3] != "\x12\x34\x00" or \
            buf[3]=='\x00' or buf[3] > '\x02':
            raise NotBglFile("Its not a bgl file")

        i = ord(buf[4]) << 8 | ord(buf[5])
        self.fd.seek(i, os.SEEK_SET)
        tmp = StringIO(self.fd.read())
        self.fd.close()
        self.fd = gzip.GzipFile(fileobj=tmp, mode='rb')

    def close(self):
        """  """
        self.fd.close()

    def save_to_file(self, path):
        """  """
        self.db.open(path)

        self.db.add_word("__entries__", self.entries)
        self.db.add_word("__title__", self.title)
        self.db.add_word("__author__", self.author)
        self.db.add_word("__email__", self.email)
        self.db.add_word("__copyright__", self.copyright)
        self.db.add_word("__slang__", self.source_lang)
        self.db.add_word("__tlang__", self.target_lang)
        self.db.add_word("__desc__", self.description)
        self.db.add_word("__scharset__", self.source_charset)
        self.db.add_word("__tcharset__", self.target_charset)
        
        self.read_entries()

        self.db.close()

    def read_bytes(self, bytes):
        """  """
        if bytes < 1 or bytes > 4:
            return 0
        buf = self.fd.read(bytes)
        if not buf: raise IOError # EOF
        val = 0
        for i in buf:
            val = val << 8 | ord(i)
        return val

    def read_block(self):
        """  """
        block = type("block", (object,), {"length": 0,
                                          "type": -1,
                                          "data": ''})
        block.length = self.read_bytes(1)
        block.type = block.length & 0xf
        if block.type == 4: return False
        block.length >>= 4
        
        if block.length < 4:
            block.length = self.read_bytes(block.length + 1)
        else:
            block.length -= 4

        if block.length:
            try:
                block.data = self.fd.read(block.length)
            except IOError:
                return False
        return block

    def _reset(self):
        self.fd.seek(0)        

    def load_informations(self):
        """  """
        def _read(block, pos):
            tmp = ''
            for i in xrange(block.length - 2):
                pos += 1
                tmp += block.data[pos]
            return tmp

        self.entries = 0
        self.title = ''
        self.author = ''
        self.email = ''
        self.copyright = ''
        self.source_lang = ''
        self.target_lang = ''
        self.description = ''
        self.source_charset = ''
        self.target_charset = ''
        while True:
            block = self.read_block()
            if not block: break

            if block.type == 10 or \
               block.type == 1:
                self.entries += 1

            elif block.type == 3:
                pos = 1
                t = ord(block.data[1])
                if t == 1:
                    self.title = self.utf8(_read(block, pos))
                elif t == 2:
                    self.author = self.utf8(_read(block, pos))
                elif t == 3:
                    self.email = self.utf8(_read(block, pos))
                elif t == 4:
                    self.copyright = self.utf8(_read(block, pos))
                elif t == 7:
                    self.source_lang = self.utf8(languages[ord(block.data[5])])
                elif t == 8:
                    self.target_lang = self.utf8(languages[ord(block.data[5])])
                elif t == 9:
                    self.description = self.utf8(_read(block, pos))
                elif t == 26:
                    type = ord(block.data[2])
                    if type > 64:
                        type -= 65
                    self.source_charset = self.utf8(charsets[type])
                elif t == 27:
                    type = ord(block.data[2])
                    if type > 64:
                        type -= 65
                    self.target_charset = self.utf8(charsets[type])

        self._reset()

    def read_entries(self):
        """  """
        while True:
            block = self.read_block()
            if not block: break

            if block.type == 10 or \
               block.type == 1:
                pos = 0 
                l = 0
                l = block.data[pos]
                headword = ''
                for i in xrange(ord(l)):
                    pos += 1
                    headword += block.data[pos]

                # Definition
                l = 0
                pos += 1
                l = ord(block.data[pos]) << 8
                pos += 1
                l |= ord(block.data[pos])

                definition = ''
                for i in xrange(l):
                    if ord(block.data[pos]) == 0x0a:
                        definition = "\n"
                        pos += 1
                    else:
                        pos +=1
                        definition += block.data[pos]
                headword, definition = self.convert_to_utf8(headword, definition)

                if self.db.opened:
                    self.db.add_word(headword, definition)
        self._reset()

    def utf8(self, s):
        if s:
            s = s.encode("utf8")
        return s

    def convert_to_utf8(self, headword, definition):
        headword = headword.strip()
        headword = headword.decode(self.source_charset)
        headword = headword.split("$")[0]
        headword = self.utf8(headword)
        
        definition = definition.strip()
        definition = definition.decode(self.target_charset)
        definition = definition.split('\x14')[0]
        definition = self.utf8(definition)
        
        return headword, definition
