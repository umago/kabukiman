#!/usr/bin/python
# coding: utf-8

import gtk
import gobject

class DialogProgress(gtk.Dialog):
    
    def __init__(self, parent=None):
        gtk.Dialog.__init__(self, parent=parent)
        self.set_title('')
        self.set_deletable(False)

        self.resize(90,90)
        self.connect("destroy", self.destroy_progress)

        align = gtk.Alignment(0.5, 0.5, 0, 0)
        align.set_padding(5, 5, 5, 5)
        text = gtk.Label()
        text.set_markup("<b>Parsing dictionary</b>")
        self.vbox.pack_start(text) 
        self.vbox.pack_start(align, False, False, 5)
        align.show()

        self.pbar = gtk.ProgressBar()
        self.pbar.set_text("Wait...")

        align.add(self.pbar)
        self.vbox.show_all()

        self.timer = gobject.timeout_add(100, self.start_progress)

    def start_progress(self):
        """ """
        self.pbar.pulse()
        return True

    def destroy_progress(self, widget, data=None):
        """  """
        gobject.source_remove(self.timer)
        self.timer = None
