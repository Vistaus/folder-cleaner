#!/usr/bin/python

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

from .helpers import get_files_and_folders, operations, folders_made, labels
import gi
gi.require_version('GExiv2', '0.10')
from gi.repository import Gio, GLib, GExiv2

ARCHIVES = ['application/x-tar', 'application/zip', 'application/gzip',
            'application/x-bzip2', 'application/x-xz', 'application/x-7z-compressed',
            'application/vnd.ms-cab-compressed', 'application/java-archive',
            'application/x-rar-compressed', 'application/x-gtar', 'application/vnd.rar']

class Sorting():

    def __init__(self, folder):
        self.folder = folder
        self.folders, self.files = get_files_and_folders(self.folder)

    def files_by_content(self):
        for f in self.files:
            try:
                content_type, uncertain = Gio.content_type_guess(f)
                simple_file = Gio.File.new_for_path(f)
                print(content_type)
                if content_type in ARCHIVES:
                    content_type_modified = _('Archives')
                else:
                    content_type_modified = content_type.split('/')[0].capitalize()
                destination_folder = Gio.File.new_for_path(self.folder + '/' + content_type_modified)
                full_path_to_file = destination_folder.get_path() + '/' + simple_file.get_basename()
                destination_for_files = Gio.File.new_for_path(full_path_to_file)

                if destination_folder.get_path() not in self.folders:
                    Gio.File.make_directory(destination_folder)
                    folders_made.append(destination_folder.get_path())
                    simple_file.move(destination_for_files, Gio.FileCopyFlags.NONE)
                    self.folders.append(destination_folder.get_path())
                    operations[f] = full_path_to_file
                else:
                    simple_file.move(destination_for_files, Gio.FileCopyFlags.NONE)
                    operations[f] = full_path_to_file


            except GLib.Error as err:
                print('%s: %s. File: %s, (code: %s)' % (err.domain, err.message, f, err.code))

        return True

    def files_by_extension(self):
        for f in self.files:
            try:
                simple_file = Gio.File.new_for_path(f)
                name, ext = simple_file.get_basename().rsplit('.', 1)
                destination_folder = Gio.File.new_for_path(self.folder + '/' + ext)
                destination_path = destination_folder.get_path() + '/' + simple_file.get_basename()
                destination_for_files = Gio.File.new_for_path(destination_path)

                if ext not in self.folders:
                    Gio.File.make_directory(destination_folder)
                    folders_made.append(destination_folder.get_path())
                    simple_file.move(destination_for_files, Gio.FileCopyFlags.NONE)
                    self.folders.append(ext)
                    operations[f] = destination_path
                else:
                    simple_file.move(destination_for_files, Gio.FileCopyFlags.NONE)
                    operations[f] = destination_path

            except GLib.Error as err:
                print('%s: %s in file: %s, (code: %s)' % (err.domain, err.message, f, err.code))

        return True


    def photos_by_exif(self, exif):
        GExiv2.initialize()
        for f in self.files:
            try:
                photo = GExiv2.Metadata.new()
                photo.open_path(f)

                if photo.has_exif() and photo.has_tag(exif):
                    tag = photo.get_tag_string(exif)

                    #works only with date at the right moment
                    #TODO
                    filedate = tag[:10].replace(':', '')

                    folder_for_photo = self.folder + filedate

                    #Gio.Files
                    photo_file = Gio.File.new_for_path(f)
                    destination_folder = Gio.File.new_for_path(folder_for_photo)
                    destination_for_photo = Gio.File.new_for_path(folder_for_photo + '/' + photo_file.get_basename())

                    if GLib.file_test(folder_for_photo, GLib.FileTest.IS_DIR):
                        photo_file.move(destination_for_photo, Gio.FileCopyFlags.NONE)
                    else:
                        Gio.File.make_directory(destination_folder)
                        photo_file.move(destination_for_photo, Gio.FileCopyFlags.NONE)
                else:
                    print('cannot read data in:', f)
            except GLib.Error as err:
                print('%s: %s in file: %s, (code: %s)' % (err.domain, err.message, f, err.code))

        return True

        
