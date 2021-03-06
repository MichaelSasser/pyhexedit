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

import gc
import logging
import mmap
import os
from pathlib import Path
from shutil import copyfile

from pyhexedit import systeminfo
from pyhexedit.common import random_string

__all__ = ['FileHandler']


class NotEditableError(Exception):
    pass


class FileHandler(object):
    instances: int = 0

    def __init__(self, file: [Path, str],
                 outputfile: [Path, str] = None,
                 editable: bool = False,
                 filetype: str = "bin",
                 direct_mode: bool = True,
                 auto_inram_mode: bool = True,
                 encoding: str = "utf8",
                 bytes_per_line: int = 16,
                 infile_edit: bool = False) -> None:
        """The FileHandler openes, closes and operates exclusively and directly with the file. That means, that no
        other class or function is dealing with the file. This class is reduced to the basic file operation functions.
        It also handles the file as like as a variable.

        It operates basicly in two modes:

        * **Direct Mode:**
          In direct mode the file is opened permanently due to operation. Nothing is
          cached inside the RAM. This mode is the best option for big files or minimal changes.
          It is also the default mode.
          * Read only:
            Read and seek operations are performed directly in the file. If you want make the file writable later on,
            just call the make_editable methode.
          * Read/Write:
            * With infile edit: Read, write and seek operations are performed directly in the file.
            * Without infile edit: Read, write and seek operations are performed directly in a copy of the original
              file. You need enaugh space on the drive for the copy.
          
        * **RAM Mode:**
          In RAM mode the file will be first cached as a string in RAM. All operation will be performed in RAM.
          After the operations are complete you can save the changes by overwriting the file.
          * Read only:
            Read operations are performed in RAM. If you want make the cached file writable later on,
            just call the make_editable methode.
          * Read/Write:
            Read and write operations are performed in the cached file.

        :param file: The file.
        :type file: str
        :param outputfile: The outputfile, if the changes should be saved to another file.
        :type outputfile: str
        :param editable: Should the file be opened editable? default = False
        :type editable: bool
        :param filetype: The type of the file: bin/intel. default = 'bin'
        :type filetype: str
        :param direct_mode: Should the file be opened in direct mode? (for big files, not cached in RAM)
        :type direct_mode: bool
        :param auto_inram_mode: Should an algorithm choose which mode should be used?
        :type auto_inram_mode: bool
        :param encoding: The encoding of the file. default = 'utf8'
        :type encoding: str
        :param bytes_per_line: The number of bytes per line.
        :type bytes_per_line: int
        :param infile_edit: infile edit for direct mode. If enabled the Read, write and seek operations are
          performed directly in the file.
        :type infile_edit: bool
        :return: None
        :rtype: None
        """
        # ToDo: IntelHex file type
        FileHandler.instances += 1
        self.instance = FileHandler.instances

        # Precheck and cast of file
        self.infile: Path
        if isinstance(file, Path):  # Must be type(file) = Path and not str
            self.infile = file
        else:
            self.infile = Path(file)

        logging.debug(f"Input file: {self.infile.absolute()}")

        # Prechecks input file
        if self.infile.is_dir():
            logging.error("INPUT must be a file, not a directory.")
            raise IOError("INPUT must be a file, not a directory.")
        if not self.infile.exists():
            logging.error("The input file doesn't exists. Please specify an existing input file.")
            raise IOError("The input file doesn't exists. Please specify an existing input file.")

        self.__direct_edit: bool = infile_edit
        self.__editable: bool = editable
        self.unsaved_changes: bool = False

        self.filetype: str = filetype
        self.encoding: str = encoding

        if outputfile:
            if not isinstance(outputfile, Path):  # Must be type(Path()) and not Path
                outputfile: Path = Path(outputfile)

            self.tempfile: Path = outputfile
            self.__tempfile_is_outputfile: bool = True
            self.auto_inram_mode: bool = True  # Not Needed?
            self.__direct_mode: bool = True
            self.__editable = True
            self.__direct_edit: bool = False
        else:
            self.tempfile = self.infile.with_name(
                self.infile.name + f"_{random_string(4)}_.phe") if self.__editable else None
            self.__tempfile_is_outputfile = False

            # Bigfile/auto bigfile
            self.auto_inram_mode = auto_inram_mode
            logging.debug(f"Auto bigfile mode is: {self.auto_inram_mode}")

        self.infile_size: int = os.path.getsize(self.infile)
        try:
            unused_memory: systeminfo.Memory = systeminfo.unused_memory()
        except NotImplementedError as e:
            logging.warning(f"Unused memory check failed: {e}")
            unused_memory = None

        if self.auto_inram_mode:
            if unused_memory:
                # 100MB = 800_000_000 Bits
                self.__direct_mode = True if unused_memory.free - self.infile_size > unused_memory.total / 10 else False
            else:
                # 10MB = 80_000_000 Bits
                self.__direct_mode = True if self.infile_size > 80_000_000 else False
        else:
            if not outputfile:
                self.__direct_mode = direct_mode

        logging.debug(f"Bigfile mode is: {direct_mode}")

        self.bytes_per_line: int = bytes_per_line

        self.infile_obj = None
        self.infile_cached = None

    def __op_open(self) -> None:
        try:
            if not self.__editable:
                self.infile_obj = self.infile.open("rb") if not self.__direct_edit else self.infile.open("r+b")
            else:
                self.infile_obj = self.tempfile.open("r+b")  # NOT "w+b", use "r+b"
        except IOError:
            self.__op_close()
            logging.critical("Something went really wrong. This should never happen. "
                             f"The tempfile is still in \"{self.tempfile.absolute()}\", if it was in use.")
            logging.exception("The input/temp file is not readable. Do you have the right permissions?")

    def open(self) -> None:
        # Open the InFile
        if self.infile_obj is not None:
            self.close()
        if self.__direct_mode:
            try:
                if not self.__editable:
                    self.infile_obj = self.infile.open("rb") if not self.__direct_edit else self.infile.open("r+b")
                else:
                    copyfile(self.infile.absolute(), self.tempfile.absolute())  # There might be an error?
                    self.infile_obj = self.tempfile.open("r+b")  # NOT "w+b", use "r+b"
            except IOError:
                self.close()
                logging.exception("The input file is not readable. Do you have the right permissions?")
        else:
            try:
                self.infile_cached = self.infile.read_bytes()  # ToDo: Editable...
            except IOError:
                logging.exception("The input file is not readable. Do you have the right permissions?")

    def make_editable(self) -> None:
        """The "make_editable()" method makes a file, that is read only editable.

        :return: None
        :rtype: None
        """
        if not self.__editable:
            if self.__direct_mode:
                self.close()
                self.__editable = True  # For future use only in this order
                self.open()
            else:
                self.__editable = True

    def save(self) -> None:
        """The "save()" method saves the changes to the file.

        :return: None
        :rtype: None
        """
        if not self.__editable:
            raise NotEditableError("The file is not editable and can not be saved.")

        if self.__direct_edit:  # ToDo: implement direct mode correctly! (Not here. yfyi...)
            logging.info("Due to direct edit mode, all changes are made directly to the file. Nothing to do...")
            return

        if self.__tempfile_is_outputfile:
            logging.info("Due to output file mode, all changes are made directly to the output file. Nothing to do...")
            return

        if self.unsaved_changes:
            if self.__direct_mode:
                self.__op_close()
                copyfile(self.tempfile.absolute(), self.infile.absolute())
                self.__op_open()
            else:
                self.infile.write_bytes(self.infile_cached)
        else:
            logging.info("No changes made. Nothing to do...")

    def __op_close(self) -> None:
        if self.infile_obj is not None:
            if not self.infile_obj.closed:
                self.infile_obj.close()
                while not self.infile_obj.closed:
                    pass  # Wait until file is closed

    def close(self) -> None:
        try:
            self.__op_close()
            del self.infile_obj  # Will be reinitialized after gc, just to make sure the object will be deleted properly
            del self.infile_cached  # Move...
        except Exception:
            return
        finally:
            try:  # Another Try, just for __del__
                if self.tempfile.exists() and self.__editable and self.__direct_mode and not self.__direct_edit and not self.__tempfile_is_outputfile:
                    os.remove(self.tempfile.absolute())
            except AttributeError:
                pass
            gc.collect()
        self.infile_obj = None
        self.infile_cached = None

    def find(self, value: [str, bytes], start: int = 0, stop: int = -1) -> [int, None]:  # ToDo: Also implement regex
        """The "find" method searches for an occurence of an defined string inside the file.

        :param value: The value to search for.
        :param start: The start point of the search. default = 0 (begin of the file)
        :param stop: The stop point of the search. default = -1 (the end of the file)
        :return: The possition of the occured string
        """
        if type(value) == str:
            value = bytes(value, encoding=self.encoding)
        if self.__direct_mode:
            with mmap.mmap(self.infile_obj.fileno(), 0, access=mmap.ACCESS_READ) as memory_map:
                ret: int = memory_map.find(value, start, stop)
        else:
            ret: int = self.infile_cached.find(value, start, stop)

        if ret != -1:
            return ret
        else:
            return None

    def __len__(self) -> int:
        """Returns the length/size of the file.

        :return: The length/size of the file
        :rtype: None
        """
        if self.__direct_mode:
            if not self.infile_obj.closed:  # Warning, the file might be changed after that.
                self.infile_obj.seek(0, 2)
                return self.infile_obj.tell()
            else:
                return self.infile_size
        else:
            return len(self.infile_cached)

    def __getitem__(self, key: int):  # class slice(start, stop[, step])
        if type(key) == int:
            key: slice = slice(key, None, None)

        if self.__direct_mode:  # ToDo: Implement stepping
            if key.step:
                raise NotImplementedError("Stepping is currently not implemented for Files in bigfile_mode")

            if key.start is None:
                start: int = 0
            else:
                start: int = key.start

            if key.stop is None:
                stop: int = len(self) - start
            else:
                stop: int = key.stop - start

            self.infile_obj.seek(start, 0)
            return self.infile_obj.read(stop)
        else:
            return self.infile_cached.__getitem__(key)

    def __setitem__(self, key, value) -> None:
        if type(key) == int:
            key = slice(key, None, None)

        if not self.__editable:
            raise NotEditableError(
                "You have to add \"editable=True\" to your args or call the \"make_editable\" method, to edit the file.")  # This is by design
        if key.step:
            raise NotImplementedError("Stepping is currently not implemented for Files in bigfile_mode")

        if type(value) == str:
            value: bytes = bytes(value, encoding=self.encoding)

        if key.stop:
            stop: int = key.stop - key.start
            if len(value) != stop:  # Fill Mode (works for both bigfile and not bigfile mode)
                value: int = (value * round((stop / len(value)) + 0.5))[:(stop)]
        else:
            stop: int = len(value)

        if self.__direct_mode:
            self.infile_obj.seek(key.start, 0)
            self.infile_obj.write(value)
        else:
            self.infile_cached = self.infile_cached[:key.start] + value + \
                                 self.infile_cached[(key.start + stop):]  # bytes: just to make sure
        self.unsaved_changes = True

    def __bytes__(self) -> bytes:
        if self.__direct_mode:
            self.infile_obj.seek(0)
            return self.infile_obj.read()
        else:
            return self.infile_cached

    def __str__(self) -> str:
        return str(self.__bytes__().decode(self.encoding))

    def __del__(self) -> None:
        self.close()
        FileHandler.instances -= 1
