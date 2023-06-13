"""Drawing shape handling module for KiCad PCB objects.

This module provides pythonic wrappers for KiCad's native drawing shapes.
Each shape class (Segment, Circle, Arc, Rectangle, Polygon)
- inherits from Drawing base class
- wraps a pcbnew.Shape native object

There are two ways to instantiate a Drawing:
- Pre-existing SWIG objects are wrapped using a factory pattern for type detection
- New Drawings can be instantiated directly using __init__ methods

All objects support geohashing for geometric comparison and testing capabilities.
"""

from kigadgets import pcbnew_bare as pcbnew
from typing import Union, Optional, Any, List, Tuple

import cmath
import math

from kigadgets import units, Size, SWIGtype, SWIG_version, Point, instanceof
from kigadgets.layer import get_board_layer_id, get_std_layer_name
from kigadgets.item import HasLayer, Selectable, HasPosition, HasWidth, BoardItem, TextEsque
from kigadgets.units import CoordinateLike

class ShapeType:
    Segment = pcbnew.S_SEGMENT
    Circle = pcbnew.S_CIRCLE
    Arc = pcbnew.S_ARC
    Polygon = pcbnew.S_POLYGON
    Rect = pcbnew.S_RECT


def wrap_drawing(instance: Any) -> Union['Segment', 'Circle', 'Arc', 'Rectangle', 'Polygon', 'TextPCB']:
    """Handles anything found in BOARD.GetDrawings
    Feeds through to shape wrap methods based on the type of shape.

    It also detects and feeds through text, which are handled separately from geometric shapes.
    """
    if instanceof(instance, SWIGtype.Text):
        return TextPCB.wrap(instance)
    if not instanceof(instance, SWIGtype.Shape):
        raise TypeError(f"Invalid drawing class: {type(instance)}")

    obj_shape = instance.GetShape()
    if obj_shape == ShapeType.Segment:
        return Segment.wrap(instance)
    if obj_shape == ShapeType.Circle:
        return Circle.wrap(instance)
    if obj_shape == ShapeType.Arc:
        return Arc.wrap(instance)
    if obj_shape == ShapeType.Polygon:
        return Polygon.wrap(instance)
    if obj_shape == ShapeType.Rect:
        return Rectangle.wrap(instance)

    # Time to fail
    layer = get_std_layer_name(instance.GetLayer())
    unsupported = ["S_CURVE", "S_LAST"]
    for unsup in unsupported:
        if not hasattr(pcbnew, unsup):
            continue
        if obj_shape is getattr(pcbnew, unsup):
            raise TypeError(f"Unsupported shape type: pcbnew.{unsup} on layer {layer}.")
    raise TypeError(f"Unrecognized shape type on layer {layer}")


class Drawing(HasLayer, HasPosition, HasWidth, Selectable, BoardItem):
    """Base class of shape drawings, not including text"""
    _wraps_native_cls = SWIGtype.Shape


class Segment(Drawing):
    def __init__(self, start: CoordinateLike, end: CoordinateLike, layer: str = "F.SilkS", width: float = 0.15, board: Optional['Board'] = None) -> None:
        line = SWIGtype.Shape(board and board.native_obj)
        line.SetShape(ShapeType.Segment)
        self._obj = line
        self.start = start
        self.end = end
        self.layer = layer
        self.width = width

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

    def geohash(self) -> int:
        hstart = hash(self.start)
        hend = hash(self.end)
        if hstart < hend:
            mine = hash((self.start, self.end))
        else:
            mine = hash((self.end, self.start))
        return mine + super().geohash()


