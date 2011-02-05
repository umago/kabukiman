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

import urllib
import simplejson
import gtk
import os
from ConfigParser import ConfigParser

from dialog_config import DialogConfig
from global_ import *

from kabukiman.module import Module
from kabukiman.utils import *

class GoogleTranslate(Module):
    """The Google Translate Module"""

    def __init__(self):
        Module.__init__(self)
        self.config = ConfigParser()
        self.config_file = os.sep.join((get_home_dir(), ".kabukiman", "googletranslate.cfg"))
        if not os.path.exists(self.config_file):
            self._create_default_config() 

    def _create_default_config(self):
        self.config.add_section("GoogleTranslate")
        self.config.set("GoogleTranslate", "languages", repr([('','en')]))
        with open(self.config_file, 'wb') as configfile:
            self.config.write(configfile)

    def is_configurable(self):
        """  """
        return True

    def look_up(self, word):
        """  """
        # Check: http://code.google.com/apis/ajaxlanguage/terms.html
        if len(word) > 5000:
            return ''
      
        # Get a list of pairs of languages to be translated
        # this list will be filled by our treeview
        languages = list()
        self.config.read(self.config_file)
        if self.config.has_option("GoogleTranslate", "languages"):
            languages = self.config.get("GoogleTranslate", "languages")
            try:
                languages = eval(languages)
            except Exception, e:
                # TODO: Message
                return

        result = ''
        for num, langs in enumerate(languages):
            from_lang, to_lang = langs
            langpair="%s|%s"%(from_lang, to_lang)
            base_url="http://ajax.googleapis.com/ajax/services/language/translate?"
            data = urllib.urlencode({'v': 1.0, "ie": "UTF8", 'q': word.encode("utf-8"), "langpair": langpair})
            url = base_url + data
            search_results = urllib.urlopen(url)
            search_results = search_results.read()
            json = simplejson.loads(search_results)
            if json:
                response_data = json["responseData"]
                if response_data is None:
                    continue

                # Insert a space between the results
                if num > 0:
                    result += '\n'

                # If not lang google will guess to us :)~
                if not from_lang:
                    from_lang = response_data["detectedSourceLanguage"]

                try:
                    from_lang = LANGUAGES[from_lang]
                except Exception:
                    # TODO: Message
                    pass
                to_lang = LANGUAGES[to_lang]
                result += "<b>[%s -> %s]</b>\n<quote>%s</quote>\n" % (from_lang,
                          to_lang, response_data["translatedText"])
        return self._remove_html_codes(result)

    def _remove_html_codes(self, text):
        """  """
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        return text

    def show_config_dialog(self, parent):
        """  """
        dialog = DialogConfig(parent)
        dialog.run()
        dialog.destroy()
