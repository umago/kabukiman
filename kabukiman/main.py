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
import time
import traceback
import gobject
import gtk
gtk.gdk.threads_init()

from threading import Thread

from kabukiman.config import *
init_gettext() # Start internationalization

from kabukiman.preferences import *
from kabukiman.version import get_version
from kabukiman.ui.combobox_definition import ComboBoxDefinition
from kabukiman.ui.treeview_shortcuts import TreeviewShortcuts
from kabukiman.ui.resultview import ResultView
from kabukiman.ui.menu_statusicon import MenuStatusIcon
from kabukiman.ui.menu_sidebar import MenuSidebar
from kabukiman.ui.treeview_results import TreeviewResults
from kabukiman.ui.dialog_modules import DialogModules
from kabukiman.core.module_manager import ModuleManager
from kabukiman.core.shortcut_manager import get_instance


class LookUpThread(Thread):
    """  """

    def __init__(self, parent, word):
        Thread.__init__(self)
        self.parent = parent
        self.word = word
        self.active = False

    def run(self):
        """Thread main loop

        Search the word in all active modules and
        insert then to the result view

        """
        self.active = True
        number_of_results = 0
        active_modules = self.parent.module_manager.get_enabled_modules()
        for module in active_modules:
            func = getattr(module, "look_up", None)
            if func and callable(func):
                # User feedback
                self.parent.statusbar.push(0, _("Searching in %s") \
                                           % module._name)

                try:
                    result = func(self.word)
                except Exception, e:
                    print >> sys.stderr, "Error searching in module %s" \
                                         % module._name
                    print >> sys.stderr, traceback.format_exc()
                    continue

                if result and \
                (isinstance(result, str) or isinstance(result, unicode)):
                    if not self.active:
                        break

                    # Threads and GUI :/
                    gobject.idle_add(self._insert_result, module._name, result)
                    number_of_results += 1
        self.parent.statusbar.push(0, _("%d definition(s) found") \
                                   % number_of_results)

    def _insert_result(self, module_name, result):
        """Insert the result to the result area
        and populates the results of the sidebar.

        """
        mark = self.parent.resultview.insert_result(result)
        self.parent.resultview.insert_source(module_name)
        self.parent.treeview_results.add_result(module_name, mark)

    def stop(self):
        """Stop the main loop."""
        self.active = False


