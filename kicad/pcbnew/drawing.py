import cmath
import math

from kicad import pcbnew_bare as pcbnew, instanceof
import kicad
from kicad.pcbnew import layer as pcbnew_layer
from kicad.point import Point
from kicad import units, Size, SWIGtype, SWIG_version
from kicad.pcbnew.item import HasLayerStrImpl, Selectable, HasPosition, HasWidth, BoardItem

class ShapeType():
    Segment = pcbnew.S_SEGMENT
    Circle = pcbnew.S_CIRCLE
    Arc = pcbnew.S_ARC
    Polygon = pcbnew.S_POLYGON
    Rect = pcbnew.S_RECT

class Drawing(HasLayerStrImpl, HasPosition, HasWidth, Selectable, BoardItem):
    @staticmethod
    def wrap(instance):
        if instanceof(instance, SWIGtype.Shape):
            return Drawing._wrap_drawsegment(instance)
        elif instanceof(instance, SWIGtype.Text):
            return kicad.new(TextPCB, instance)
        else:
            raise TypeError('Invalid drawing class: {}'.format(type(instance)))

    @staticmethod
    def _wrap_drawsegment(instance):
        obj_shape = instance.GetShape()

        if obj_shape is pcbnew.S_SEGMENT:
            return kicad.new(Segment, instance)

        if obj_shape is pcbnew.S_CIRCLE:
            return kicad.new(Circle, instance)

        if obj_shape is pcbnew.S_ARC:
            return kicad.new(Arc, instance)

        if obj_shape is pcbnew.S_POLYGON:
            return kicad.new(Polygon, instance)

        if obj_shape is pcbnew.S_RECT:
            return kicad.new(Rectangle, instance)

        # Time to fail
        layer = instance.GetLayer()
        layer_str = pcbnew.BOARD_GetStandardLayerName(layer)
        unsupported = ['S_CURVE', 'S_LAST']
        for unsup in unsupported:
            if not hasattr(pcbnew, unsup):
                continue
            if obj_shape is getattr(pcbnew, unsup):
                raise TypeError('Unsupported shape type: pcbnew.{} on layer {}.'.format(unsup, layer_str))

        raise TypeError('Unrecognized shape type on layer {}'.format(layer_str))


class Segment(Drawing):
    def __init__(self, start, end, layer='F.SilkS', width=0.15, board=None):
        line = SWIGtype.Shape(board and board.native_obj)
        line.SetShape(ShapeType.Segment)
        self._obj = line
        line.SetStart(Point.native_from(start))
        line.SetEnd(Point.native_from(end))
        self.layer = layer
        self.width = width

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


class Circle(Drawing):
    def __init__(self, center, radius, layer='F.SilkS', width=0.15,
                 board=None):
        circle = SWIGtype.Shape(board and board.native_obj)
        circle.SetShape(ShapeType.Circle)
        circle.SetCenter(Point.native_from(center))
        start_coord = Point.native_from(
            (center[0], center[1] + radius))
        if SWIG_version >= 6:
            circle.SetEnd(start_coord)
            circle.SetModified()
        else:
            circle.SetArcStart(start_coord)
        circle.SetLayer(pcbnew_layer.get_board_layer_id(board, layer))
        circle.SetWidth(int(width * units.DEFAULT_UNIT_IUS))
        self._obj = circle

    @property
    def center(self):
        return Point.wrap(self._obj.GetCenter())

    @center.setter
    def center(self, value):
        self._obj.SetCenter(Point.native_from(value))

    @property
    def start(self):
        if SWIG_version >= 6:
            return Point.wrap(self._obj.GetEnd())
        else:
            return Point.wrap(self._obj.GetArcStart())

    @start.setter
    def start(self, value):
        if SWIG_version >= 6:
            self._obj.SetEnd(Point.native_from(value))
            self._obj.SetModified()
        else:
            self._obj.SetArcStart(Point.native_from(value))

    @property
    def radius(self):
        return float(self._obj.GetRadius()) / units.DEFAULT_UNIT_IUS

    @radius.setter
    def radius(self, value):
        self._obj.SetRadius(int(value * units.DEFAULT_UNIT_IUS))


