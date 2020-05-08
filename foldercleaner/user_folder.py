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

    i = 0

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new(constants['main_settings_path'])
        UserFoldersBox.i += 1

