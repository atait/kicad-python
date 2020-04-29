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
from kicad.pcbnew import layer
from kicad.point import Point
from kicad import units


class Via(object):
    def __init__(self, coord, layer_pair, size, drill, board=None):
        self._via = pcbnew.VIA(board and board.native_obj)
        self._via.SetWidth(int(size * units.DEFAULT_UNIT_IUS))
        coord_point = Point.build_from(coord)
        self._via.SetEnd(coord_point.native_obj)
        self._via.SetStart(coord_point.native_obj)
        if board:
            self._via.SetLayerPair(board.get_layer(layer_pair[0]),
                                   board.get_layer(layer_pair[1]))
        else:
            self._via.SetLayerPair(layer.get_std_layer(layer_pair[0]),
                                   layer.get_std_layer(layer_pair[1]))

        self._via.SetDrill(int(drill * units.DEFAULT_UNIT_IUS))

    @property
    def native_obj(self):
        return self._via
