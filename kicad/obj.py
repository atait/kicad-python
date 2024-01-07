from kicad import pcbnew_bare

import kicad
from kicad import SWIGtype
from kicad.pcbnew import board
from kicad.pcbnew import drawing
from kicad.pcbnew import module


_WRAPPERS = {pcbnew_bare.BOARD: board.Board,
             SWIGtype.Shape: drawing.Drawing,
             SWIGtype.Footprint: module.Module,
             SWIGtype.Point: kicad.Point,
             SWIGtype.Size: kicad.Size}


def wrap(instance):
    """Returns a python wrapped object from a swig/C++ one."""
    if type(instance) in _WRAPPERS:
        return _WRAPPERS[type(instance)].wrap(instance)

    raise ValueError("Class with no wrapper: %s" % type(instance))
