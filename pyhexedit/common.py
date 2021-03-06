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


__author__: str = "Michael Sasser"
__email__: str = "Michael@MichaelSasser.de"

import random
import string


def random_string(length: int) -> str:
    """Generates a random string of lowercase ascii characters.

    :param length: Number of characters been generated
    :type length: int
    :return: The random string of lowercase ascii characters
    :rtype: str
    """
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
