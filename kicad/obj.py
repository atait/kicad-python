#  Copyright 2015 Miguel Angel Ajo Pelayo <miguelangel@ajo.es>
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
from kicad import SWIGtype
from kicad.pcbnew import board
from kicad.pcbnew import drawing
from kicad.pcbnew import module


_WRAPPERS = {pcbnew.BOARD: board.Board,
             SWIGtype.Shape: drawing.Drawing,
             SWIGtype.Footprint: module.Module,
             SWIGtype.Point: kicad.Point,
             SWIGtype.Size: kicad.Size}


def wrap(instance):
    """Returns a python wrapped object from a swig/C++ one."""
    if type(instance) in _WRAPPERS:
        return _WRAPPERS[type(instance)].wrap(instance)

    raise ValueError("Class with no wrapper: %s" % type(instance))
