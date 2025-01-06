from kigadgets import pcbnew_bare as pcbnew

from kigadgets import Size
from kigadgets.item import HasPosition, HasConnection, HasLayer, Selectable, BoardItem


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
    def __init__(self):
        raise NotImplementedError("Direct instantiation of Pad is not supported. See KicadModTree to make new footprints.")

    @property
    def pad_type(self):
        return self._obj.GetAttribute()

    @pad_type.setter
    def pad_type(self, value):
        """Value should be integer that can be found by referencing PadType.Through"""
        self._obj.SetAttribute(value)

    @property
    def drill_shape(self):
        return self._obj.GetDrillShape()

    @drill_shape.setter
    def drill_shape(self, value):
        """Value should be integer that can be found by referencing DrillShape.Circle"""
        self._obj.SetDrillShape(value)

    @property
    def drill(self):
        """Drill size. Returns `Size`."""
        return Size.wrap(self._obj.GetDrillSize())

    @drill.setter
    def drill(self, value):
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
    def shape(self):
        return self._obj.GetShape()

    @shape.setter
    def shape(self, value):
        """Value should be integer that can be found by referencing PadShape.Circle"""
        self._obj.SetShape(value)

    @property
    def size(self):
        return Size.wrap(self._obj.GetSize())

    @size.setter
    def size(self, value):
        try:
            size = Size.build_from(value)
            # self.drill_shape = DrillShape.Oval
        except TypeError:
            size = Size.build_from((value, value))
            # self.drill_shape = DrillShape.Circle
        self._obj.SetSize(size.native_obj)

    @property
    def name(self):
        return self._obj.GetName()

    @name.setter
    def name(self, value):
        self._obj.SetName(value)

    def geohash(self):
        mine = hash((
            self.pad_type,
            self.drill_shape,
            self.drill,
            self.shape,
            self.size,
        ))
        return mine + super().geohash()
