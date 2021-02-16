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
from kicad import units, Size
from kicad.pcbnew.item import HasLayerStrImpl, Selectable, HasPosition


class Drawing(HasLayerStrImpl, Selectable):
    @property
    def native_obj(self):
        return self._obj

    @staticmethod
    def wrap(instance):
        if type(instance) is pcbnew.DRAWSEGMENT:
            return Drawing._wrap_drawsegment(instance)
        elif type(instance) is pcbnew.TEXTE_PCB:
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


class Segment(Drawing):
    def __init__(self, start, end, layer='F.SilkS', width=0.15, board=None):
        line = pcbnew.DRAWSEGMENT(board and board.native_obj)
        line.SetShape(pcbnew.S_SEGMENT)
        line.SetStart(Point.native_from(start))
        line.SetEnd(Point.native_from(end))
        line.SetLayer(pcbnew_layer.get_board_layer(board, layer))
        line.SetWidth(int(width * units.DEFAULT_UNIT_IUS))
        self._obj = line


class Circle(Drawing):
    def __init__(self, center, radius, layer='F.SilkS', width=0.15,
                 board=None):
        circle = pcbnew.DRAWSEGMENT(board and board.native_obj)
        circle.SetShape(pcbnew.S_CIRCLE)
        circle.SetCenter(Point.native_from(center))
        start_coord = Point.native_from(
            (center[0], center[1] + radius))
        circle.SetArcStart(start_coord)
        circle.SetLayer(pcbnew_layer.get_board_layer(board, layer))
        circle.SetWidth(int(width * units.DEFAULT_UNIT_IUS))
        self._obj = circle


class Arc(Drawing):
    def __init__(self, center, radius, start_angle, stop_angle,
                 layer='F.SilkS', width=0.15, board=None):
        start_coord = radius * cmath.exp(math.radians(start_angle - 90) * 1j)
        start_coord = Point.native_from((start_coord.real, start_coord.imag))

        angle = stop_angle - start_angle
        arc = pcbnew.DRAWSEGMENT(board and board.native_obj)
        arc.SetShape(pcbnew.S_ARC)
        arc.SetCenter(Point.native_from(center))
        arc.SetArcStart(start_coord)
        arc.SetAngle(angle * 10)
        arc.SetLayer(pcbnew_layer.get_board_layer(board, layer))
        arc.SetWidth(int(width * units.DEFAULT_UNIT_IUS))
        self._obj = arc


class TextPCB(Drawing, HasPosition):
    def __init__(self, position, text=None, layer='F.SilkS', size=1.0, thickness=0.15, board=None):
        self._obj = pcbnew.TEXTE_PCB(board and board.native_obj)
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
        for k, v in lookups.items():
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
                token = lookups[value]
            except KeyError:
                raise ValueError('Invalid justification {} of available {}'.format(value, list(lookups.keys())))
            enum_val = getattr(pcbnew, token)
            if 'HJUSTIFY' in token:
                self._obj.SetHorizJustify(enum_val)
            else:
                self._obj.SetVertJustify(enum_val)

lookups = dict(
    left='GR_TEXT_HJUSTIFY_LEFT',
    center='GR_TEXT_HJUSTIFY_CENTER',
    right='GR_TEXT_HJUSTIFY_RIGHT',
    bottom='GR_TEXT_VJUSTIFY_BOTTOM',
    middle='GR_TEXT_VJUSTIFY_CENTER',
    top='GR_TEXT_VJUSTIFY_TOP',
)