class Circle(Drawing):
    def __init__(self, center: CoordinateLike, radius: float, layer: str = "F.SilkS", width: float = 0.15, board: Optional['Board'] = None) -> None:
        circle = SWIGtype.Shape(board and board.native_obj)
        circle.SetShape(ShapeType.Circle)
        self._obj = circle
        self.center = center
        self.width = width
        self.layer = layer

        start_coord = Point.native_from((center[0], center[1] + radius))
        if SWIG_version >= 6:
            circle.SetEnd(start_coord)
            circle.SetModified()
        else:
            circle.SetArcStart(start_coord)

    @property
    def center(self) -> Point:
        return Point.wrap(self._obj.GetCenter())

    @center.setter
    def center(self, value: CoordinateLike) -> None:
        self._obj.SetCenter(Point.native_from(value))

    @property
    def start(self) -> Point:
        if SWIG_version >= 6:
            return Point.wrap(self._obj.GetEnd())
        else:
            return Point.wrap(self._obj.GetArcStart())

    @start.setter
    def start(self, value: CoordinateLike) -> None:
        if SWIG_version >= 6:
            self._obj.SetEnd(Point.native_from(value))
            self._obj.SetModified()
        else:
            self._obj.SetArcStart(Point.native_from(value))

    @property
    def radius(self) -> float:
        return float(self._obj.GetRadius()) / units.DEFAULT_UNIT_IUS

    @radius.setter
    def radius(self, value: float) -> None:
        self._obj.SetRadius(int(value * units.DEFAULT_UNIT_IUS))

    def geohash(self) -> int:
        mine = hash((
            self.center,
            self.start,
            self.radius,
        ))
        return mine + super().geohash()


# --- Logic for Arc changed a lot in version 6, so there are two classes
class Arc_v5(Drawing):
    def __init__(
        self, center: CoordinateLike, radius: float, start_angle: float, stop_angle: float,
        layer: str = "F.SilkS", width: float = 0.15, board: Optional['Board'] = None,
    ) -> None:
        start_coord = radius * cmath.exp(math.radians(start_angle - 90) * 1j)
        start_coord = Point.native_from((start_coord.real, start_coord.imag))
        center_coord = Point.native_from(center)
        start_coord += center_coord

        angle = stop_angle - start_angle
        arc = SWIGtype.Shape(board and board.native_obj)
        arc.SetShape(ShapeType.Arc)
        arc.SetCenter(center_coord)
        arc.SetArcStart(start_coord)
        arc.SetAngle(angle * 10)
        arc.SetLayer(get_board_layer_id(board, layer))
        arc.SetWidth(int(width * units.DEFAULT_UNIT_IUS))
        self._obj = arc

    @property
    def center(self) -> Point:
        return Point.wrap(self._obj.GetCenter())

    @center.setter
    def center(self, value: CoordinateLike) -> None:
        self._obj.SetCenter(Point.native_from(value))

    @property
    def radius(self) -> float:
        return float(self._obj.GetRadius()) / units.DEFAULT_UNIT_IUS

    @radius.setter
    def radius(self, value: float) -> None:
        self._obj.SetRadius(int(value * units.DEFAULT_UNIT_IUS))

    @property
    def start(self) -> Point:
        return Point.wrap(self._obj.GetArcStart())

    @start.setter
    def start(self, value: CoordinateLike) -> None:
        self._obj.SetArcStart(Point.native_from(value))

    @property
    def end(self) -> Point:
        return Point.wrap(self._obj.GetArcEnd())

    @end.setter
    def end(self, value: CoordinateLike) -> None:
        self._obj.SetArcEnd(Point.native_from(value))

    @property
    def angle(self) -> float:
        return float(self._obj.GetAngle()) / 10

    @angle.setter
    def angle(self, value: float) -> None:
        self._obj.SetAngle(value * 10)

    def geohash(self) -> int:
        mine = hash((
            self.center,
            self.radius,
            self.start,
            self.end,
            self.angle
        ))
        return mine + super().geohash()


