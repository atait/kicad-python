# -*- coding: utf-8 -*-
#
#  Copyright 2018 Hasan Yavuz Özderya
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

from math import radians, degrees
from kicad.point import Point
from kicad.pcbnew.layer import Layer

class HasPosition(object):
    """Board items that has valid position property should inherit
    this."""

    def __init__(self):
        raise NotImplementedError("This is an abstract class!")

    @property
    def position(self):
        return Point.wrap(self._obj.GetPosition())

    @position.setter
    def position(self, value):
        self._obj.SetPosition(Point.native_from(value))

    @property
    def x(self):
        return self.position.x

    @x.setter
    def x(self, value):
        self.position = (value, self.y)

    @property
    def y(self):
        return self.position.y

    @y.setter
    def y(self, value):
        self.position = (self.x, value)

class HasRotation(object):
    """Board items that has rotation property should inherit this."""
    def __init__(self):
        raise NotImplementedError("This is an abstract class!")

    @property
    def rotation(self):
        """Rotation of the item in radians."""
        return radians(self._obj.GetOrientation() / 10.)

    @rotation.setter
    def rotation(self, value):
        self._obj.SetOrientation(degrees(value) * 10.)

class HasLayer(object):
    """Board items that has layer should inherit this."""
    def __init__(self):
        raise NotImplementedError("This is an abstract class!")

    @property
    def layer(self):
        return Layer(self._obj.GetLayer())

    @layer.setter
    def layer(self, value):
        self._obj.SetLayer(value.value)

class HasConnection(object):
    """All BOARD_CONNECTED_ITEMs should inherit this."""
    def __init__(self):
        raise NotImplementedError("This is an abstract class!")

    @property
    def netName(self):
        return self._obj.GetNetname()

    @netName.setter
    def netName(self, value):
        """ Takes a name and attempts to look it up based on the containing board """
        if not self._obj:
            raise TypeError("Cannot set netName without a containing Board.")
        try:
            new_code = self._obj.GetBoard().GetNetcodeFromNetname(value)
        except IndexError:
            raise KeyError("Net name '{}' not found in board nets.".format(value))
        self._obj.SetNetCode(new_code)

    @property
    def netCode(self):
        return self._obj.GetNetCode()

    @netCode.setter
    def netCode(self, value):
        self._obj.SetNetCode(value)