# --- Logic for Arc changed a lot in version 6, so there are two classes
class Arc_v5(Drawing):
    def __init__(self, center, radius, start_angle, stop_angle,
                 layer='F.SilkS', width=0.15, board=None):
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
        arc.SetLayer(pcbnew_layer.get_board_layer_id(board, layer))
        arc.SetWidth(int(width * units.DEFAULT_UNIT_IUS))
        self._obj = arc

    @property
    def center(self):
        return Point.wrap(self._obj.GetCenter())

    @center.setter
    def center(self, value):
        self._obj.SetCenter(Point.native_from(value))

    @property
    def radius(self):
        return float(self._obj.GetRadius()) / units.DEFAULT_UNIT_IUS

    @radius.setter
    def radius(self, value):
        self._obj.SetRadius(int(value * units.DEFAULT_UNIT_IUS))

    @property
    def start(self):
        return Point.wrap(self._obj.GetArcStart())

    @start.setter
    def start(self, value):
        self._obj.SetArcStart(Point.native_from(value))

    @property
    def end(self):
        return Point.wrap(self._obj.GetArcEnd())

    @end.setter
    def end(self, value):
        self._obj.SetArcEnd(Point.native_from(value))

    @property
    def angle(self):
        return float(self._obj.GetAngle()) / 10

    @angle.setter
    def angle(self, value):
        self._obj.SetAngle(value * 10)


class Arc_v6(Drawing):
    def __init__(self, center, radius, start_angle, stop_angle,
                 layer='F.SilkS', width=0.15, board=None):
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
    def center(self):
        return Point.wrap(self._obj.GetCenter())

    @center.setter
    def center(self, value):
        self._obj.SetCenter(Point.native_from(value))

    @property
    def radius(self):
        return float(self._obj.GetRadius()) / units.DEFAULT_UNIT_IUS

    @radius.setter
    def radius(self, value):
        self._obj.SetRadius(int(value * units.DEFAULT_UNIT_IUS))

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
        start = self._obj.GetStart()
        mid = self._obj.GetArcMid()
        self._obj.SetArcGeometry(start, mid, Point.native_from(value))

    @property
    def angle(self):
        if SWIG_version >= 7:
            return float(self._obj.GetArcAngle().AsDegrees())
        else:
            return float(self._obj.GetArcAngle()) / 10

    @angle.setter
    def angle(self, value):
        if SWIG_version >= 7:
            val_obj = pcbnew.EDA_ANGLE(value, pcbnew.EDA_UNITS_DEGREES)
            self._obj.SetArcAngleAndEnd(val_obj)
        else:
            self._obj.SetArcAngleAndEnd(value * 10)

if SWIG_version >= 6:
    Arc = Arc_v6
else:
    Arc = Arc_v5


class Polygon(Drawing):
    def __init__(self, coords,
                 layer='F.SilkS', width=0.15, board=None):
        poly_obj = SWIGtype.Shape(board and board.native_obj)
        poly_obj.SetShape(ShapeType.Polygon)
        self._obj = poly_obj

        chain = pcbnew.SHAPE_LINE_CHAIN()
        for coord in coords:
            chain.Append(Point.native_from(coord))
        chain.SetClosed(True)
        poly_shape = pcbnew.SHAPE_POLY_SET(chain)
        poly_obj.SetPolyShape(poly_shape)

        self.layer = layer
        self.width = width

    @property
    def filled(self):
        return self._obj.IsFilled()

    @filled.setter
    def filled(self, value=True):
        self._obj.SetFilled(value)

    def get_vertices(self):
        poly = self._obj.GetPolyShape()
        noutlines = poly.OutlineCount()
        if noutlines == 0:
            raise RuntimeError('Polygon\'s SHAPE_POLY_SET has no Outlines')
        elif noutlines > 1:
            raise ValueError('Polygon contains multiple Outlines which is not supported')
        outline = poly.Outline(0)
        pts = []
        for ipt in range(outline.PointCount()):
            native = outline.GetPoint(ipt)
            pts.append(Point.wrap(native))
        return pts

    def to_segments(self, replace=False):
        ''' If replace is true, removes the original polygon
        '''
        segs = []
        verts = self.get_vertices()
        for iseg in range(len(verts)):
            new_seg = Segment(verts[iseg-1], verts[iseg],
                self.layer, self.width, self.board
            )
            segs.append(new_seg)
        if replace:
            for seg in segs:
                self.board.add(seg)
            self.board.remove(self)
        return segs

    def fillet(self, radius_mm, tol_mm=.01):
        poly = self.native_obj.GetPolyShape()
        smoothed = poly.Fillet(int(radius_mm * units.DEFAULT_UNIT_IUS), int(tol_mm * units.DEFAULT_UNIT_IUS))
        self.native_obj.SetPolyShape(smoothed)

    def contains(self, point):
        poly = self._obj.GetPolyShape()
        return poly.Contains(Point.native_from(point))


