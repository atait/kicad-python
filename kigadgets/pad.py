"""Pad handling for KiCad PCB footprint components.

This module provides classes for representing PCB pads within footprints,
including pad shapes, drill types, and electrical connection properties.

Direct instantiation of Pad is not supported because all pads are part of a footprint.
- Access pre-existing pads through `Footprint.pads` property
- Create new footprint designs using the KicadModTree, not kigadgets
"""

from kigadgets import pcbnew_bare as pcbnew

from kigadgets import Size
from kigadgets.item import HasPosition, HasConnection, HasLayer, Selectable, BoardItem
from typing import Union, Tuple


class DrillShape:
    Circle = pcbnew.PAD_DRILL_SHAPE_CIRCLE
    Oval = pcbnew.PAD_DRILL_SHAPE_OBLONG


class PadShape:
    Circle = pcbnew.PAD_SHAPE_CIRCLE
    Oval = pcbnew.PAD_SHAPE_OVAL
    Rectangle = pcbnew.PAD_SHAPE_RECT
    RoundedRectangle = pcbnew.PAD_SHAPE_ROUNDRECT
    Trapezoid = pcbnew.PAD_SHAPE_TRAPEZOID
    Chamfered = pcbnew.PAD_SHAPE_CHAMFERED_RECT
    Custom = pcbnew.PAD_SHAPE_CUSTOM


class PadType:
    Through = pcbnew.PAD_ATTRIB_PTH
    SMD = pcbnew.PAD_ATTRIB_SMD
    Connector = pcbnew.PAD_ATTRIB_CONN
    NPTH = pcbnew.PAD_ATTRIB_NPTH


class Pad(HasPosition, HasConnection, HasLayer, Selectable, BoardItem):
    def __init__(self) -> None:
        raise NotImplementedError("Direct instantiation of Pad is not supported. See KicadModTree to make new footprints.")

    @property
    def pad_type(self) -> int:
        return self._obj.GetAttribute()

    @pad_type.setter
    def pad_type(self, value: int) -> None:
        """Value should be integer that can be found by referencing PadType.Through"""
        self._obj.SetAttribute(value)

    @property
    def drill_shape(self) -> int:
        return self._obj.GetDrillShape()

    @drill_shape.setter
    def drill_shape(self, value: int) -> None:
        """Value should be integer that can be found by referencing DrillShape.Circle"""
        self._obj.SetDrillShape(value)

    @property
    def drill(self) -> Size:
        """Drill size. Returns `Size`."""
        return Size.wrap(self._obj.GetDrillSize())

    @drill.setter
    def drill(self, value: Union[Size, Tuple[float, float], float]) -> None:
        """Sets the drill size. If value is a single float or int, pad drill
        shape is set to circle, if input is a tuple of (x, y) drill
        shape is set to oval."""
        try:
            size = Size.build_from(value)
            self.drill_shape = DrillShape.Oval
        except TypeError:
            size = Size.build_from((value, value))
            self.drill_shape = DrillShape.Circle
        self._obj.SetDrillSize(size.native_obj)

    @property
    def shape(self) -> int:
        return self._obj.GetShape()

    @shape.setter
    def shape(self, value: int) -> None:
        """Value should be integer that can be found by referencing PadShape.Circle"""
        self._obj.SetShape(value)

    @property
    def size(self) -> Size:
        return Size.wrap(self._obj.GetSize())

    @size.setter
    def size(self, value: Union[Size, Tuple[float, float], float]) -> None:
        try:
            size = Size.build_from(value)
            # self.drill_shape = DrillShape.Oval
        except TypeError:
            size = Size.build_from((value, value))
            # self.drill_shape = DrillShape.Circle
        self._obj.SetSize(size.native_obj)

    @property
    def name(self) -> str:
        return self._obj.GetName()

    @name.setter
    def name(self, value: str) -> None:
        self._obj.SetName(value)

    def geohash(self) -> int:
        mine = hash((
            self.pad_type,
            self.drill_shape,
            self.drill,
            self.shape,
            self.size,
        ))
        return mine + super().geohash()
