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


class HasLayerEnumImpl(object):
    """Board items that has layer should inherit this."""
    def __init__(self):
        raise NotImplementedError("This is an abstract class!")

    @property
    def layer(self):
        return Layer(self._obj.GetLayer())

    @layer.setter
    def layer(self, value):
        self._obj.SetLayer(value.value)


class HasLayer(HasLayerEnumImpl):
    _has_warned = False

    def print_warning(self):
        if not self._has_warned:
            print('\nDeprecation warning (HasLayer): Use either HasLayerEnumImpl or HasLayerStrImpl.'
                  '\nDefault will change from Enum to Str in the future.')
            self._has_warned = True

    @property
    def layer(self):
        self.print_warning()
        return Layer(self._obj.GetLayer())

    @layer.setter
    def layer(self, value):
        self.print_warning()
        self._obj.SetLayer(value.value)


class HasLayerStrImpl(object):
    """ Board items that has layer outside of standard layers should inherit this.
        String implementation can sometimes be more intuitive, and accomodates custom layer names.
        If the layer is not present, it will be caught at runtime, rather than disallowed.
    """
    def __init__(self):
        raise NotImplementedError("This is an abstract class!")

    @property
    def layer(self):
        brd = self._obj.GetBoard()
        if brd:
            return brd.GetLayerName(self._obj.GetLayer())
        else:
            return pcbnew_layer.get_std_layer_name(self._obj.GetLayer())

    @layer.setter
    def layer(self, value):
        brd = self._obj.GetBoard()
        if brd:
            self._obj.SetLayer(brd.GetLayerID(value))
        else:
            self._obj.SetLayer(pcbnew_layer.get_std_layer(value))


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


class Selectable(object):
    """ This influences the main window. Make sure to pcbnew.Refresh() to see it """
    def __init__(self):
        raise NotImplementedError("This is an abstract class!")

    def is_selected(self):
        return bool(self._obj.IsSelected())

    def select(self, value=True):
        """ Selecting changes the appearance and also plays a role in determining
            what will be the subject of a subsequent command (delete, move to layer, etc.)
        """
        if value:
            self._obj.SetSelected()
        else:
            self._obj.ClearSelected()

    def deselect(self):
        self.select(False)

    def brighten(self, value=True):
        """ Brightening gives a bright green appearance """
        if value:
            self._obj.SetBrightened()
        else:
            self._obj.ClearBrightened()






