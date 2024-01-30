from kicad import pcbnew_bare as pcbnew

import kicad
from kicad.pcbnew import layer as pcbnew_layer
from kicad.point import Point
from kicad import units, SWIGtype
from kicad.pcbnew.item import HasConnection, HasLayerStrImpl, Selectable, BoardItem

class Track(HasConnection, HasLayerStrImpl, Selectable, BoardItem):
    def __init__(self, width, start, end, layer='F.Cu', board=None):
        self._obj = SWIGtype.Track(board and board.native_obj)
        self._obj.SetWidth(int(width * units.DEFAULT_UNIT_IUS))
        self.layer = layer
        self._obj.SetStart(Point.native_from(start))
        self._obj.SetEnd(Point.native_from(end))

    @staticmethod
    def wrap(instance):
        """Wraps a C++ api TRACK object, and returns a `Track`."""
        return kicad.new(Track, instance)

    @property
    def width(self):
        return float(self._obj.GetWidth()) / units.DEFAULT_UNIT_IUS

    @width.setter
    def width(self, value):
        self._obj.SetWidth(int(value * units.DEFAULT_UNIT_IUS))

    @property
    def start(self):
        return Point.wrap(self._obj.GetStart())

    @start.setter
    def start(self, value):
        self._obj.SetStart(Point.native_from(value))

    @property
    def end(self):
        return Point.wrap(self._obj.GetEnd())

    @end.setter
    def end(self, value):
        self._obj.SetEnd(Point.native_from(value))

    def delete(self):
        self._obj.DeleteStructure()
