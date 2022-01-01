#  Copyright 2014 Piers Titus van der Torren <pierstitus@gmail.com>
#  Copyright 2015 Miguel Angel Ajo <miguelangel@ajo.es>
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
import cmath
import math

from kicad import pcbnew_bare as pcbnew
import kicad
from kicad.pcbnew import layer as pcbnew_layer
from kicad.point import Point
from kicad import units, Size, SWIGtype, SWIG_version
from kicad.pcbnew.item import HasLayerStrImpl, Selectable, HasPosition
from enum import IntEnum

class ShapeType(IntEnum):
    Segment = pcbnew.S_SEGMENT
    Circle = pcbnew.S_CIRCLE
    Arc = pcbnew.S_ARC
    Polygon = pcbnew.S_POLYGON

class Drawing(HasLayerStrImpl, Selectable):
    @property
    def native_obj(self):
        return self._obj

    @staticmethod
    def wrap(instance):
        if type(instance) == SWIGtype.Shape:
            return Drawing._wrap_drawsegment(instance)
        elif type(instance) == SWIGtype.Text:
            return kicad.new(TextPCB, instance)

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

        # Time to fail
        layer = instance.GetLayer()
        layer_str = pcbnew.BOARD_GetStandardLayerName(layer)
        unsupported = ['S_CURVE', 'S_RECT', 'S_LAST']
        for unsup in unsupported:
            if obj_shape is getattr(pcbnew, unsup):
                raise TypeError('Unsupported shape type: pcbnew.{} on layer {}.'.format(unsup, layer_str))

        raise TypeError('Unrecognized shape type on layer {}'.format(layer_str))


class HasWidth(object):
    @property
    def width(self):
        return float(self._obj.GetWidth()) / units.DEFAULT_UNIT_IUS

    @width.setter
    def width(self, value):
        self._obj.SetWidth(int(value * units.DEFAULT_UNIT_IUS))


class Segment(Drawing, HasWidth):
    def __init__(self, start, end, layer='F.SilkS', width=0.15, board=None):
        line = SWIGtype.Shape(board and board.native_obj)
        line.SetShape(ShapeType.Segment)
        line.SetStart(Point.native_from(start))
        line.SetEnd(Point.native_from(end))
        line.SetLayer(pcbnew_layer.get_board_layer(board, layer))
        line.SetWidth(int(width * units.DEFAULT_UNIT_IUS))
        self._obj = line

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


class Circle(Drawing, HasWidth):
    def __init__(self, center, radius, layer='F.SilkS', width=0.15,
                 board=None):
        circle = SWIGtype.Shape(board and board.native_obj)
        circle.SetShape(ShapeType.Circle)
        circle.SetCenter(Point.native_from(center))
        start_coord = Point.native_from(
            (center[0], center[1] + radius))
        if SWIG_version == 6:
            circle.SetStart(start_coord)
        else:
            circle.SetArcStart(start_coord)
        circle.SetLayer(pcbnew_layer.get_board_layer(board, layer))
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
        return Point.wrap(self._obj.GetArcStart())

    @start.setter
    def start(self, value):
        if SWIG_version == 6:
            self._obj.SetStart(Point.native_from(value))
        else:
            self._obj.SetArcStart(Point.native_from(value))

    @property
    def radius(self):
        return float(self._obj.GetRadius()) / units.DEFAULT_UNIT_IUS

    @radius.setter
    def radius(self, value):
        self._obj.SetRadius(int(value * units.DEFAULT_UNIT_IUS))


# --- Logic for Arc changed a lot in version 6, so there are two classes
class Arc_v5(Drawing, HasWidth):
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
        arc.SetLayer(pcbnew_layer.get_board_layer(board, layer))
        arc.SetWidth(int(width * units.DEFAULT_UNIT_IUS))
        self._obj = arc

    @property
    def center(self):
        return Point.wrap(self._obj.GetCenter())

    @center.setter
    def center(self, value):
        self._obj.SetCenter(Point.native_from(value))

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


class Arc_v6(Drawing, HasWidth):
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
        arc.SetStart(start_coord)
        arc.SetArcAngleAndEnd(angle * 10)
        arc.SetLayer(pcbnew_layer.get_board_layer(board, layer))
        arc.SetWidth(int(width * units.DEFAULT_UNIT_IUS))
        self._obj = arc

    @property
    def center(self):
        return Point.wrap(self._obj.GetCenter())

    @center.setter
    def center(self, value):
        self._obj.SetCenter(Point.native_from(value))

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
        return float(self._obj.GetArcAngle()) / 10

    @angle.setter
    def angle(self, value):
        self._obj.SetArcAngleAndEnd(value * 10)

if SWIG_version == 6:
    Arc = Arc_v6
else:
    Arc = Arc_v5


class Polygon(Drawing, HasWidth):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError('Polygon direct instantiation is not supported by kicad-python')


class TextPCB(Drawing, HasPosition):
    def __init__(self, position, text=None, layer='F.SilkS', size=1.0, thickness=0.15, board=None):
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
        return float(self._obj.GetThickness()) / units.DEFAULT_UNIT_IUS

    @thickness.setter
    def thickness(self, value):
        return self._obj.SetThickness(int(value * units.DEFAULT_UNIT_IUS))

    @property
    def size(self):
        return Size.wrap(self._obj.GetTextSize())

    @size.setter
    def size(self, value):
        if isinstance(value, tuple):
            if not isinstance(value, Size):
                value = Size(value[0], value[1])
            self._obj.SetTextSize(value.native_obj)

        else: # value is a single number/integer
            self._obj.SetTextSize(Size(value, value).native_obj)

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
