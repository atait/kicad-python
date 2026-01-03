"""Track (PCB trace segment) handling for KiCad PCB objects.

This module provides the Track class for representing PCB traces/segments
that connect electrical nets on specific copper layers.

Key features:
- Direct instantiation
- Inherits electrical connection capabilities from HasConnection
- Geohashing for layout comparison
"""

from kigadgets import SWIGtype, Point
from kigadgets.item import HasConnection, HasLayer, HasWidth, Selectable, BoardItem
from kigadgets.units import CoordinateLike
from typing import Optional


class Track(HasConnection, HasLayer, HasWidth, Selectable, BoardItem):
    _wraps_native_cls = SWIGtype.Track

    def __init__(self, start: CoordinateLike, end: CoordinateLike, layer: str = "F.Cu", width: Optional[float] = None, board: Optional['Board'] = None) -> None:
        self._obj = SWIGtype.Track(board and board.native_obj)
        self.start = start
        self.end = end
        if width is None:
            width = self.board.default_width if self.board else 0.2
        self.width = width
        self.layer = layer

    @property
    def start(self) -> Point:
        return Point.wrap(self._obj.GetStart())

    @start.setter
    def start(self, value: CoordinateLike) -> None:
        self._obj.SetStart(Point.native_from(value))

    @property
    def end(self) -> Point:
        return Point.wrap(self._obj.GetEnd())

    @end.setter
    def end(self, value: CoordinateLike) -> None:
        self._obj.SetEnd(Point.native_from(value))

    def delete(self) -> None:
        self._obj.DeleteStructure()

    def geohash(self) -> int:
        hstart = hash(self.start)
        hend = hash(self.end)
        if hstart < hend:
            mine = hstart + hend
        else:
            mine = hend + hstart
        return mine + super().geohash()
