from kigadgets import DEFAULT_UNIT_IUS, SWIGtype, Point
from kigadgets.item import HasConnection, HasLayer, HasWidth, Selectable, BoardItem


class Track(HasConnection, HasLayer, HasWidth, Selectable, BoardItem):
    _wraps_native_cls = SWIGtype.Track

    def __init__(self, start, end, layer="F.Cu", width=None, board=None):
        self._obj = SWIGtype.Track(board and board.native_obj)
        self.start = start
        self.end = end
        if width is None:
            width = self.board.default_width if self.board else 0.2
        self.width = width
        self.layer = layer

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

    def geohash(self):
        hstart = hash(self.start)
        hend = hash(self.end)
        if hstart < hend:
            mine = hstart + hend
        else:
            mine = hend + hstart
        return mine + super().geohash()
