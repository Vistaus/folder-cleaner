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


from typing import List
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GExiv2', '0.10')
from gi.repository import Gtk, Gio, GLib
from .constants import folder_cleaner_constants as constants
from .sorting import Sorting


@Gtk.Template(resource_path=constants['UI_PATH'] + 'folder_box.ui')
class FolderBox(Gtk.ListBoxRow):
    __gtype_name__ = "folder_box_row"

    _sort_photos_button = Gtk.Template.Child()
    _folder_box_label = Gtk.Template.Child()

    def __init__(self, label, *args, **kwargs):
        super().__init__(**kwargs)
        self.label: str = label
        self.settings: Gio.Settings = Gio.Settings.new(constants['main_settings_path'])
        self.sort: Sorting = Sorting(self.label)
        self.settings.connect("changed::photo-sort", self.on_photos_sort_change, self._sort_photos_button)

        if self.settings.get_boolean('photo-sort'):
            self._sort_photos_button.props.visible = True
        else:
            self._sort_photos_button.props.visible = False

    @Gtk.Template.Callback()
    def on__sort_photos_button_clicked(self, button: Gtk.Button) -> None:

        # TODO other exifs
        if self.settings.get_int('photo-sort-by') == 0:
            sort_exif: str = 'Exif.Image.DateTime'

        if self.sort.photos_by_exif(sort_exif):
            self.settings.set_boolean('is-sorted', True)

    @Gtk.Template.Callback()
    def on__sort_files_clicked(self, button: Gtk.Button) -> None:
        if self.settings.get_boolean('sort-by-category'):
            if self.sort.files_by_content():
                self.settings.set_boolean('is-sorted', True)
        else:
            if self.sort.files_by_extension():
                self.settings.set_boolean('is-sorted', True)

    @Gtk.Template.Callback()
    def on__open_folder_clicked(self, button: Gtk.Button) -> None:
        GLib.spawn_async(['/usr/bin/xdg-open', self.label])

    @Gtk.Template.Callback()
    def on__close_folder_clicked(self, button: Gtk.Button) -> None:
        saved_folders: List[str] = self.settings.get_value('saved-folders').unpack()
        saved_folders.remove(self.label)
        self.settings.set_value('saved-folders', GLib.Variant('as', saved_folders))
        self.destroy()

    def on_photos_sort_change(self, settings: Gio.Settings, key: str, button: Gtk.Button) -> None:
        if settings.get_boolean(key):
            button.props.visible = True
        else:
            button.props.visible = False
