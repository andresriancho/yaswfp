# Copyright 2013-2014 Facundo Batista
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  http://github.com/facundobatista/yaswfp

"""Some helpers for the SWF parser."""

import itertools
import struct


def grouper(n, iterable, fillvalue=None):
    """Collect data into fixed-length chunks or blocks.

    This is taken from the itertools docs.
    """
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def unpack_si16(src):
    """Read and unpack signed integer 16b."""
    return struct.unpack("<h", src.read(2))[0]


def unpack_ui8(src):
    """Read and unpack unsigned integer 8b."""
    return struct.unpack("<B", src.read(1))[0]


def unpack_ui16(src):
    """Read and unpack unsigned integer 16b."""
    return struct.unpack("<H", src.read(2))[0]


def unpack_ui32(src):
    """Read and unpack unsigned integer 32b."""
    return struct.unpack("<I", src.read(4))[0]


class BitConsumer:
    """Get a byte source, yield bunch of bits."""
    def __init__(self, src):
        self.src = src
        self._bits = None
        self._count = 0

    def u_get(self, quant):
        """Return a number using the given quantity of unsigned bits."""
        if not quant:
            return
        bits = []
        while quant:
            if self._count == 0:
                byte = self.src.read(1)
                number = struct.unpack("<B", byte)[0]
                self._bits = bin(number)[2:].zfill(8)
                self._count = 8
            if quant > self._count:
                self._count, quant, toget = 0, quant - self._count, self._count
            else:
                self._count, quant, toget = self._count - quant, 0, quant
            read, self._bits = self._bits[:toget], self._bits[toget:]
            bits.append(read)
        data = int("".join(bits), 2)
        return data

    def s_get(self, quant):
        """Return a number using the given quantity of signed bits."""
        sign = self.u_get(1)
        raw_number = self.u_get(quant - 1)
        if sign == 0:
            # positive, simplest case
            number = raw_number
        else:
            # negative, complemento a 2
            complement = 2 ** (quant - 1) - 1
            number = -1 * ((raw_number ^ complement) + 1)
        return number
