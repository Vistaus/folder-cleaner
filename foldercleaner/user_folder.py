# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from locale import gettext as _
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib

from .constants import folder_cleaner_constants as constants

@Gtk.Template(resource_path = constants['UI_PATH'] + 'user_folder.ui')
class UserFoldersBox(Gtk.ListBox):

    __gtype_name__ = "user_folders_list_box"

    file_extension_button = Gtk.Template.Child()
    user_folder_button = Gtk.Template.Child()
    close_user_folders_button = Gtk.Template.Child()
    file_extension_button_label = Gtk.Template.Child()
    user_folder_button_label = Gtk.Template.Child()

    i = 0

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new(constants['main_settings_path'])
        UserFoldersBox.i += 1
        self.id = UserFoldersBox.i
        self.settings.set_int('count-user-folders', UserFoldersBox.i)

    @Gtk.Template.Callback()
    def on_close_user_folders_button_clicked(self, btn):
        UserFoldersBox.i -= 1
        self.settings.set_int('count-user-folders', UserFoldersBox.i)
        self.get_parent().destroy()

    @Gtk.Template.Callback()
    def on_file_extension_button_popover_entry_changed(self, entry):
        self.file_extension_button_label.props.label = entry.get_text()

    @Gtk.Template.Callback()
    def on_user_folder_button_popover_entry_changed(self, entry):
        self.user_folder_button_label.props.label = entry.get_text()


