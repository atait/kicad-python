#  Copyright 2014 Piers Titus van der Torren <pierstitus@gmail.com>
#  Copyright 2015 Miguel Angel Ajo <miguelangel@ajo.es>
#  Copyright 2017 Hasan Yavuz Ozderya <hy@ozderya.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
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
from kicad import pcbnew_bare as pcbnew

import kicad
from kicad import Point, Size, DEFAULT_UNIT_IUS, SWIGtype
from kicad.pcbnew.item import HasPosition, HasRotation, HasLayerEnumImpl, Selectable, HasLayerStrImpl
from kicad.pcbnew.layer import Layer
from kicad.pcbnew.pad import Pad


class ModuleLabel(HasPosition, HasRotation, HasLayerEnumImpl, Selectable):
    """wrapper for `TEXTE_MODULE`"""
    def __init__(self, mod, text=None, layer=None):
        self._obj = SWIGtype.FpText(mod.native_obj)
        mod.native_obj.Add(self._obj)
        if text:
            self.text = text
        if layer:
            self.layer = layer

    @property
    def text(self):
        return self._obj.GetText()

    @text.setter
    def text(self, value):
        return self._obj.SetText(value)

    @property
    def visible(self):
        raise ValueError('ModuleLabel.visible is write only.')

    @visible.setter
    def visible(self, value):
        return self._obj.SetVisible(value)

    @property
    def thickness(self):
        return float(self._obj.GetThickness()) / DEFAULT_UNIT_IUS

    @thickness.setter
    def thickness(self, value):
        return self._obj.SetThickness(int(value * DEFAULT_UNIT_IUS))

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

    @staticmethod
    def wrap(instance):
        if type(instance) is SWIGtype.FpText:
            return kicad.new(ModuleLabel, instance)


class ModuleLine(HasLayerStrImpl, Selectable):
    """Wrapper for `EDGE_MODULE`"""
    @property
    def native_obj(self):
        return self._obj

    @staticmethod
    def wrap(instance):
        if type(instance) is SWIGtype.FpShape:
            return kicad.new(ModuleLine, instance)


class Module(HasPosition, HasRotation, Selectable):
    def __init__(self, ref=None, pos=None, board=None):
        self._obj = SWIGtype.Footprint(board.native_obj)
        if ref:
            self.reference = ref
        if pos:
            self.position = pos
        if board:
            board.add(self)

    @property
    def native_obj(self):
        return self._obj

    @staticmethod
    def wrap(instance):
        if type(instance) is SWIGtype.Footprint:
            return kicad.new(Module, instance)

    @property
    def reference(self):
        return self._obj.GetReference()

    @reference.setter
    def reference(self, value):
        self._obj.SetReference(value)

    @property
    def referenceLabel(self):
        # TODO: not critical but always return the same wrapper object
        return ModuleLabel.wrap(self._obj.Reference())

    @property
    def value(self):
        return self._obj.GetValue()

    @value.setter
    def value(self, value):
        self._obj.SetValue(value)

    @property
    def valueLabel(self):
        # TODO: not critical but always return the same wrapper object
        return ModuleLabel.wrap(self._obj.Value())

    @property
    def graphicalItems(self):
        """Text and drawings of module iterator."""
        for item in self._obj.GraphicalItems():
            if type(item) == SWIGtype.FpShape:
                yield ModuleLine.wrap(item)
            elif type(item) == SWIGtype.FpText:
                yield ModuleLabel.wrap(item)
            else:
                raise Exception("Unknown module item type: %s" % type(item))

    @property
    def layer(self):
        return Layer(self._obj.GetLayer())

    @layer.setter
    def layer(self, value):
        if value != self.layer:
            if value in [Layer.Front, Layer.Back]:
                # this will make sure all components of the module is
                # switched to correct layer
                self._obj.Flip(self._obj.GetCenter())
            else:
                raise ValueError("You can place a module only on Front or Back layers!")

    @property
    def libName(self):
        return self._obj.GetFPID().GetLibNickname().GetChars()

    @property
    def fpName(self):
        return self._obj.GetFPID().GetLibItemName().GetChars()

    def copy(self, ref, pos=None, board=None):
        """Create a copy of an existing module on the board"""
        _module = SWIGtype.Footprint(board and board._obj)
        _module.Copy(self._obj)
        module = Module.wrap(_module)
        module.reference = ref
        if pos:
            module.position = pos
        if board:
            board.add(module)
        return module

    @property
    def pads(self):
        for p in self._obj.Pads():
            yield Pad.wrap(p)

    def remove(self, element, permanent=False):
        ''' Makes it so Ctrl-Z works.
            Keeps a reference to the element in the python pcb object,
            so it persists for the life of that object
        '''
        if not permanent:
            if not hasattr(self, '_removed_elements'):
                self._removed_elements = []
            self._removed_elements.append(element)
        self._obj.Remove(element._obj)

    def restore_removed(self):
        if hasattr(self, '_removed_elements'):
            for element in self._removed_elements:
                self._obj.Add(element._obj)
        self._removed_elements = []
