# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Peter Levi <peterlevi@peterlevi.com>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

from gi.repository import Gio, Gtk # pylint: disable=E0611
import logging
logger = logging.getLogger('variety_lib')

from . helpers import get_builder, show_uri, get_help_uri

# This class is meant to be subclassed by VarietyWindow.  It provides
# common functions and some boilerplate.
class Window(Gtk.Window):
    __gtype_name__ = "Window"

    # To construct a new instance of this method, the following notable 
    # methods are called in this order:
    # __new__(cls)
    # __init__(self)
    # finish_initializing(self, builder)
    # __init__(self)
    #
    # For this reason, it's recommended you leave __init__ empty and put
    # your initialization code in finish_initializing
    
    def __new__(cls):
        """Special static method that's automatically called by Python when 
        constructing a new instance of this class.
        
        Returns a fully instantiated BaseVarietyWindow object.
        """
        builder = get_builder('VarietyWindow')
        new_object = builder.get_object("variety_window")
        new_object.finish_initializing(builder)
        return new_object

    def finish_initializing(self, builder):
        """Called while initializing this instance in __new__

        finish_initializing should be called after parsing the UI definition
        and creating a VarietyWindow object with it in order to finish
        initializing the start of the new VarietyWindow instance.
        """
        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.ui = builder.get_ui(self, True)
        self.PreferencesDialog = None # class
        self.preferences_dialog = None # instance
        self.AboutDialog = None # class

#        self.settings = Gio.Settings("net.launchpad.variety")
#        self.settings.connect('changed', self.on_preferences_changed)

        # Optional Launchpad integration
        # This shouldn't crash if not found as it is simply used for bug reporting.
        # See https://wiki.ubuntu.com/UbuntuDevelopment/Internationalisation/Coding
        # for more information about Launchpad integration.
        try:
            from gi.repository import LaunchpadIntegration # pylint: disable=E0611
            # LaunchpadIntegration.add_items(self.ui.helpMenu, 1, True, True)
            LaunchpadIntegration.set_sourcepackagename('variety')
        except ImportError:
            pass

    def on_mnu_contents_activate(self, widget, data=None):
        show_uri(self, "ghelp:%s" % get_help_uri())

    def on_mnu_about_activate(self, widget, data=None):
        """Display the about box for variety."""
        if self.about is not None:
            logger.debug('show existing about_dialog')
            self.about.set_keep_above(True)
            self.about.present()
            self.about.set_keep_above(False)
            self.about.present()
        elif self.AboutDialog is not None:
            logger.debug('create new about dialog')
            self.about = self.AboutDialog() # pylint: disable=E1102
            response = self.about.run()
            self.about.destroy()
            self.about = None

    def get_preferences_dialog(self):
        if not self.preferences_dialog:
            self.create_preferences_dialog()
        return self.preferences_dialog

    def create_preferences_dialog(self):
        if not self.preferences_dialog:
            logger.debug('create new preferences_dialog')
            self.preferences_dialog = self.PreferencesDialog(parent=self) # pylint: disable=E1102

            def _on_preferences_dialog_destroyed(widget, data=None):
                logger.debug('on_preferences_dialog_destroyed')
                self.preferences_dialog = None
            self.preferences_dialog.connect('destroy', _on_preferences_dialog_destroyed)

            def _on_preferences_close_button(arg1, arg2):
                self.preferences_dialog.close()
                return True
            self.preferences_dialog.connect('delete_event', _on_preferences_close_button)

    def on_mnu_preferences_activate(self, widget=None, data=None):
        """Display the preferences window for variety."""

        """ From the PyGTK Reference manual
           Say for example the preferences dialog is currently open,
           and the user chooses Preferences from the menu a second time;
           use the present() method to move the already-open dialog
           where the user can see it."""
        if self.preferences_dialog is not None:
            if self.preferences_dialog.get_visible():
                logger.debug('bring to front existing and visible preferences_dialog')
                self.preferences_dialog.set_keep_above(True)
                self.preferences_dialog.present()
                self.preferences_dialog.set_keep_above(False)
                self.preferences_dialog.present()
            else:
                logger.debug('reload and show existing but non-visible preferences_dialog')
                self.preferences_dialog.reload()
                self.preferences_dialog.show()

        elif self.PreferencesDialog is not None:
            self.create_preferences_dialog()
            self.preferences_dialog.show()
        # destroy command moved into dialog to allow for a help button

    def on_mnu_close_activate(self, widget, data=None):
        """Signal handler for closing the VarietyWindow."""
        self.destroy()

    def on_destroy(self, widget, data=None):
        """Called when the VarietyWindow is closed."""
        pass
        # Clean up code for saving application state should be added here.
        # Gtk.main_quit()

    def on_preferences_changed(self, settings, key, data=None):
        logger.debug('preference changed: %s = %s' % (key, str(settings.get_value(key))))