class Arc_v6(Drawing):
    def __init__(
        self, center: CoordinateLike, radius: float, start_angle: float, stop_angle: float,
        layer: str = "F.SilkS", width: float = 0.15, board: Optional['Board'] = None
    ):
        start_coord = radius * cmath.exp(math.radians(start_angle - 90) * 1j)
        abs_start = (start_coord.real + center[0], start_coord.imag + center[1])

        arc = SWIGtype.Shape(board and board.native_obj)
        arc.SetShape(ShapeType.Arc)
        self._obj = arc
        self.center = center
        self.start = abs_start
        self.angle = stop_angle - start_angle
        self.layer = layer
        self.width = width

    @property
    def center(self) -> Point:
        return Point.wrap(self._obj.GetCenter())

    @center.setter
    def center(self, value: CoordinateLike) -> None:
        self._obj.SetCenter(Point.native_from(value))

    @property
    def radius(self) -> float:
        return float(self._obj.GetRadius()) / units.DEFAULT_UNIT_IUS

    @radius.setter
    def radius(self, value: float) -> None:
        self._obj.SetRadius(int(value * units.DEFAULT_UNIT_IUS))

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
        start = self._obj.GetStart()
        mid = self._obj.GetArcMid()
        self._obj.SetArcGeometry(start, mid, Point.native_from(value))

    @property
    def angle(self) -> float:
        if SWIG_version >= 7:
            return float(self._obj.GetArcAngle().AsDegrees())
        else:
            return float(self._obj.GetArcAngle()) / 10

    @angle.setter
    def angle(self, value: float) -> None:
        if SWIG_version >= 7:
            val_obj = pcbnew.EDA_ANGLE(value, pcbnew.EDA_UNITS_DEGREES)
            self._obj.SetArcAngleAndEnd(val_obj)
        else:
            self._obj.SetArcAngleAndEnd(value * 10)

    def geohash(self) -> int:
        mine = hash((
            self.center,
            self.radius,
            self.start,
            self.end,
            self.angle
        ))
        return mine + super().geohash()


if SWIG_version >= 6:
    Arc = Arc_v6
else:
    Arc = Arc_v5


class Polygon(Drawing):
    def __init__(self, coords: List[CoordinateLike], layer: str = "F.SilkS", width: float = 0.15, board: Optional['Board'] = None) -> None:
        poly_obj = SWIGtype.Shape(board and board.native_obj)
        poly_obj.SetShape(ShapeType.Polygon)
        self._obj = poly_obj
        self.layer = layer
        self.width = width

        chain = pcbnew.SHAPE_LINE_CHAIN()
        for coord in coords:
            chain.Append(Point.native_from(coord))
        chain.SetClosed(True)
        poly_shape = pcbnew.SHAPE_POLY_SET(chain)
        poly_obj.SetPolyShape(poly_shape)

    @classmethod
    def _from_polyset(cls, shape_poly_set: Any, multiple: bool = False, **pkwds) -> Union['Polygon', List['Polygon']]:
        """If multiple=True, returns a list that can be any length (possibly zero).
        Otherwise, it checks that there is only one Outline and returns one Polygon, no list

        shape_poly_set is a `pcbnew.SHAPE_POLY_SET` native to `pcbnew`,
        so this constructor is not intended for direct usage
        """
        poly_builder = []
        for iout in range(shape_poly_set.OutlineCount()):
            outline = shape_poly_set.Outline(iout)
            pts = []
            for ipt in range(outline.PointCount()):
                native = outline.GetPoint(ipt)
                pts.append(Point.wrap(native))
            poly = cls(pts, **pkwds)
            poly_builder.append(poly)

        if multiple:
            return poly_builder
        else:
            if len(poly_builder) == 0:
                raise ValueError("Given SHAPE_POLY_SET has no Outlines")
            elif len(poly_builder) > 1:
                raise ValueError("SHAPE_POLY_SET contains multiple Outlines. Use Polygon.from_polyset(..., multiple=True)")
            return poly_builder[0]

    @property
    def filled(self) -> bool:
        return self._obj.IsFilled()

    @filled.setter
    def filled(self, value: bool = True) -> None:
        self._obj.SetFilled(value)

    def get_vertices(self) -> List[Point]:
        poly = self._obj.GetPolyShape()
        noutlines = poly.OutlineCount()
        if noutlines == 0:
            raise RuntimeError("Polygon's SHAPE_POLY_SET has no Outlines")
        elif noutlines > 1:
            raise ValueError("Polygon contains multiple Outlines which is not supported")
        outline = poly.Outline(0)
        pts = []
        for ipt in range(outline.PointCount()):
            native = outline.GetPoint(ipt)
            pts.append(Point.wrap(native))
        return pts

    def to_segments(self, replace: bool = False) -> List[Segment]:
        """If replace is true, removes the original polygon"""
        segs = []
        verts = self.get_vertices()
        for iseg in range(len(verts)):
            new_seg = Segment(
                verts[iseg - 1], verts[iseg],
                self.layer, self.width, self.board
            )
            segs.append(new_seg)
        if replace:
            for seg in segs:
                self.board.add(seg)
            self.board.remove(self)
        return segs

    def fillet(self, radius_mm: float, tol_mm: float = 0.01) -> None:
        poly = self.native_obj.GetPolyShape()
        smoothed = poly.Fillet(
            int(radius_mm * units.DEFAULT_UNIT_IUS),
            int(tol_mm * units.DEFAULT_UNIT_IUS),
        )
        self.native_obj.SetPolyShape(smoothed)

    def contains(self, point: CoordinateLike) -> bool:
        """Does this shape contain the point

        Args:
            point (tuple, Point): the point as a tuple or kigadgets.Point
        Returns:
            bool: True if contained
        """
        poly = self._obj.GetPolyShape()
        return poly.Contains(Point.native_from(point))

    def geohash(self) -> int:
        mine = hash((
            tuple(self.get_vertices()),
            self.filled,
        ))
        return mine + super().geohash()


