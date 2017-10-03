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


from pyhexedit.hexedit import PyHexedit


def main(*args, **kwargs):
    import argparse

    # Argparser
    parser = argparse.ArgumentParser(prog='pyhexedit',
                                     description="%(prog)s provides you the ability to view, convert, edit and "
                                                 "manipulate Binary files and Intel Hex files.")
    parser.add_argument("input", help="The input file.", type=str)
    parser.add_argument("-o", "--output", help="The output file.", type=str, default=None)
    parser.add_argument("-s", "--start", help="start", default=None)
    parser.add_argument("-e", "--end", help="end", default=None)
    parser.add_argument("-p", "--pprint", help="pretty-print", action="store_true")
    parser.add_argument("-l", "--lines", help="lines to pprint before next headline", type=int, default=16)
    parser.add_argument("-f", "--force", help="Overwrites the output file.", action="store_true")
    parser.add_argument("-E", "--edit", help="Safe edit.", action="store_true")
    parser.add_argument("-b", "--bytes", help="bytes per line", type=int, default=16)
    parser.add_argument("--bigfile-mode", help="Enables bigfile mode", action="store_true")
    parser.add_argument("--no_auto_bigfile-mode", help="Disables auto bigfile mode", action="store_false")

    parser.add_argument("--encoding", help="String encoding. Default: \"utf8\"", type=str, default="utf8")

    parser.add_argument("--verbose", help="Verbose display output.", action="store_true")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    args = parser.parse_args()

    he = PyHexedit(args.input, bytes_per_line=args.bytes, outputfile=args.output, encoding=args.encoding, auto_bigfile_mode=args.no_auto_bigfile_mode, bigfile_mode=args.bigfile_mode, editable=args.edit)
    #he = PyHexedit(args.input, outputfile=args.output, encoding=args.encoding, auto_bigfile_mode=False, bigfile_mode=True, editable=True)
    #print(bytes(he))
    #he[20] = "Hello World"
    #print(bytes(he))
    #print("Search:", he.find("1", 0, 0x2))
    start:[int, hex] = args.start if args.start is not None else 0
    end:[int, hex] = args.end if args.end is not None else len(he)
    empty:int = 0 if int(start) == 0 else int(start) % int(args.bytes)

    #escapes = ''.join([chr(char) for char in range(1, 32)])
    escapes = {n: '.' for n in range(1, 32)}

    #temp
    charset = "ANSI"

    if args.pprint:
        __headline = "Offset(h) | "
        for i in range(args.bytes):
            __headline += f" {i:02X}"
        __headline += f"  |  {charset.center(args.bytes, ' ')}"
        __headline += '\n' + '-' * len(__headline)

        printed_lines = 0
        last_start = start
        run = True
        while run:

            if printed_lines % args.lines == 0:
                print()
                print(__headline)
            #address = start + printed_lines
            next_end = last_start + args.bytes
            print(f"{last_start:08X}  | " + ' ' * 3 * empty, end='')
            empty = 0
            if next_end < end:
                chars = bytes(he[last_start:next_end])
            elif next_end >= end:
                chars = bytes(he[last_start:end])
                run = False
            else:
                raise(RuntimeError("This Error should never happen."))
            for char in chars:
                print(f" {char:02X}", end='')
            if run == False:
                print(' ' * 3 * abs(int(end) - int(last_start) - args.bytes), end='')
            print("  |  ", end='')
            for char in chars:
                print(chr(char).translate(escapes), end='')
            print()

            printed_lines += 1
            last_start = next_end


if __name__ == '__main__':
    from pyhexedit.colors import colorize

    colorize()
    main()
