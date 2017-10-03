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
    escapes = {n: '.' for n in range(1, 32)}

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

    def find(self, value: [str, bytes], start: int = 0, stop: int = -1) -> [int, None]:
        return self.handler.find(value, start, stop)

    def find_all(self, value: [str, bytes], start: int = 0, stop: int = -1) -> tuple:
        eof = stop if stop != -1 else self.__len__()
        found = []
        start_next = start
        while True:
            if start_next > eof:
                break
            hit = self.find(value, start_next, stop)
            if hit is None:
                break
            found.append(hit)
            start_next = hit + 1
        return tuple(found)

    def pprint(self, begin:int=None, end:int=None, lines:int=16, charset:str="ANSI"):
        # ToDo: Create a buffer/generator, don't print. The User should print himselfe
        begin: int = int(begin) if begin is not None else 0
        end: int = int(end) if end is not None else len(self)
        empty: int = 0 if begin == 0 else begin % self.__len__()

        headline = "Offset(h) | "
        for i in range(self.handler.bytes_per_line):
            headline += f" {i:02X}"
        headline += f"  |  {charset.center(self.handler.bytes_per_line, ' ')}"
        headline += '\n' + '-' * len(headline)

        printed_lines = 0
        last_start = begin
        run = True
        while run:

            if printed_lines % lines == 0:
                print()
                print(headline)
            #address = start + printed_lines
            next_end = last_start + self.handler.bytes_per_line - empty
            #print("LAST NEXT END: ", last_start, next_end, end)
            print(f"{last_start:08X}  | " + ' ' * 3 * empty, end='')

            if next_end < end:
                chars = bytes(self[last_start:next_end])
            elif next_end >= end:
                chars = bytes(self[last_start:end])
                run = False
            else:
                raise(RuntimeError("This Error should never happen."))
            for char in chars:
                print(f" {char:02X}", end='')
            if run == False:

                print(' ' * 3 * (abs(end - last_start - self.handler.bytes_per_line) - empty), end='')
            print("  |  " + " " * empty, end='')
            for char in chars:
                print(chr(char).translate(PyHexedit.escapes), end='')
            print()

            printed_lines += 1
            last_start = next_end
            empty = 0

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
