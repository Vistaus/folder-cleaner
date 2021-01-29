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

from .helpers import get_files_and_folders
from .constants import folder_cleaner_constants as constants
from .basic_formats import base
from locale import gettext as _
import gi

gi.require_version('GExiv2', '0.10')
from gi.repository import Gio, GLib, GExiv2


class Sorting():

    def __init__(self, base_folder):
        self.settings = Gio.Settings.new(constants['main_settings_path'])
        self.folders_made = self.settings.get_value('folders-made').unpack()
        self.operations = self.settings.get_value('operations').unpack()
        self.base_folder = base_folder

    def files_by_content(self):
        folders, files = get_files_and_folders(self.base_folder)
        extensions = base
        user_extensions = self.settings.get_value('saved-user-folders').unpack()
        no_error = True
        for f in files:
            try:
                # content_type, uncertain = Gio.content_type_guess(f)
                simple_file = Gio.File.new_for_path(f)
                try:
                    name, ext = simple_file.get_basename().rsplit('.', 1)
                except ValueError:
                    ext = ""

                content_type = _("Unsorted")

                if user_extensions:
                    for k, v in user_extensions.items():
                        if ext == k:
                            content_type = v.capitalize()
                        else:
                            # TODO
                            # REWRITE
                            for key, value in extensions.items():
                                if ext == key:
                                    content_type = value.capitalize()
                else:
                    # TODO
                    # REWRITE
                    for k, v in extensions.items():
                        if ext == k:
                            content_type = v.capitalize()

                destination_folder = Gio.File.new_for_path(GLib.build_pathv(GLib.DIR_SEPARATOR_S,
                                                                            [self.base_folder, content_type]))
                full_path_to_file = GLib.build_pathv(GLib.DIR_SEPARATOR_S, [destination_folder.get_path(),
                                                                            simple_file.get_basename()])
                destination_for_files = Gio.File.new_for_path(full_path_to_file)

                if destination_folder.get_path() not in folders:
                    Gio.File.make_directory(destination_folder)
                    self.folders_made.append(destination_folder.get_path())
                    simple_file.move(destination_for_files, Gio.FileCopyFlags.NONE)
                    folders.append(destination_folder.get_path())
                    self.operations[f] = full_path_to_file
                else:
                    simple_file.move(destination_for_files, Gio.FileCopyFlags.NONE)
                    self.operations[f] = full_path_to_file

            except GLib.Error as err:
                print('%s: %s. File: %s, (code: %s)' % (err.domain, err.message, f, err.code))

        self.settings.set_value('folders-made', GLib.Variant('as', self.folders_made))
        self.settings.set_value('operations', GLib.Variant('a{ss}', self.operations))
        return no_error

    def files_by_extension(self):
        folders, files = get_files_and_folders(self.base_folder)
        no_error = True
        for f in files:
            try:
                simple_file = Gio.File.new_for_path(f)
                name, ext = simple_file.get_basename().rsplit('.', 1)
                destination_folder = Gio.File.new_for_path(GLib.build_pathv(GLib.DIR_SEPARATOR_S,
                                                                            [self.base_folder, ext]))
                destination_path = GLib.build_pathv(GLib.DIR_SEPARATOR_S, [destination_folder.get_path(),
                                                                           simple_file.get_basename()])
                destination_for_files = Gio.File.new_for_path(destination_path)

                if ext not in folders:
                    Gio.File.make_directory(destination_folder)
                    self.folders_made.append(destination_folder.get_path())
                    simple_file.move(destination_for_files, Gio.FileCopyFlags.NONE)
                    folders.append(ext)
                    self.operations[f] = destination_path
                else:
                    simple_file.move(destination_for_files, Gio.FileCopyFlags.NONE)
                    self.operations[f] = destination_path

            except GLib.Error as err:
                print('%s: %s in file: %s, (code: %s)' % (err.domain, err.message, f, err.code))

        self.settings.set_value('folders-made', GLib.Variant('as', self.folders_made))
        self.settings.set_value('operations', GLib.Variant('a{ss}', self.operations))
        return no_error

    def photos_by_exif(self, exif):
        folders, files = get_files_and_folders(self.base_folder)
        GExiv2.initialize()
        no_error = True
        for f in files:
            try:
                photo = GExiv2.Metadata.new()
                photo.open_path(f)

                if photo.has_exif() and photo.has_tag(exif):
                    tag = photo.get_tag_string(exif)

                    # works only with date at the right moment
                    # TODO
                    filedate = tag[:10].replace(':', '')

                    folder_for_photo = GLib.build_pathv(GLib.DIR_SEPARATOR_S, [self.base_folder, filedate])

                    # Gio.Files
                    photo_file = Gio.File.new_for_path(f)
                    destination_folder = Gio.File.new_for_path(folder_for_photo)
                    destination_path = GLib.build_pathv(GLib.DIR_SEPARATOR_S, [folder_for_photo,
                                                                               photo_file.get_basename()])
                    destination_for_photo = Gio.File.new_for_path(destination_path)

                    if filedate not in folders:
                        Gio.File.make_directory(destination_folder)
                        self.folders_made.append(destination_folder.get_path())
                        photo_file.move(destination_for_photo, Gio.FileCopyFlags.NONE)
                        folders.append(filedate)
                        self.operations[f] = destination_path
                    else:
                        photo_file.move(destination_for_photo, Gio.FileCopyFlags.NONE)
                        self.operations[f] = destination_path
                else:
                    print('cannot read data in:', f)
            except GLib.Error as err:
                print('%s: %s in file: %s, (code: %s)' % (err.domain, err.message, f, err.code))

        self.settings.set_value('folders-made', GLib.Variant('as', self.folders_made))
        self.settings.set_value('operations', GLib.Variant('a{ss}', self.operations))
        return no_error
