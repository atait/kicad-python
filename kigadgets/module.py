"""Footprint (module) handling for KiCad PCB components.

This module provides classes for representing PCB footprints, which contain
pads, graphical elements, text labels, and electrical connections.

Key features:
- Footprint creation from libraries and copying existing footprints
- Management of reference designators and component values
- Access to pads and graphical items within footprints
- Geohashing for layout comparison
"""

from kigadgets import pcbnew_bare as pcbnew

from kigadgets import Point, Size, DEFAULT_UNIT_IUS, SWIGtype, SWIG_version, instanceof
from kigadgets.item import HasPosition, HasOrientation, Selectable, HasLayer, BoardItem, TextEsque
from kigadgets.pad import Pad
from kigadgets.layer import get_board_layer_name
from kigadgets.drawing import wrap_drawing, TextPCB
from kigadgets.units import CoordinateLike
from typing import Optional, List, Union, Any


class FootprintLabel(TextPCB):
    """wrapper for `TEXTE_MODULE` (old) or `FP_TEXT`"""
    _wraps_native_cls = SWIGtype.FpText

    @property
    def visible(self) -> bool:
        try:
            return self._obj.IsVisible()
        except AttributeError:
            raise AttributeError(f"FootprintLabel.visible is write only in KiCad v{SWIG_version}")

    @visible.setter
    def visible(self, value: bool) -> None:
        self._obj.SetVisible(value)


class FootprintLine(HasLayer, Selectable, BoardItem):
    """Wrapper for `EDGE_MODULE` (old) or `FP_SHAPE`"""
    _wraps_native_cls = SWIGtype.FpShape


def wrap_footprint_item(item: Any) -> Union['FootprintLine', FootprintLabel]:
    if SWIG_version >= 8:
        return wrap_drawing(item)
    else:
        if instanceof(item, SWIGtype.FpShape):
            return FootprintLine.wrap(item)
        elif instanceof(item, SWIGtype.FpText):
            return FootprintLabel.wrap(item)
        raise Exception("Unknown footprint member type: {}".format(type(item)))


class Footprint(HasPosition, HasOrientation, Selectable, BoardItem):
    _ref_label = None
    _val_label = None
    _wraps_native_cls = SWIGtype.Footprint

    def __init__(self, ref: Optional[str] = None, pos: Optional[CoordinateLike] = None, board: Optional['Board'] = None) -> None:
        if not board:
            from kigadgets.board import Board
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
    def load_from_library(library_path: str, name: str) -> Optional['Footprint']:
        mod = pcbnew.FootprintLoad(library_path, name)
        if mod is None:
            return None
        else:
            return Footprint.wrap(mod)

    @property
    def reference(self) -> str:
        return self._obj.GetReference()

    @reference.setter
    def reference(self, value: str) -> None:
        self._obj.SetReference(value)

    @property
    def reference_label(self) -> FootprintLabel:
        """Caches the wrapped FootprintLabel so that subsequent accesses return the same object."""
        native = self._obj.Reference()
        if self._ref_label is None or self._ref_label.native_obj is not native:
            self._ref_label = FootprintLabel.wrap(native)
        return self._ref_label

    @property
    def value(self) -> str:
        return self._obj.GetValue()

    @value.setter
    def value(self, value: str) -> None:
        self._obj.SetValue(value)

    @property
    def value_label(self) -> FootprintLabel:
        """Caches the wrapped FootprintLabel so that subsequent accesses return the same object."""
        native = self._obj.Value()
        if self._val_label is None or self._val_label.native_obj is not native:
            self._val_label = FootprintLabel.wrap(native)
        return self._val_label

    @property
    def graphical_items(self) -> List[Union['FootprintLine', FootprintLabel]]:
        """Text and drawings of module iterator."""
        drawings = self._obj.GraphicalItems()
        return [wrap_footprint_item(item) for item in drawings]

    def flip(self) -> None:
        if SWIG_version >= 7:
            self._obj.Flip(self._obj.GetCenter(), False)
        else:
            self._obj.Flip(self._obj.GetCenter())

    @property
    def layer(self) -> str:
        return get_board_layer_name(self.board, self._obj.GetLayer())

    @layer.setter
    def layer(self, value: str) -> None:
        if value == self.layer:
            return
        if value not in ["F.Cu", "B.Cu"]:
            raise ValueError("You can place a module only on 'F.Cu' or 'B.Cu' layers!")
        # Using flip will make sure all components of the module are
        # switched to correct layer
        self.flip()

    @property
    def lib_name(self) -> str:
        return self._obj.GetFPID().GetLibNickname().GetChars()

    @property
    def fp_name(self) -> str:
        return self._obj.GetFPID().GetLibItemName().GetChars()

    def copy(self, ref: str, pos: Optional[CoordinateLike] = None, board: Optional['Board'] = None) -> 'Footprint':
        """Create a copy of an existing module on the same board
        A new reference designator is required, example::

            mod2 = mod1.copy('U2')
            mod2.reference == 'U2'  # True

        mod2 is automatically placed in mod1.board
        """
        if not board:
            board = self.board
        if SWIG_version >= 7:
            _module = SWIGtype.Footprint(self._obj)
        else:
            _module = SWIGtype.Footprint(board and board._obj)
            _module.Copy(self._obj)
        module = Footprint.wrap(_module)
        module.reference = ref
        if pos:
            module.position = pos
        if board:
            board.add(module)
        return module

    @property
    def pads(self) -> List[Pad]:
        return [Pad.wrap(p) for p in self._obj.Pads()]

    def remove(self, element: Union[Pad, 'FootprintLine', FootprintLabel], permanent: bool = False) -> None:
        """Makes it so Ctrl-Z works.
        Keeps a reference to the element in the python pcb object,
        so it persists for the life of that object
        """
        if not permanent:
            if not hasattr(self, "_removed_elements"):
                self._removed_elements = []
            self._removed_elements.append(element)
        self._obj.Remove(element._obj)

    def restore_removed(self) -> None:
        if hasattr(self, "_removed_elements"):
            for element in self._removed_elements:
                self._obj.Add(element._obj)
        self._removed_elements = []

    def geohash(self) -> int:
        mine = hash((
            self.reference,
            self.value,
            self.layer,
            # self.lib_name,
            self.fp_name
        ))

        child_hashes = []
        for pad in self.pads:
            child_hashes.append(pad.geohash())
        for dwg in self.graphical_items:
            child_hashes.append(dwg.geohash())
        child_hashes.sort()
        mine += hash(tuple(child_hashes))
        return mine + super().geohash()


# In case v5 naming is used
Module = Footprint
ModuleLine = FootprintLine
ModuleLabel = FootprintLabel
