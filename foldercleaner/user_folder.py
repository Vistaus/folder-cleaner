# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from locale import gettext as _
import gi
import re

gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')
from gi.repository import Gtk, Gio, GLib, Handy

from .constants import folder_cleaner_constants as constants

Handy.init()

@Gtk.Template(resource_path=constants['UI_PATH'] + 'user_folder.ui')
class UserFoldersBoxRow(Handy.ActionRow):
    __gtype_name__ = "user_folders_list_box_row"

    change_user_folder_button = Gtk.Template.Child()
    remove_user_folder_button = Gtk.Template.Child()
    user_folder_change_popover = Gtk.Template.Child()
    file_folder_button_popover_entry = Gtk.Template.Child()
    file_extension_button_popover_entry = Gtk.Template.Child()

    def __init__(self, extension=None, folder=None, *args, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new(constants['main_settings_path'])
        self.user_saved_folders = self.settings.get_value('saved-user-folders').unpack()

        self.subtitle = extension if extension else constants['default_extension_name']
        self.title = folder if folder else constants['default_folder_name']
        self.set_title(self.title)  # folder
        self.set_subtitle(self.subtitle)  # extension

    @Gtk.Template.Callback()
    def on_remove_user_folder_button_clicked(self, btn):
        self.destroy()


    # TODO
    # check if two folders are the same

    @Gtk.Template.Callback()
    def on_file_folder_button_popover_entry_changed(self, entry):
        if self.check_entry(entry, self.non_letters_check):
            self.set_title(entry.get_text().strip())  # folder

    @Gtk.Template.Callback()
    def on_file_extension_button_popover_entry_changed(self, entry):
        if self.check_entry(entry, self.non_letters_check):
            self.set_subtitle(entry.get_text().strip())  # extension

    # @Gtk.Template.Callback()
    # def on_close_user_folders_button_clicked(self, btn):
    #     try:
    #         self.user_saved_folders.pop(self.extension, None)
    #         self.settings.set_value('saved-user-folders', GLib.Variant('a{ss}', self.user_saved_folders))
    #     except:
    #         print("Error")
    #     self.get_parent().destroy()        

    def non_letters_check(self, text):
        if text:
            return True if re.match('^[A-Za-z0-9 _]+$', text) else False

    def check_entry(self, e, func):
        text = e.props.text.strip()
        e.props.secondary_icon_name = ''
        if text:
            if not func(text):
                e.props.secondary_icon_name = 'dialog-warning-symbolic'
                return False
            else:
                e.props.secondary_icon_name = ''
                return True
