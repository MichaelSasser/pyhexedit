#!/usr/bin/env python
# pyhexedit
# Copyright (C) 2017  Michael Sasser <Michael@MichaelSasser.de>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


__author__ = "Michael Sasser"
__email__ = "Michael@MichaelSasser.de"


import logging

from pathlib import Path
from pyhexedit.filehandler import FileHandler


__all__ = ['PyHexedit']


class PyHexedit(object):  # Don't make this to a child of filehandler.
    instances = 0

    def __init__(self, file: [Path, str],
                 outputfile: [Path, str] = None,
                 editable: bool = False,
                 filetype: str = "bin",
                 auto_open: bool = True,
                 bigfile_mode: bool = True,
                 auto_bigfile_mode: bool = False,
                 encoding: str = "utf8",
                 bytes_per_line: int = 16,
                 direct_edit: bool = False) -> None:
        PyHexedit.instances += 1
        self.handler = FileHandler(file=file,
                                   outputfile=outputfile,
                                   editable=editable,
                                   filetype=filetype,
                                   bigfile_mode=bigfile_mode,
                                   auto_bigfile_mode=auto_bigfile_mode,
                                   encoding=encoding,
                                   bytes_per_line=bytes_per_line,
                                   direct_edit=direct_edit)

        if auto_open:
            self.open()

    def open(self):
        self.handler.open()

    def close(self):
        self.handler.close()

    def save(self):
        self.handler.save()

    def find(self, value, start, stop):
        return self.handler.find(value, start, stop)

    def __getitem__(self, key):
        return self.handler.__getitem__(key)

    def __setitem__(self, key, value):
        self.handler.__setitem__(key, value)

    def __del__(self):
        PyHexedit.instances -= 1

    def __bytes__(self):
        return self.handler.__bytes__()

    def __str__(self):
        return self.handler.__str__()

    def __len__(self):
        return self.handler.__len__()


if __name__ == '__main__':
    from pyhexedit.colors import colorize

    colorize()
