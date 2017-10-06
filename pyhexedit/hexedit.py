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

from pathlib import Path

from pyhexedit.filehandler import FileHandler

__all__ = ['PyHexedit']


class PyHexedit(object):  # Don't make this to a child of FileHandler.
    instances: int = 0
    escapes: dict = {n: '.' for n in range(1, 32)}

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
        self.handler: FileHandler = FileHandler(file=file,
                                                outputfile=outputfile,
                                                editable=editable,
                                                filetype=filetype,
                                                direct_mode=bigfile_mode,
                                                auto_inram_mode=auto_bigfile_mode,
                                                encoding=encoding,
                                                bytes_per_line=bytes_per_line,
                                                infile_edit=direct_edit)

        if auto_open:
            self.open()

    def open(self):
        self.handler.open()

    def close(self):
        self.handler.close()

    def save(self):
        self.handler.save()

    def find(self, value: [str, bytes], begin: int = 0, end: int = -1, pprint: bool = False) -> [int, None]:
        found: int = self.handler.find(value, begin, end)
        if pprint:
            self.pprint_around(found)
        return found

    def find_all(self, value: [str, bytes], begin: int = 0, end: int = -1, pprint: bool = False) -> tuple:
        eof: int = end if end != -1 else self.__len__()
        found: list = []
        start_next: int = begin
        while True:
            if start_next > eof:
                break
            hit: int = self.find(value, start_next, end, pprint)
            if hit is None:
                break
            found.append(hit)
            start_next = hit + 1
        return tuple(found)

    def pprint_around(self, address: int, line_above: int = 2, line_below: int = 3, charset: str = "ANSI") -> None:
        if type(address) == int:
            print(f"< Found: at Address: {address:08X} >")
            lines = line_below + line_above
            mid: int = int(address - (address % self.handler.bytes_per_line))  # * self.handler.bytes_per_line
            # print(f"\tMid: {mid:02X}", end='')
            line_above = mid - line_above * self.handler.bytes_per_line if mid - line_above * self.handler.bytes_per_line > 0 else 0
            line_below = mid + line_below * self.handler.bytes_per_line if mid + line_below * self.handler.bytes_per_line < self.handler.__len__() else self.handler.__len__()
            # print(f"\tAbove: {line_above:02X}\tBelow: {line_below:02X}")
            self.pprint(line_above, line_below, lines, charset)
        else:
            # Todo
            pass

    def pprint(self, begin: int = None, end: int = None, lines: int = 16, charset: str = "ANSI") -> None:
        # ToDo: Create a buffer/generator, don't print. The User should print himselfe
        begin: int = int(begin) if begin is not None else 0
        end: int = int(end) if end != -1 else self.handler.__len__()
        empty: int = 0 if begin == 0 else begin % self.handler.bytes_per_line

        headline: str = "Offset(h) | "
        for i in range(self.handler.bytes_per_line):
            headline += f" {i:02X}"
        headline += f"  |  {charset.center(self.handler.bytes_per_line, ' ')}"
        headline += '\n' + '-' * len(headline)

        printed_lines: int = 0
        last_start: int = begin
        run: bool = True
        while run:

            if printed_lines % lines == 0:
                print(headline)
            # address = start + printed_lines
            next_end: int = last_start + self.handler.bytes_per_line - empty
            #print("LAST NEXT END: ", last_start, next_end, end)
            print(f"{last_start:08X}  | " + ' ' * 3 * empty, end='')

            if next_end < end:
                chars: bytes = bytes(self[last_start:next_end])
            elif next_end >= end:
                chars: bytes = bytes(self[last_start:end])
                run = False
            else:
                raise (RuntimeError("This Error should never happen."))
            for char in chars:
                print(f" {char:02X}", end='')
            if run == False:
                print(' ' * 3 * (abs(end - last_start - self.handler.bytes_per_line) - empty), end='')
            print("  |  " + " " * empty, end='')
            for char in chars:
                print(chr(char).translate(PyHexedit.escapes), end='')
            print()  # Just for the Newline

            if printed_lines % lines == lines - 1:  # A line between
                print()

            printed_lines += 1
            last_start = next_end
            empty = 0

    def __getitem__(self, key):
        return self.handler.__getitem__(key)

    def __setitem__(self, key, value) -> None:
        self.handler.__setitem__(key, value)

    def __del__(self) -> None:
        PyHexedit.instances -= 1

    def __bytes__(self) -> bytes:
        return self.handler.__bytes__()

    def __str__(self) -> str:
        return self.handler.__str__()

    def __len__(self) -> int:
        return self.handler.__len__()
