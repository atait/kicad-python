from kicad import pcbnew_bare as pcbnew

import kicad
from kicad.exceptions import deprecate_member
from kicad import Point, Size, DEFAULT_UNIT_IUS, SWIGtype, SWIG_version
from kicad.pcbnew.item import HasPosition, HasRotation, HasLayerEnumImpl, Selectable, HasLayerStrImpl, BoardItem
from kicad.pcbnew.pad import Pad


class ModuleLabel(HasPosition, HasRotation, HasLayerStrImpl, Selectable):
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
        if type(instance) is not SWIGtype.FpShape:
            # raise TypeError()
            return None
        return kicad.new(ModuleLine, instance)


@deprecate_member('referenceLabel', 'reference_label')
@deprecate_member('valueLabel', 'value_label')
@deprecate_member('graphicalItems', 'graphical_items')
@deprecate_member('libName', 'lib_name')
@deprecate_member('fpName', 'fp_name')
class Module(HasPosition, HasRotation, Selectable, BoardItem):
    _ref_label = None
    _val_label = None

    def __init__(self, ref=None, pos=None, board=None):
        if not board:
            from kicad.pcbnew.board import Board
            try:
                board = Board.from_editor()
            except:
                board = None
        self._obj = SWIGtype.Footprint(board.native_obj)
        if ref:
            self.reference = ref
        if pos:
            self.position = pos
        if board:
            board.add(self)

    @staticmethod
    def wrap(instance):
        if type(instance) is not SWIGtype.Footprint:
            # raise TypeError()
            return None
        return kicad.new(Module, instance)

    @property
    def reference(self):
        return self._obj.GetReference()

    @reference.setter
    def reference(self, value):
        self._obj.SetReference(value)

    @property
    def reference_label(self):
        native = self._obj.Reference()
        if self._ref_label is None or self._ref_label.native_obj is not native:
            self._ref_label = ModuleLabel.wrap(native)
        return self._ref_label

    @property
    def value(self):
        return self._obj.GetValue()

    @value.setter
    def value(self, value):
        self._obj.SetValue(value)

    @property
    def value_label(self):
        native = self._obj.Value()
        if self._val_label is None or self._val_label.native_obj is not native:
            self._val_label = ModuleLabel.wrap(native)
        return self._val_label

    @property
    def graphical_items(self):
        """Text and drawings of module iterator."""
        for item in self._obj.GraphicalItems():
            if type(item) == SWIGtype.FpShape:
                yield ModuleLine.wrap(item)
            elif type(item) == SWIGtype.FpText:
                yield ModuleLabel.wrap(item)
            else:
                raise Exception("Unknown module item type: %s" % type(item))

    def flip(self):
        self._obj.Flip(self._obj.GetCenter())

    @property
    def layer(self):
        if self.board:
            return self.board.get_layer_name(self._obj.GetLayer())
        else:
            return pcbnew_layer.get_std_layer_name(self._obj.GetLayer())

    @layer.setter
    def layer(self, value):
        if value == self.layer:
            return
        if value not in ['F.Cu', 'B.Cu']:
            raise ValueError("You can place a module only on 'F.Cu' or 'B.Cu' layers!")
        # Using flip will make sure all components of the module are
        # switched to correct layer
        self.flip()

    @property
    def lib_name(self):
        return self._obj.GetFPID().GetLibNickname().GetChars()

    @property
    def fp_name(self):
        return self._obj.GetFPID().GetLibItemName().GetChars()

    def copy(self, ref, pos=None, board=None):
        """Create a copy of an existing module on the board
            A new reference designator is required, example:
                mod2 = mod1.copy('U2')
                mod2.reference == 'U2'  # True
        """
        if SWIG_version >= 7:
            _module = SWIGtype.Footprint(self._obj)
        else:
            _module = SWIGtype.Footprint(board and board._obj)
            _module.Copy(self._obj)
        module = Module.wrap(_module)
        module.reference = ref
        if pos:
            module.position = pos
        if board:
            board.add(module)
        elif self.board:
            self.board.add(module)
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


# In case v6+ naming is used
Footprint = Module
FootprintLine = ModuleLine
FootprintLabel = ModuleLabel
