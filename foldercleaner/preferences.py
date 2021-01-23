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
    clear_all_button = Gtk.Template.Child()
    preferences_list_box = Gtk.Template.Child()
    photo_sort_row = Gtk.Template.Child()
    photo_sort_by_row = Gtk.Template.Child()

    def __init__(self, app, *args, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new(constants['main_settings_path'])
        self.sorted_by_category = self.settings.get_boolean('sort-by-category')

        self.settings.connect("changed::user-folders", self.on_user_folders_change, self.user_folders_box)

        self.user_folders = self.settings.get_boolean('user-folders')
        self.user_folders_switcher.set_active(self.user_folders)

        self.photo_sort = self.settings.get_boolean('photo-sort')
        self.photo_sort_switcher.set_active(self.photo_sort)

        self.user_saved_folders = self.settings.get_value('saved-user-folders').unpack()

        # for user created formats and folders
        self.new_user_formats = {}

        self.sorting_combobox.props.active = 1 if self.sorted_by_category else 0
        self.user_folders_box.props.visible = True if self.user_folders else False
        self.user_folders_frame.props.visible = True if self.user_saved_folders else False

        if self.user_saved_folders:
            self.populate_user_folders()

    @Gtk.Template.Callback()
    def on_sorting_combobox_changed(self, box):
        if box.props.active == 0:  # by extension
            self.settings.set_boolean('sort-by-category', False)  # by type
        else:
            self.settings.set_boolean('sort-by-category', True)

    @Gtk.Template.Callback()
    def on_photo_sort_switcher_state_set(self, switch, state):
        self.set_photo_sort_preferences(state)

    @Gtk.Template.Callback()
    def on_user_folders_switcher_state_set(self, switch, state):
        self.settings.set_boolean('user-folders', state)

    @Gtk.Template.Callback()
    def on_add_user_folder_button_clicked(self, btn):
        self.user_folders_frame.props.visible = True
        children = self.user_folders_list_box.get_children()
        extensions = []
        ufolder = UserFoldersBox()

        if children:
            for child in children:  # each child contains another child of UserFolder instance
                user_folder = child.get_child()
                extension = user_folder.extension
                extensions.append(extension)

        #check if extension already present
        while ufolder.extension in extensions:
            ufolder.extension += '_copy'

        ufolder.file_extension_button_label.props.label = ufolder.extension  # from button label
        ufolder.user_folder_button_label.props.label = ufolder.folder  # from button label
        self.user_folders_list_box.insert(ufolder, -1)

    def on_user_folders_change(self, s, k, w):
        if s.get_boolean(k):
            w.props.visible = True
        else:
            w.props.visible = False
            self.resize(700, 200)

    def populate_user_folders(self):
        for k, v in self.user_saved_folders.items():
            ufolder = UserFoldersBox(k, v)
            self.user_folders_list_box.insert(ufolder, -1)

    @Gtk.Template.Callback()
    def on_delete_event(self, w, e):  # when preference window closed
        # save new user formats to GSettings
        # null before new formats from listbox added
        self.user_saved_folders = {}

        children = self.user_folders_list_box.get_children()  # children = list of Gtk.ListBox
        for child in children:  # each child contains another child of UserFolder instance
            user_folder = child.get_child()
            extension = user_folder.extension
            folder = user_folder.folder
            self.user_saved_folders[extension] = folder

        # save new user-made formats
        self.settings.set_value('saved-user-folders', GLib.Variant('a{ss}', self.user_saved_folders))

    @Gtk.Template.Callback()
    def on_clear_all_button_clicked(self, btn):
        children = self.user_folders_list_box.get_children()  # children = list of Gtk.ListBox
        for child in children:  # each child contains another child of UserFolder instance
            child.destroy()

    @Gtk.Template.Callback()
    def on_preferences_list_box_row_activated(self, list_box, row):
        if row.get_name() == 'photo_sort':
            self.photo_sort_switcher.props.state = not self.photo_sort_switcher.props.state
            self.set_photo_sort_preferences(self.photo_sort_switcher.props.state)
        elif row.get_name() == 'user_folders':
            self.user_folders_switcher.props.state = not self.user_folders_switcher.props.state
            self.settings.set_boolean('user-folders', self.user_folders_switcher.props.state)

    def set_photo_sort_preferences(self, state):
        self.settings.set_boolean('photo-sort', state)
        self.photo_sort_by_row.props.visible = state
        if not self.photo_sort_by_row.props.visible:
            self.resize(700, 200)

