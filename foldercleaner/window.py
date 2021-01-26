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

from locale import gettext as _
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib, Gdk

from .folder_box import FolderBox
from .preferences import PreferencesWindow
from .aboutdialog import AboutWindow
from .constants import folder_cleaner_constants as constants
from .helpers import operations, folders_made, labels


@Gtk.Template(resource_path=constants['UI_PATH'] + 'folder_cleaner.ui')
class FolderCleaner(Gtk.ApplicationWindow):
    __gtype_name__ = "_main_window"

    _main_list_box = Gtk.Template.Child()
    _main_revealer = Gtk.Template.Child()
    main_label_box = Gtk.Template.Child()
    label_box = Gtk.Template.Child()

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, title=_("Folder Cleaner"), application=app)

        self.set_size_request(500, 300)

        self.set_wmclass("Folder Cleaner", _("Folder Cleaner"))
        self.settings = Gio.Settings.new(constants['main_settings_path'])
        self.settings.connect("changed::count", self.on_count_change, None)
        self.settings.connect("changed::is-sorted", self.on_is_sorted_change, None)
        self.saved_folders = self.settings.get_value('saved-folders')
        self.user_saved_folders = self.settings.get_value('saved-user-folders').unpack()

        self.label_box.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.label_box.connect("drag-data-received", self.on_drag_data_received)
        self.label_box.drag_dest_set_target_list(None)
        self.label_box.drag_dest_add_text_targets()

        css_file = Gio.File.new_for_path('data/style.css')
        css_provider = Gtk.CssProvider()
        css_provider.load_from_file(css_file)
        screen = Gdk.Screen.get_default()

        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_USER)

        if self.saved_folders:
            self.main_label_box.props.visible = False
            for path in self.saved_folders:
                folder = FolderBox(path)
                if not self._main_list_box.props.visible:
                    self._main_list_box.props.visible = True
                    folder._folder_box_label.set_label(path)
                self._main_list_box.insert(folder, -1)

    @Gtk.Template.Callback()
    def on__add_button_clicked(self, button):
        chooser = Gtk.FileChooserDialog(title=_("Open Folder"),
                                        transient_for=self,
                                        action=Gtk.FileChooserAction.SELECT_FOLDER,
                                        buttons=(_("Cancel"), Gtk.ResponseType.CANCEL,
                                                 _("OK"), Gtk.ResponseType.OK))
        response = chooser.run()
        if response == Gtk.ResponseType.OK:
            self.main_label_box.props.visible = False
            label = chooser.get_filename()
            folder = FolderBox(label)
            self._main_list_box.props.visible = True
            folder._folder_box_label.set_label(label)
            self._main_list_box.insert(folder, -1)
            chooser.destroy()
        else:
            chooser.destroy()

    @Gtk.Template.Callback()
    def on__preferences_button_clicked(self, button):
        preferences = PreferencesWindow(self)
        preferences.show()

    @Gtk.Template.Callback()
    def on__about_button_clicked(self, button):
        about = AboutWindow(self)
        about.set_logo_icon_name(constants["APP_ID"])
        about.set_copyright("GPLv3+")
        about.run()
        about.destroy()

    @Gtk.Template.Callback()
    def on__main_revealer_button_clicked(self, button):
        for key, value in operations.items():
            from_file = Gio.File.new_for_path(value)
            to_file = Gio.File.new_for_path(key)
            try:
                from_file.move(to_file, Gio.FileCopyFlags.NONE)
            except gi.repository.GLib.Error as e:
                print(e)
                pass

        operations.clear()

        for folder in folders_made:
            GLib.spawn_async(['/usr/bin/rm', '-r', folder])

        folders_made.clear()

    @Gtk.Template.Callback()
    def on__revealer_close_button_clicked(self, button):
        self.settings.set_boolean('is-sorted', False)
        operations = {}

    @Gtk.Template.Callback()
    def on__main_window_destroy(self, w):
        self.settings.set_value('saved-folders', GLib.Variant('as', labels))

    def on_count_change(self, settings, key, button):
        if self.settings.get_int('count') > 0:
            self.main_label_box.props.visible = False
        else:
            self.main_label_box.props.visible = True
            self.settings.reset('saved-folders')

    def on_is_sorted_change(self, settings, key, button):
        if self.settings.get_boolean('is-sorted'):
            self._main_revealer.set_reveal_child(True)
        else:
            self._main_revealer.set_reveal_child(False)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        drop_source = GLib.filename_from_uri(data.get_text())
        folder_path = drop_source[0].rstrip()

        if GLib.file_test(folder_path, GLib.FileTest.IS_DIR):
            self.main_label_box.props.visible = False
            label = folder_path
            folder = FolderBox(label)
            self._main_list_box.props.visible = True
            folder._folder_box_label.set_label(label)
            self._main_list_box.insert(folder, -1)
        else:
            print(f"Error: {folder_path} is not a folder.")