class Main:
    """ Main class where the layout will be constructed,
    widgets out of the glade file will be added,
    signals will be connected and so on.

    """

    _look_up_thread = None

    def start(self):
        """  """
        self.builder = gtk.Builder()
        self.builder.set_translation_domain(APP_NAME)
        self.builder.add_from_file(GLADE_NAME)
        self.builder.connect_signals(self)
        self.shortcut_manager = get_instance()

        self._setup()
        self._init_widgets()
        self._setup_widgets()
        self._attach_callbacks()
        self._setup_preferences()

        self.window_main.realize()

        gtk.main()

    def _setup(self):
        """  """
        if not os.path.exists(CONFIGDIR):
            os.makedirs(CONFIGDIR)

    def _init_widgets(self):
        """  """
        self.window_main = self.builder.get_object("window_main")
        self.hpaned_main = self.builder.get_object("hpaned_main")
        self.image_sidebar = self.builder.get_object("image_sidebar")
        self.sidebar = self.hpaned_main.get_child1()
        self.statusbar = self.builder.get_object("statusbar")
        self.hbox_sidebar = self.builder.get_object("hbox_sidebar")
        self.alignment_definition = self.builder.\
                                             get_object("alignment_definition")
        self.button_go = self.builder.get_object("button_go")
        self.combobox_definition = ComboBoxDefinition()
        self.entry_definition = self.combobox_definition.child
        self.aboutdialog = self.builder.get_object("aboutdialog")
        self.dialog_preferences = self.builder.get_object("dialog_preferences")
        self.checkmenuitem_sidebar = self.builder. \
                                            get_object("checkmenuitem_sidebar")
        self.checkmenuitem_statusbar = self.builder. \
                                          get_object("checkmenuitem_statusbar")
        self.button_configure_module = self.builder. \
                                          get_object("button_configure_module")
        self.label_module_author = self.builder. \
                                              get_object("label_module_author")
        self.label_module_version = self.builder. \
                                             get_object("label_module_version")
        self.label_module_website = self.builder. \
                                             get_object("label_module_website")
        self.scrolledwindow_shortcuts = self.builder. \
                                         get_object("scrolledwindow_shortcuts")
        self.scrolledwindow_resultview = self.builder. \
                                        get_object("scrolledwindow_resultview")
        self.checkbutton_show_win_startup = self.builder. \
                                     get_object("checkbutton_show_win_startup")
        self.checkbutton_save_history = self.builder. \
                                         get_object("checkbutton_save_history")
        self.togglebutton_sidebar = self.builder. \
                                             get_object("togglebutton_sidebar")
        self.togglebutton_combobox_sidebar = self.builder. \
                                    get_object("togglebutton_combobox_sidebar")
        self.notebook_sidebar = self.builder. \
                                                 get_object("notebook_sidebar")
        self.scrolledwindow_sidebar_searchin = self.builder. \
                                  get_object("scrolledwindow_sidebar_searchin")
        self.scrolledwindow_sidebar_results = self.builder. \
                                   get_object("scrolledwindow_sidebar_results")
        self.resultview = ResultView()
        self.treeview_shortcuts = TreeviewShortcuts(self)
        self.module_manager = ModuleManager(MODULES_DIRS)
        self.status_icon = gtk.StatusIcon()
        self.menu_statusicon = MenuStatusIcon()
        self.menu_sidebar = MenuSidebar()
        self.dialog_modules = DialogModules(self.window_main)
        self.treeview_results = TreeviewResults()

    def _setup_widgets(self):
        """  """
        pixbuf_22x22 = gtk.gdk.pixbuf_new_from_file(os.sep.join((ICONS_DIR,
                                                   "kabukiman_22x22.png")))
        pixbuf_about = gtk.gdk.pixbuf_new_from_file(os.sep.join((ICONS_DIR,
                                                   "kabukiman_about.png")))
        self.window_main.set_icon(pixbuf_22x22)
        self.image_sidebar.set_from_file(os.sep.join((ICONS_DIR,
                                         "kabukiman_sidebar.png")))
        self.alignment_definition.add(self.combobox_definition)
        self.entry_definition.grab_focus()
        self.aboutdialog.set_version(get_version())
        self.aboutdialog.set_logo(pixbuf_about)
        self.aboutdialog.set_authors(AUTHORS)
        self.aboutdialog.set_artists(ARTISTS)
        self.aboutdialog.set_name(APP_NAME)
        self.aboutdialog.set_copyright(COPYRIGHT)
        self.aboutdialog.set_license(LICENSE)
        self.scrolledwindow_shortcuts.add(self.treeview_shortcuts)
        self.scrolledwindow_resultview.add(self.resultview)
        self.status_icon.set_from_pixbuf(pixbuf_22x22)
        self.status_icon.set_tooltip(APP_NAME.capitalize())
        self.status_icon.set_visible(True)
        self.shortcut_manager.init()
        self.scrolledwindow_sidebar_results.add(self.treeview_results)

    def _attach_callbacks(self):
        """  """
        self.entry_definition.connect("activate", self.go)
        self.status_icon.connect("button-press-event",
                                 self.show_menu_statusicon)
        self.menu_statusicon.menu_preferences.connect("activate",
                                                      self.show_preferences)
        self.menu_statusicon.menu_modules.connect("activate",
                                                  self.show_modules)
        self.menu_statusicon.menu_quit.connect("activate", self.quit)
        self.menu_sidebar.connect("deactivate", self.menu_sidebar_deactivate)
        self.menu_sidebar.menu_results.connect("activate",
                                          self.change_notebook_sidebar_page, 0)
        #self.menu_sidebar.menu_search_in.connect("activate",
        #                                 self.change_notebook_sidebar_page, 1)
        self.shortcut_manager.connect("quick_search", self.quick_search)
        self.shortcut_manager.connect("scan_selection", self.scan_selection)
        self.treeview_results.connect("cursor-changed", self.scroll_to_result)

    def _setup_preferences(self):
        """  """
        spinbutton_max_words_history = self.builder. \
                                     get_object("spinbutton_max_words_history")
        value = get_max_words_history()
        spinbutton_max_words_history.set_value(value)

        statusbar = get_statusbar_active()
        sidebar = get_sidebar_active()
        show_win_startup = get_show_win_startup()
        save_history = get_save_history()

        if not statusbar:
            self.statusbar.hide()

        if not sidebar:
            self.sidebar.hide()

        if not show_win_startup:
            self.window_main.show()

        # Setup widgets
        self.checkmenuitem_statusbar.set_active(statusbar)
        self.checkmenuitem_sidebar.set_active(sidebar)
        self.togglebutton_sidebar.set_active(sidebar)
        self.checkbutton_show_win_startup.set_active(show_win_startup)
        self.checkbutton_save_history.set_active(save_history)

        # Setup history
        if get_save_history():
            self.combobox_definition.load_history()

    # Callbacks
    #

    def go(self, widget):
        """Search the word/expression"""
        word = self.entry_definition.get_text().strip()
        if word != '':
            if word == str(ord('*')):
                word = _("The meaning of life, the universe and everything")

            self.entry_definition.set_text(word)
            self.entry_definition.grab_focus()
            self.combobox_definition.add_to_list(word)

            # Saving words history
            if get_save_history():
                self.combobox_definition.save_history()

            # Setup the resultview
            self.resultview.clear()
            self.resultview.insert_header(word)

            self.treeview_results.clear()

            # It's recklessly!
            if self._look_up_thread:
                if self._look_up_thread._Thread__started.is_set():
                    self._look_up_thread._Thread__stop()
                    self._look_up_thread.stop()

            self._look_up_thread = LookUpThread(self, word)
            self._look_up_thread.start()

    def new_search(self, widget):
        """  """
        self.entry_definition.set_text('')
        self.entry_definition.grab_focus()

    def about(self, widget):
        """Show the about dialog"""
        self.aboutdialog.run()
        self.aboutdialog.hide()

    def show_preferences(self, widget):
        """Show the preferences dialog"""
        self.dialog_preferences.run()
        self.dialog_preferences.hide()

    def show_modules(self, widget):
        """Show the modules dialog"""
        self.dialog_modules.run()
        self.dialog_modules.hide()

    def set_show_win_startup(self, widget):
        """  """
        active = self.checkbutton_show_win_startup.get_active()
        set_show_win_startup(active)

    def set_save_history(self, widget):
        """  """
        active = self.checkbutton_save_history.get_active()
        set_save_history(active)

    def set_max_words_history(self, widget):
        """  """
        value = int(widget.get_value())
        set_max_words_history(value)

    def quick_search(self, event):
        """ """
        timestamp = int(time.time())
        self.window_main.present_with_time(timestamp)
        self.window_main.window.focus()
        self.new_search(None)

    def scan_selection(self, event, word):
        """  """
        self.quick_search(None)
        self.entry_definition.set_text(word)
        self.go(None)

    def copy(self, widget):
        """  """
        self.resultview.copy()

    def select_all(self, widget):
        """  """
        if self.entry_definition.is_focus():
            self.entry_definition.grab_focus()
        else:
            self.resultview.select_all()

    def scroll_to_result(self, widget):
        """  """
        selection = self.treeview_results.get_selection()
        (model, giter) = selection.get_selected()
        try:
            mark = model.get_value(giter, 1)
        except TypeError:
            print >> sys.stderr, "Fail scrolling to result"
            return False

        self.resultview.scroll_to_result(mark)

    def quit(self, widget):
        """Shutdown kabukiman"""
        self.window_main.destroy()
        self.shortcut_manager.stop()
        gtk.main_quit()

    # Main Window
    #

    def close_window_main(self, widget, event=None):
        """Minimize the main window to the tray icon"""
        if event:
            if event.type == gtk.gdk.KEY_PRESS:
                if event.keyval == gtk.keysyms.Escape:
                    pass
                else:
                    return False

        self.window_main.hide()
        return True

    # Status bar
    #

    def toggle_statusbar(self, widget):
        """  """
        if not self.checkmenuitem_statusbar.get_active():
            set_statusbar_active(False)
            self.statusbar.hide()
        else:
            set_statusbar_active(True)
            self.statusbar.show()

    # Status icon
    #

    def show_menu_statusicon(self, widget, event):
        """  """
        def set_position(widget):
            """ """
            allocation = self.status_icon.get_geometry()[1]
            x = allocation.x
            y = allocation.y + allocation.height
            return (x, y, False)

        if event.button == 3: # Context button
            if self.menu_statusicon:
                # Show the popup menu
                self.menu_statusicon.show_all()
                self.menu_statusicon.popup(None, None, set_position, 3,
                                           event.time)

        elif event.button == 1: # Left button
            if self.window_main.window.is_visible():
                if self.window_main.has_toplevel_focus():
                    self.window_main.hide()
                else:
                    self.window_main.present()
            else:
                self.window_main.show()

    # Sidebar
    #

    def close_sidebar(self, widget):
        """  """
        self.checkmenuitem_sidebar.set_active(False)
        self.sidebar.hide()

    def toggle_sidebar(self, widget):
        """  """
        if not widget.get_active():
            set_sidebar_active(False)
            self.checkmenuitem_sidebar.set_active(False)
            self.togglebutton_sidebar.set_active(False)
            self.sidebar.hide()
        else:
            set_sidebar_active(True)
            self.checkmenuitem_sidebar.set_active(True)
            self.togglebutton_sidebar.set_active(True)
            self.sidebar.show()

    def menu_sidebar_deactivate(self, widget):
        """ """
        self.togglebutton_combobox_sidebar.set_active(False)

    def menu_sidebar_position(self, widget):
        """ """
        x, y = self.togglebutton_combobox_sidebar.window.get_origin()
        allocation = self.togglebutton_combobox_sidebar.get_allocation()
        x += allocation.x
        y += allocation.y + allocation.height
        return (x, y, False)

    def show_menu_sidebar_key(self, widget, event):
        """  """
        if event.keyval == gtk.keysyms.KP_Space or \
           event.keyval == gtk.keysyms.space or \
           event.keyval == gtk.keysyms.Return or \
           event.keyval == gtk.keysyms.KP_Enter:

            self.togglebutton_combobox_sidebar.set_active(True)
            self.menu_sidebar.show_all()
            self.menu_sidebar.popup(None, None, self.menu_sidebar_position, 3,
                                    event.time)
            return True

    def show_menu_sidebar_button(self, widget, event):
        """  """
        if event.button == 1:

            self.togglebutton_combobox_sidebar.set_active(True)
            self.menu_sidebar.show_all()
            self.menu_sidebar.popup(None, None, self.menu_sidebar_position, 3,
                                    event.time)
            return True

    def change_notebook_sidebar_page(self, widget, page):
        """  """
        if self.notebook_sidebar.get_current_page() == page:
            return

        label = self.builder.get_object("label_menu_sidebar")
        label.set_text(widget.get_label())
        self.notebook_sidebar.set_current_page(page)
