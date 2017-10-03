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

import sys

from pyhexedit._version import __version__, __version_info__

if sys.version_info < (3, 6):
    raise RuntimeError('You need Python 3.6+ for this module.')

__author__ = "Michael Sasser <Michael@MichaelSasser.de>"
__license__ = "GNU General Public License Version 3 (GPLv3)"

#from pyhexedit.hexedit import PyHexedit
#from pyhexedit.filehandler import FileHandler
#from pyhexedit.systeminfo import unused_memory
#from pyhexedit.common import random_string

from .common import *
from .colors import *
from .filehandler import *
from .hexedit import *
from .systeminfo import *


__all__ = (hexedit.__all__,
           filehandler.__all__)