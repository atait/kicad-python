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
from kicad import units
from kicad.pcbnew.item import HasLayerStrImpl


class Drawing(HasLayerStrImpl):
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


class TextPCB(Drawing):
    ''' Todo: test the methods. It is copied from ModuleLabel '''
    pass
#     """wrapper for `TEXTE_PCB`"""
#     def __init__(self, mod, text=None, layer=None):
#         self._obj = pcbnew.TEXTE_PCB(mod.native_obj)
#         mod.native_obj.Add(self._obj)
#         if text:
#             self.text = text
#         if layer:
#             self.layer = layer

#     @property
#     def text(self):
#         return self._obj.GetText()

#     @text.setter
#     def text(self, value):
#         return self._obj.SetText(value)

#     @property
#     def thickness(self):
#         return float(self._obj.GetThickness()) / DEFAULT_UNIT_IUS

#     @thickness.setter
#     def thickness(self, value):
#         return self._obj.SetThickness(int(value * DEFAULT_UNIT_IUS))

#     @property
#     def size(self):
#         return Size.wrap(self._obj.GetTextSize())

#     @size.setter
#     def size(self, value):
#         if isinstance(value, tuple):
#             if not isinstance(value, Size):
#                 value = Size(value[0], value[1])
#             self._obj.SetTextSize(value.native_obj)

#         else: # value is a single number/integer
#             self._obj.SetTextSize(Size(value, value).native_obj)

#     @staticmethod
#     def wrap(instance):
#         if type(instance) is pcbnew.TEXTE_MODULE:
#             return kicad.new(ModuleLabel, instance)
