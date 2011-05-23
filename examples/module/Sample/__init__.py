from kabukiman.module import Module
import gtk

class Sample(Module):

    def is_configurable(self):
        """  """
        return True

    def look_up(self, word):
        return "Penguins are nice"

    def show_config_dialog(self, parent):
        """  """
        dialog = gtk.Dialog(parent=parent)
        dialog.vbox.pack_start(gtk.Label("SAMPLE"), True)
        dialog.vbox.show_all()
        dialog.run()
        dialog.destroy()
