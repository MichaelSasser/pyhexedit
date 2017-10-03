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
    parser.add_argument("-r", "--raw", help="raw-print", action="store_true")
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
    print("Search:", he.find_all("Test", 0, 0xE0))


    if not args.raw:
        he.pprint(args.start, args.end, args.lines)

if __name__ == '__main__':
    from pyhexedit.colors import colorize

    colorize()
    main()
