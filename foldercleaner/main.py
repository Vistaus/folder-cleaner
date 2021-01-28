#!/usr/bin/python3

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import locale
import sys
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')
from gi.repository import Gtk, GLib, Gio, Handy
from locale import gettext as _
from .window import FolderCleaner

# locales
locale.textdomain('com.github.Latesil.folder-cleaner')


def main():
    app = Application()
    return app.run(sys.argv)


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.github.Latesil.folder-cleaner",
                         flags=Gio.ApplicationFlags.FLAGS_NONE, **kwargs)

        self.window = None

        GLib.set_application_name(_('Folder Cleaner'))
        GLib.set_prgname("com.github.Latesil.folder-cleaner")

    def do_startup(self):
        Gtk.Application.do_startup(self)

        Handy.init()

    def do_activate(self):
        if not self.window:
            self.window = FolderCleaner(self)

        self.window.present()