class Rectangle(Polygon):
    ''' Inherits x,y get/set from HasPosition '''
    def __init__(self, corner_nw, corner_se,
                 layer='F.SilkS', width=0.15, board=None):
        rect_obj = SWIGtype.Shape(board and board.native_obj)
        rect_obj.SetShape(ShapeType.Rect)
        self._obj = rect_obj
        rect_obj.SetStart(Point.native_from(corner_nw))
        rect_obj.SetEnd(Point.native_from(corner_se))
        self.layer = layer
        self.width = width

    @classmethod
    def from_centersize(cls, xcent, ycent, xsize, ysize,
                     layer='F.SilkS', width=0.15, board=None):
        center = Point(xcent, ycent)
        half_size = Point(xsize / 2, ysize / 2)
        corner_nw = center - half_size
        corner_se = center + half_size
        return cls(corner_nw, corner_se, layer, width, board)

    def get_vertices(self):
        corners_native = self.native_obj.GetRectCorners()
        corners = [Point.wrap(pt) for pt in corners_native]
        return corners

    @property
    def size(self):
        nw = Point.wrap(self._obj.GetStart())
        se = Point.wrap(self._obj.GetEnd())
        sz = nw - se
        return (abs(sz[0]), abs(sz[1]))

    # The inherited to_segments works based on overloading get_vertices

    def to_polygon(self, replace=False):
        corners_native = self.native_obj.GetRectCorners()
        corners = [Point.wrap(pt) for pt in corners_native]
        poly = Polygon(corners, layer=self.layer, width=self.width, board=self.board)
        if replace:
            self.board.add(poly)
            self.board.remove(self)
        return poly

    def fillet(self, radius_mm, tol_mm=.01):
        ''' Deletes the rectangle but that is ok in most situations
            It can be undone IF it is run inside an action plugin
        '''
        poly = self.to_polygon(replace=True)
        poly.fillet(radius_mm, tol_mm)

    def contains(self, point):
        poly = self.to_polygon(replace=False)
        return poly.contains(point)


class TextPCB(Drawing):
    def __init__(self, position, text=None, layer='F.SilkS',
                 size=1.0, thickness=0.15, board=None):
        self._obj = SWIGtype.Text(board and board.native_obj)
        self.position = position
        if text:
            self.text = text
        self.layer = layer
        self.size = size
        self.thickness = thickness

    @property
    def text(self):
        return self._obj.GetText()

    @text.setter
    def text(self, value):
        return self._obj.SetText(value)

    @property
    def thickness(self):
        if SWIG_version >= 7:
            return float(self._obj.GetTextThickness()) / units.DEFAULT_UNIT_IUS
        else:
            return float(self._obj.GetThickness()) / units.DEFAULT_UNIT_IUS

    @thickness.setter
    def thickness(self, value):
        if SWIG_version >= 7:
            return self._obj.SetTextThickness(int(value * units.DEFAULT_UNIT_IUS))
        else:
            return self._obj.SetThickness(int(value * units.DEFAULT_UNIT_IUS))

    @property
    def size(self):
        return Size.wrap(self._obj.GetTextSize())

    @size.setter
    def size(self, value):
        try:
            size = Size.build_from(value)
        except TypeError:
            size = Size.build_from((value, value))
        self._obj.SetTextSize(size.native_obj)

    @property
    def orientation(self):
        return self._obj.GetTextAngle() / 10

    @orientation.setter
    def orientation(self, value):
        self._obj.SetTextAngle(value * 10)

    @property
    def justification(self):
        hj = self._obj.GetHorizJustify()
        vj = self._obj.GetVertJustify()
        for k, v in justification_lookups.items():
            if hj == getattr(pcbnew, v):
                hjs = k
            if vj in getattr(pcbnew, v):
                vjs = k
        return hjs, vjs

    @justification.setter
    def justification(self, value):
        if isinstance(value, (list, tuple)):
            assert len(value) == 2
            self.justification = value[0]
            self.justification = value[1]
        else:
            try:
                token = justification_lookups[value]
            except KeyError:
                raise ValueError('Invalid justification {} of available {}'.format(value, list(justification_lookups.keys())))
            enum_val = getattr(pcbnew, token)
            if 'HJUSTIFY' in token:
                self._obj.SetHorizJustify(enum_val)
            else:
                self._obj.SetVertJustify(enum_val)

justification_lookups = dict(
    left='GR_TEXT_HJUSTIFY_LEFT',
    center='GR_TEXT_HJUSTIFY_CENTER',
    right='GR_TEXT_HJUSTIFY_RIGHT',
    bottom='GR_TEXT_VJUSTIFY_BOTTOM',
    middle='GR_TEXT_VJUSTIFY_CENTER',
    top='GR_TEXT_VJUSTIFY_TOP',
)
