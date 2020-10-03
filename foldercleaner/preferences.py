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
from gi.repository import Gtk, Gio, GLib
from .constants import folder_cleaner_constants as constants
from .user_folder import UserFoldersBox
from .helpers import user_folders


@Gtk.Template(resource_path=constants['UI_PATH'] + 'preferences.ui')
class PreferencesWindow(Gtk.Dialog):
    __gtype_name__ = "_preferences_dialog"

    sorting_combobox = Gtk.Template.Child()
    photo_sort_switcher = Gtk.Template.Child()
    user_folders_box = Gtk.Template.Child()
    user_folders_switcher = Gtk.Template.Child()
    user_folders_list_box = Gtk.Template.Child()
    user_folders_frame = Gtk.Template.Child()
    user_folders_scrolled_window = Gtk.Template.Child()
    user_folders_second_box = Gtk.Template.Child()

    def __init__(self, app, *args, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new(constants['main_settings_path'])
        self.sorted_by_category = self.settings.get_boolean('sort-by-category')
        self.settings.connect("changed::user-folders", self.on_user_folders_change, self.user_folders_box)
        self.user_folders = self.settings.get_boolean('user-folders')
        self.user_folders_switcher.set_active(self.user_folders)
        self.photo_sort = self.settings.get_boolean('photo-sort')
        self.photo_sort_switcher.set_active(self.photo_sort)
        self.settings.connect("changed::count-user-folders", self.on_quantity_user_folders_change, None)
        self.user_folders_quantity = self.settings.get_int('count-user-folders')
        self.user_saved_folders = self.settings.get_value('saved-user-folders').unpack()

        if self.user_folders_quantity > 0:
            self.user_folders_frame.props.visible = True
            for k, v in self.user_saved_folders.items():
                ufolder = UserFoldersBox(k, v)
                self.user_folders_list_box.insert(ufolder, -1)

        self.sorting_combobox.props.active = 1 if self.sorted_by_category else 0
        self.user_folders_box.props.visible = True if self.user_folders else False

    @Gtk.Template.Callback()
    def on_sorting_combobox_changed(self, box):
        if box.props.active == 0:  # by extension
            self.settings.set_boolean('sort-by-category', False)  # by type
        else:
            self.settings.set_boolean('sort-by-category', True)

    @Gtk.Template.Callback()
    def on_photo_sort_switcher_state_set(self, switch, state):
        self.settings.set_boolean('photo-sort', state)

    @Gtk.Template.Callback()
    def on_user_folders_switcher_state_set(self, switch, state):
        self.settings.set_boolean('user-folders', state)

    @Gtk.Template.Callback()
    def on_add_user_folder_button_clicked(self, btn):
        self.user_folders_frame.props.visible = True
        extension = constants['default_extension_name']
        folder = constants['default_folder_name']
        ufolder = UserFoldersBox(extension, folder)  # quantity changed +1
        print(ufolder)
        self.user_folders_list_box.insert(ufolder, -1)
        # TODO Dynamic resize scrolled window

    def on_quantity_user_folders_change(self, s, k, w):
        if self.settings.get_int('count-user-folders') == 0:
            self.user_folders_frame.props.visible = False
            self.resize(700, 200)
        else:
            self.user_folders_frame.props.visible = True

    def on_user_folders_change(self, s, k, w):
        if s.get_boolean(k):
            w.props.visible = True
        else:
            w.props.visible = False
            self.resize(700, 200)

    @Gtk.Template.Callback()
    def on_delete_event(self, w, e):  # when preference window closed
        new_user_formats = {}
        for child in self.user_folders_list_box.get_children():
            # child = Gtk.ListBoxRow
            for w in child.get_children():  # w = UserFolders
                extension = w.file_extension_button_label.props.label
                folder = w.user_folder_button_label.props.label
                new_user_formats[extension] = folder
        user_folders.update(new_user_formats)
