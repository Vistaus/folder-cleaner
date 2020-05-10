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

from gi.repository import Gio
from .basic_formats import base
from .constants import folder_cleaner_constants as constants

class Formats:

    _formats = base

    def __init__(self):
        self.settings = Gio.Settings.new(constants['main_settings_path'])
        self._user_formats = self.settings.get_value('saved-user-folders').unpack()

    def get_formats(self):
        return self._formats

    def get__user_formats(self):
        return self._user_formats
