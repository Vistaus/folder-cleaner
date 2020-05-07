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

class Sorting():

    def __init__(self, folder):
        self.folder = folder

    def sort_files_by_content(self):
        pass

    def sort_files_by_extension(self):
        pass

    def sort_photos_by_exif(self, exif):
        GExiv2.initialize()
        folders, files = get_files_and_folders(self.folder)
        for f in files:
            try:
                photo = GExiv2.Metadata.new()
                photo.open_path(f)

                if photo.has_exif() and photo.has_tag('Exif.Image.DateTime'):
                    tag = photo.get_tag_string('Exif.Image.DateTime')

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

        
