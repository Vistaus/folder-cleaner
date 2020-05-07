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

from .basic_formats import base

class Formats:

    """
    ['application/x-tar', 'application/zip', 'application/gzip',
            'application/x-bzip2', 'application/x-xz', 'application/x-7z-compressed',
            'application/vnd.ms-cab-compressed', 'application/java-archive',
            'application/x-rar-compressed', 'application/x-gtar', 'application/vnd.rar']
    """

    _formats = base

    _user_formats = {}

    def get_formats(self):
        return self._formats

    def get__user_formats(self):
        return self._user_formats

    def add_user_format(self, f):
        self._user_formats.update(f)
