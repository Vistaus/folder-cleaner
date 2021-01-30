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

from typing import Dict, List
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')
from gi.repository import Gtk, Gio, GLib, Handy, Gdk
from .constants import folder_cleaner_constants as constants
from .user_folder import UserFoldersBoxRow


@Gtk.Template(resource_path=constants['UI_PATH'] + 'preferences.ui')
class PreferencesWindow(Handy.PreferencesWindow):
    __gtype_name__ = "hdy_preferences_dialog"

    sorting_combobox = Gtk.Template.Child()
    photo_sort_switcher = Gtk.Template.Child()
    user_folders_switcher = Gtk.Template.Child()
    clear_all_user_folder_button = Gtk.Template.Child()
    photo_sorting_combobox = Gtk.Template.Child()
    add_user_folder_section = Gtk.Template.Child()
    photo_sorting_section = Gtk.Template.Child()
    section_user_folders = Gtk.Template.Child()
    add_user_folder_button = Gtk.Template.Child()

    def __init__(self, app, *args, **kwargs):
        super().__init__(**kwargs)

        self.settings: Gio.Settings = Gio.Settings.new(constants['main_settings_path'])
        self.sorted_by_category = self.settings.get_boolean('sort-by-category')

        self.user_folders: bool = self.settings.get_boolean('user-folders')
        self.user_folders_switcher.set_active(self.user_folders)

        self.photo_sort: bool = self.settings.get_boolean('photo-sort')
        self.photo_sort_switcher.set_active(self.photo_sort)

        self.settings.connect("changed::saved-user-folders", self.on_saved_user_folders_change, None)

        user_saved_folders: Dict[str, str] = self.settings.get_value('saved-user-folders').unpack()

        # for user created formats and folders
        self.new_user_formats: Dict[str, str] = {}

        self.sorting_combobox.props.active = 1 if self.sorted_by_category else 0
        self.photo_sorting_combobox.active = self.settings.get_int('photo-sort-by')
        self.add_user_folder_section.props.visible = True if self.user_folders else False
        if self.user_folders and user_saved_folders:
            self.section_user_folders.props.visible = True
        else:
            self.section_user_folders.props.visible = False

        if user_saved_folders:
            self.populate_user_folders()

    @Gtk.Template.Callback()
    def on_sorting_combobox_changed(self, box: Gtk.ComboBox) -> None:
        if box.props.active == 0:  # by extension
            self.settings.set_boolean('sort-by-category', False)  # by type
        else:
            self.settings.set_boolean('sort-by-category', True)

    @Gtk.Template.Callback()
    def on_photo_sorting_combobox_changed(self, box: Gtk.ComboBox) -> None:
        if box.props.active == 0:  # by date
            self.settings.set_int('photo-sort-by', 0)  # by date

    @Gtk.Template.Callback()
    def on_photo_sort_switcher_state_set(self, switch: Gtk.Switch, state: bool) -> None:
        self.settings.set_boolean('photo-sort', state)
        self.photo_sorting_section.props.visible = state

    @Gtk.Template.Callback()
    def on_user_folders_switcher_state_set(self, switch: Gtk.Switch, state: bool):
        user_saved_folders: Dict[str, str] = self.settings.get_value('saved-user-folders').unpack()
        self.settings.set_boolean('user-folders', state)
        self.add_user_folder_section.props.visible = state
        if state and user_saved_folders:
            self.section_user_folders.props.visible = True
        else:
            self.section_user_folders.props.visible = False

    @Gtk.Template.Callback()
    def on_add_user_folder_button_clicked(self, btn: Gtk.Button) -> None:
        extensions: List[str] = []
        new_folders: Dict[str, str] = {}

        if not self.section_user_folders.props.visible:
            self.section_user_folders.props.visible = True

        ufolder: UserFoldersBoxRow = UserFoldersBoxRow()
        self.section_user_folders.add(ufolder)
        children: List[UserFoldersBoxRow] = self.section_user_folders.get_children()

        if children:
            for child in children:  # child = UserFoldersBoxRow instance
                extension: str = child.get_subtitle()
                while extension in extensions:
                    ufolder.set_subtitle(extension + ' copy')
                    extension += ' copy'
                extensions.append(extension)

        if children:
            for child in children:
                new_folders[child.get_subtitle()] = child.get_title()

        self.settings.set_value('saved-user-folders', GLib.Variant('a{ss}', new_folders))

    @Gtk.Template.Callback()
    def on_delete_event(self, w: Gtk.Widget, e: Gdk.Event) -> None:  # when preference window closed
        # save new user formats to GSettings
        # null before new formats from listbox added
        new_folders: Dict[str, str] = {}

        children: List[UserFoldersBoxRow] = self.section_user_folders.get_children()
        for child in children:  # child = UserFoldersBoxRow instance
            extension: str = child.get_subtitle()
            folder: str = child.get_title()
            new_folders[extension] = folder

        # save new user-made formats
        self.settings.set_value('saved-user-folders', GLib.Variant('a{ss}', new_folders))

    @Gtk.Template.Callback()
    def on_clear_all_user_folder_button_clicked(self, btn: Gtk.Button) -> None:
        children: List[UserFoldersBoxRow] = self.section_user_folders.get_children()
        for child in children:  # child = UserFoldersBoxRow instance
            child.destroy()
        self.settings.reset('saved-user-folders')
        self.section_user_folders.props.visible = False

    def on_saved_user_folders_change(self, settings: Gio.Settings, key: str, widget: Gtk.Widget) -> None:
        user_folder_active: bool = self.settings.get_boolean('user-folders')
        if user_folder_active:
            if len(self.section_user_folders.get_children()) > 0:
                self.section_user_folders.props.visible = True
            else:
                self.section_user_folders.props.visible = False

    ###############################

    def populate_user_folders(self) -> None:
        user_saved_folders: Dict[str, str] = self.settings.get_value('saved-user-folders').unpack()
        for k, v in user_saved_folders.items():
            ufolder: UserFoldersBoxRow = UserFoldersBoxRow(k, v)
            self.section_user_folders.add(ufolder)
