import kigadgets
from kigadgets import DEFAULT_UNIT_IUS, SWIGtype, Point
from kigadgets.item import HasConnection, HasLayer, Selectable, BoardItem

class Track(HasConnection, HasLayer, Selectable, BoardItem):
    def __init__(self, start, end, layer='F.Cu', width=None, board=None):
        self._obj = SWIGtype.Track(board and board.native_obj)
        self.start = start
        self.end = end
        if width is None:
            width = self.board.default_width if self.board else 0.2
        self.width = width
        self.layer = layer

    @staticmethod
    def wrap(instance):
        """Wraps a C++ api TRACK object, and returns a `Track`."""
        return kigadgets.new(Track, instance)

    @property
    def width(self):
        return float(self._obj.GetWidth()) / DEFAULT_UNIT_IUS

    @width.setter
    def width(self, value):
        self._obj.SetWidth(int(value * DEFAULT_UNIT_IUS))

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
