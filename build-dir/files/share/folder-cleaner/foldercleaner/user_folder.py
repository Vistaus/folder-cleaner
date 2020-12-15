# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from locale import gettext as _
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib

from .constants import folder_cleaner_constants as constants
from .helpers import user_folders


@Gtk.Template(resource_path=constants['UI_PATH'] + 'user_folder.ui')
class UserFoldersBox(Gtk.ListBox):
    __gtype_name__ = "user_folders_list_box"

    file_extension_button = Gtk.Template.Child()
    user_folder_button = Gtk.Template.Child()
    close_user_folders_button = Gtk.Template.Child()
    file_extension_button_label = Gtk.Template.Child()
    user_folder_button_label = Gtk.Template.Child()

    def __init__(self, extension=None, folder=None, *args, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new(constants['main_settings_path'])
        self.user_saved_folders = self.settings.get_value('saved-user-folders').unpack()

        self.extension = extension if extension else constants['default_extension_name']
        self.folder = folder if folder else constants['default_folder_name']

        self.file_extension_button_label.props.label = self.extension
        self.user_folder_button_label.props.label = self.folder

    @Gtk.Template.Callback()
    def on_close_user_folders_button_clicked(self, btn):
        try:
            self.user_saved_folders.pop(self.extension, None)
            self.settings.set_value('saved-user-folders', GLib.Variant('a{ss}', self.user_saved_folders))
        except:
            print("Error")
        self.get_parent().destroy()

    @Gtk.Template.Callback()
    def on_file_extension_button_popover_entry_changed(self, entry):
        self.extension = self.file_extension_button_label.props.label = entry.get_text()

    @Gtk.Template.Callback()
    def on_user_folder_button_popover_entry_changed(self, entry):
        self.folder = self.user_folder_button_label.props.label = entry.get_text()
