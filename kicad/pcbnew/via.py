#  Copyright 2014 Piers Titus van der Torren <pierstitus@gmail.com>
#  Copyright 2015 Miguel Angel Ajo <miguelangel@ajo.es>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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
from kicad import pcbnew_bare as pcbnew

import kicad
from kicad.pcbnew import layer as pcbnew_layer
from kicad.point import Point
from kicad import units
from kicad.pcbnew.item import HasPosition, HasConnection, Selectable

class Via(HasPosition, HasConnection, Selectable):
    def __init__(self, coord, layer_pair, diameter, drill, board=None):
        self._obj = pcbnew.VIA(board and board.native_obj)
        self.diameter = diameter
        coord_point = Point.build_from(coord)
        self._obj.SetEnd(coord_point.native_obj)
        self._obj.SetStart(coord_point.native_obj)
        if board:
            self._obj.SetLayerPair(board.get_layer(layer_pair[0]),
                                   board.get_layer(layer_pair[1]))
        else:
            self._obj.SetLayerPair(pcbnew_layer.get_std_layer(layer_pair[0]),
                                   pcbnew_layer.get_std_layer(layer_pair[1]))

        self.drill = drill

    @property
    def native_obj(self):
        return self._obj

    @staticmethod
    def wrap(instance):
        """Wraps a C++ api VIA object, and returns a `Via`."""
        return kicad.new(Via, instance)

    @property
    def drill(self):
        """Via drill diameter"""
        return float(self._obj.GetDrill()) / units.DEFAULT_UNIT_IUS

    @drill.setter
    def drill(self, value):
        self._obj.SetDrill(int(value * units.DEFAULT_UNIT_IUS))

    @property
    def diameter(self):
        """Via diameter"""
        return float(self._obj.GetWidth()) / units.DEFAULT_UNIT_IUS

    @diameter.setter
    def diameter(self, value):
        self._obj.SetWidth(int(value * units.DEFAULT_UNIT_IUS))

    @property
    def center(self):
        """Via center"""
        return Point.wrap(self._obj.GetCenter())

    # @center.setter
    # def center(self, value):
    #     self._obj.SetCenter(int(value * units.DEFAULT_UNIT_IUS))

    @property
    def top_layer(self):
        brd = self._obj.GetBoard()
        if brd:
            return brd.GetLayerName(self._obj.TopLayer())
        else:
            return pcbnew_layer.get_std_layer_name(self._obj.TopLayer())

    @top_layer.setter
    def top_layer(self, value):
        brd = self._obj.GetBoard()
        if brd:
            self._obj.SetTopLayer(brd.GetLayerID(value))
        else:
            self._obj.SetTopLayer(pcbnew_layer.get_std_layer(value))

    @property
    def bottom_layer(self):
        brd = self._obj.GetBoard()
        if brd:
            return brd.GetLayerName(self._obj.BottomLayer())
        else:
            return pcbnew_layer.get_std_layer_name(self._obj.BottomLayer())

    @bottom_layer.setter
    def bottom_layer(self, value):
        brd = self._obj.GetBoard()
        if brd:
            self._obj.SetTopLayer(brd.GetLayerID(value))
        else:
            self._obj.SetTopLayer(pcbnew_layer.get_std_layer(value))

    @property
    def is_through(self):
        return self._obj.GetViaType() == pcbnew.VIA_THROUGH
        # self._obj.GetViaType() in [pcbnew.VIA_MICROVIA, pcbnew.VIA_BLIND_BURIED]
