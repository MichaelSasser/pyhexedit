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


import platform
if platform.system() == 'Windows':
    import ctypes


def unused_memory():
    """
    Get node total memory and memory usage
    """
    if platform.system() == 'Windows':
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

            def __init__(self):
                self.dwLength = ctypes.sizeof(self)
                super(MEMORYSTATUSEX, self).__init__()

        stat = MEMORYSTATUSEX()
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

        return stat.ullAvailPhys  # Free physical memory in bits

    try:
        with open('/proc/meminfo', 'r') as mem:
            ret = {}
            tmp = 0
            for i in mem:
                sline = i.split()
                if str(sline[0]) == 'MemTotal:':
                    ret['total'] = int(sline[1])
                elif str(sline[0]) in ('MemFree:', 'Buffers:', 'Cached:'):
                    tmp += int(sline[1])
            ret['free'] = tmp
            ret['used'] = int(ret['total']) - int(ret['free'])
        return ret
    except:
        raise NotImplementedError("I was not able to detect the free physical memory of your OS."
                                  "\"auto_bigfile_mode\" is now using constant values to compensate this issue."
                                  "You can determinate the bigfile_mode by setting \"bigfile_mode: bool\" to True"
                                  "or to False.")
