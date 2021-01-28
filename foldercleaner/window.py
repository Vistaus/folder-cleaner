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
gi.require_version('Handy', '1')
from gi.repository import Gtk, Gio, GLib, Gdk, Handy

from .folder_box import FolderBox
from .preferences import PreferencesWindow
from .aboutdialog import AboutWindow
from .constants import folder_cleaner_constants as constants


@Gtk.Template(resource_path=constants['UI_PATH'] + 'folder_cleaner.ui')
class FolderCleaner(Handy.ApplicationWindow):
    __gtype_name__ = "_main_window"

    _main_list_box = Gtk.Template.Child()
    _main_revealer = Gtk.Template.Child()
    _main_label_box = Gtk.Template.Child()
    _main_box = Gtk.Template.Child()

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, title=_("Folder Cleaner"), application=app)

        self.set_size_request(400, 300)

        self.set_wmclass("Folder Cleaner", _("Folder Cleaner"))
        self.settings = Gio.Settings.new(constants['main_settings_path'])
        self.settings.connect("changed::count", self.on_count_change, None)
        self.settings.connect("changed::is-sorted", self.on_is_sorted_change, None)
        self.saved_folders = self.settings.get_value('saved-folders')
        self.user_saved_folders = self.settings.get_value('saved-user-folders').unpack()

        self._main_box.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self._main_box.connect("drag-data-received", self.on_drag_data_received)
        self._main_box.drag_dest_set_target_list(None)
        self._main_box.drag_dest_add_text_targets()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource(constants['UI_PATH'] + 'foldercleaner.css')
        screen = Gdk.Screen.get_default()

        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        if self.saved_folders:
            self._main_label_box.props.visible = False
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
            self._main_label_box.props.visible = False
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
        operations = self.settings.get_value('operations').unpack()
        folders_made = self.settings.get_value('folders-made').unpack()
        for key, value in operations.items():
            from_file = Gio.File.new_for_path(value)
            to_file = Gio.File.new_for_path(key)
            try:
                from_file.move(to_file, Gio.FileCopyFlags.NONE)
            except GLib.Error as err:
                print('%s: %s. File: %s, (code: %s)' % (err.domain, err.message, err.code))

        self.settings.reset('operations')

        for folder in folders_made:
            GLib.spawn_async(['/usr/bin/rm', '-r', folder])

        self.settings.reset('folders-made')

    @Gtk.Template.Callback()
    def on__revealer_close_button_clicked(self, button):
        self.settings.set_boolean('is-sorted', False)
        self.settings.reset('operations')

    @Gtk.Template.Callback()
    def on__main_window_destroy(self, w):
        saved_folders = []
        children = self._main_list_box.get_children()
        for child in children:
            saved_folders.append(child.label)
        self.settings.set_value('saved-folders', GLib.Variant('as', saved_folders))

    def on_count_change(self, settings, key, button):
        if self.settings.get_int('count') > 0:
            self._main_label_box.props.visible = False
        else:
            self._main_label_box.props.visible = True
            self._main_list_box.props.visible = False
            self.settings.reset('saved-folders')

    def on_is_sorted_change(self, settings, key, button):
        if self.settings.get_boolean('is-sorted'):
            self._main_revealer.set_reveal_child(True)
        else:
            self._main_revealer.set_reveal_child(False)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        drop_source = GLib.filename_from_uri(data.get_text())
        folder_path = drop_source[0].rstrip()

        try:
            if GLib.file_test(folder_path, GLib.FileTest.IS_DIR):
                self._main_label_box.props.visible = False
                label = folder_path
                folder = FolderBox(label)
                self._main_list_box.props.visible = True
                folder._folder_box_label.set_label(label)
                self._main_list_box.insert(folder, -1)
            else:
                raise GLib.Error(message=f'Error: {folder_path} is not a folder.')
        except GLib.Error as err:
            print('%s' % err.message)
