#!/usr/bin/python

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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
from .constants import folder_cleaner_constants as constants

@Gtk.Template(resource_path = constants['UI_PATH'] + 'preferences.ui')
class PreferencesWindow(Gtk.Dialog):

    __gtype_name__ = "_preferences_dialog"


    sorting_combobox = Gtk.Template.Child()
    photo_sort_switcher = Gtk.Template.Child()

    def __init__(self, app, *args, **kwargs):
        super().__init__(**kwargs)
    
        self.settings = Gio.Settings.new(constants['main_settings_path'])
        self.sorted_by_category = self.settings.get_boolean('sort-by-category')
        self.photo_sort = self.settings.get_boolean('photo-sort')
        self.photo_sort_switcher.set_active(self.photo_sort)

        if self.sorted_by_category:
            self.sorting_combobox.props.active = 1
        else:
            self.sorting_combobox.props.active = 0


    @Gtk.Template.Callback()
    def on_sorting_combobox_changed(self, box):
        if box.props.active == 0: #by extension
            self.settings.set_boolean('sort-by-category', False) #by type
        else:
            self.settings.set_boolean('sort-by-category', True)

    @Gtk.Template.Callback()
    def on_photo_sort_switcher_state_set(self, switch, w):
        if switch.get_active():
            self.settings.set_boolean('photo-sort', True)
        else:
            self.settings.set_boolean('photo-sort', False)