class Rectangle(Polygon):
    """Inherits x,y get/set from HasPosition"""
    def __init__(self, corner_nw: CoordinateLike, corner_se: CoordinateLike, layer: str = "F.SilkS", width: float = 0.15, board: Optional['Board'] = None) -> None:
        rect_obj = SWIGtype.Shape(board and board.native_obj)
        rect_obj.SetShape(ShapeType.Rect)
        self._obj = rect_obj
        rect_obj.SetStart(Point.native_from(corner_nw))
        rect_obj.SetEnd(Point.native_from(corner_se))
        self.layer = layer
        self.width = width

    @classmethod
    def from_centersize(
        cls, xcent: float, ycent: float, xsize: float, ysize: float,
        layer: str = "F.SilkS", width: float = 0.15, board: Optional['Board'] = None
    ) -> 'Rectangle':
        center = Point(xcent, ycent)
        half_size = Point(xsize / 2, ysize / 2)
        corner_nw = center - half_size
        corner_se = center + half_size
        return cls(corner_nw, corner_se, layer, width, board)

    def get_vertices(self) -> List[Point]:
        corners_native = self.native_obj.GetRectCorners()
        corners = [Point.wrap(pt) for pt in corners_native]
        return corners

    @property
    def size(self) -> Tuple[float, float]:
        nw = Point.wrap(self._obj.GetStart())
        se = Point.wrap(self._obj.GetEnd())
        sz = nw - se
        return (abs(sz[0]), abs(sz[1]))

    # The inherited to_segments works based on overloading get_vertices

    def to_polygon(self, replace: bool = False) -> Polygon:
        corners_native = self.native_obj.GetRectCorners()
        corners = [Point.wrap(pt) for pt in corners_native]
        poly = Polygon(corners, layer=self.layer, width=self.width, board=self.board)
        if replace:
            self.board.add(poly)
            self.board.remove(self)
        return poly

    def fillet(self, radius_mm: float, tol_mm: float = 0.01) -> None:
        """Deletes the rectangle but that is ok in most situations
        It can be undone IF it is run inside an action plugin
        """
        poly = self.to_polygon(replace=True)
        poly.fillet(radius_mm, tol_mm)

    def contains(self, point: CoordinateLike) -> bool:
        """Does this shape contain the point

        Args:
            point (tuple, Point): the point as a tuple or kigadgets.Point
        Returns:
            bool: True if contained
        """
        poly = self.to_polygon(replace=False)
        return poly.contains(point)


class TextPCB(HasLayer, HasPosition, Selectable, BoardItem, TextEsque):
    _wraps_native_cls = SWIGtype.Text

    def __init__(
        self, position: CoordinateLike, text: Optional[str] = None, layer: str = "F.SilkS",
        size: float = 1.0, thickness: float = 0.15, justification: Optional[Union[str, Tuple[str, str]]] = None,
        mirrored: bool = False, board: Optional['Board'] = None
    ) -> None:
        self._obj = self._wraps_native_cls(board and board.native_obj)
        self.position = position
        if text:
            self.text = text
        if justification:
            self.justification = justification
        self.layer = layer
        self.size = size
        self.thickness = thickness
        self.mirrored = mirrored
