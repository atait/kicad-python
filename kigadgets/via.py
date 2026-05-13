from kigadgets import pcbnew_bare as pcbnew

from kigadgets import SWIGtype, SWIG_version, Point, DEFAULT_UNIT_IUS
from kigadgets.item import HasPosition, HasConnection, Selectable, BoardItem
from kigadgets.layer import get_board_layer_id, get_board_layer_name
from kigadgets.units import CoordinateLike
from typing import Optional, List, Tuple, Any, Union

if SWIG_version >= 6:
    class ViaType:
        Through = pcbnew.VIATYPE_THROUGH
        Micro = pcbnew.VIATYPE_MICROVIA
        # KiCad <10 had a combined BLIND_BURIED; KiCad 10+ split it into two.
        Blind = getattr(pcbnew, "VIATYPE_BLIND_BURIED", getattr(pcbnew, "VIATYPE_BLIND", None))
        Buried = getattr(pcbnew, "VIATYPE_BURIED", Blind)
else:
    class ViaType:
        Through = pcbnew.VIA_THROUGH
        Micro = pcbnew.VIA_MICROVIA
        Blind = pcbnew.VIA_BLIND_BURIED
        Buried = Blind


class Via(HasPosition, HasConnection, Selectable, BoardItem):
    """Careful setting top_layer, then getting top_layer may
    return different values if the new top_layer is below the existing bottom layer
    """
    _wraps_native_cls = SWIGtype.Via

    def __init__(self, center: CoordinateLike, size: Optional[float] = None, drill: Optional[float] = None, layer_pair: Optional[List[str]] = None, board: Optional['Board'] = None) -> None:
        self._obj = SWIGtype.Via(board and board.native_obj)
        if size is None:
            size = self.board.default_via_size if self.board else 0.6
        if drill is None:
            drill = self.board.default_via_drill if self.board else 0.3
        self.center = center
        self.size = size
        self.drill = drill

        if layer_pair is None:
            layer_pair = ["F.Cu", "B.Cu"]
        self.is_through = "F.Cu" in layer_pair and "B.Cu" in layer_pair
        self.set_layer_pair(layer_pair)

    @property
    def drill(self) -> float:
        """Via drill diameter"""
        return float(self._obj.GetDrill()) / DEFAULT_UNIT_IUS

    @drill.setter
    def drill(self, value: float) -> None:
        self._obj.SetDrill(int(value * DEFAULT_UNIT_IUS))

    @property
    def size(self) -> float:
        """Via diameter"""
        if SWIG_version >= 9:
            alayer = get_board_layer_id(self.board, self.top_layer)
            return float(self._obj.GetWidth(alayer)) / DEFAULT_UNIT_IUS
        else:
            return float(self._obj.GetWidth()) / DEFAULT_UNIT_IUS

    @size.setter
    def size(self, value):
        if SWIG_version >= 9:
            alayer = get_board_layer_id(self.board, self.top_layer)
            self._obj.SetWidth(alayer, int(value * DEFAULT_UNIT_IUS))
            alayer = get_board_layer_id(self.board, self.bottom_layer)
            self._obj.SetWidth(alayer, int(value * DEFAULT_UNIT_IUS))
        else:
            self._obj.SetWidth(int(value * DEFAULT_UNIT_IUS))

    width = size
    diameter = size

    @property
    def center(self) -> Point:
        """Via center"""
        try:
            return Point.wrap(self._obj.GetStart())
        except AttributeError:
            return Point.wrap(self._obj.GetCenter())

    @center.setter
    def center(self, value: CoordinateLike) -> None:
        try:
            self._obj.SetEnd(Point.native_from(value))
            self._obj.SetStart(Point.native_from(value))
        except AttributeError:
            self._obj.SetCenter(Point.native_from(value))

    def set_layer_pair(self, layer_pair: Union[Tuple[str, str], List[str]]) -> None:
        layer_pair = self._normalize_layer_pair(layer_pair)
        self.top_layer = layer_pair[0]
        self.bottom_layer = layer_pair[1]

    def _normalize_layer_pair(self, layer_pair: Union[Tuple[str, str], List[str]]):
        """Normalizes layer pair to ensure consistent hashing regardless of order."""
        try:
            if len(layer_pair) != 2:
                raise TypeError
            if layer_pair[0] == layer_pair[1]:
                raise TypeError
        except TypeError:
            raise TypeError("layer_pair must have two uniqe layers as strings")
        sorting_key = lambda name: get_board_layer_id(self.board, name)
        sorted_pair = sorted(layer_pair, key=sorting_key)
        return tuple(sorted_pair)

    def get_layer_pair_hash(self) -> int:
        normalized = self._normalize_layer_pair((self.top_layer, self.bottom_layer))
        return hash(normalized)

    @property
    def top_layer(self) -> str:
        return get_board_layer_name(self.board, self._obj.TopLayer())

    @top_layer.setter
    def top_layer(self, value: str) -> None:
        assert value.endswith(".Cu")
        self._obj.SetTopLayer(get_board_layer_id(self.board, value))
        if value.startswith("In"):
            self.is_through = False

    @property
    def bottom_layer(self) -> str:
        return get_board_layer_name(self.board, self._obj.BottomLayer())

    @bottom_layer.setter
    def bottom_layer(self, value: str) -> None:
        assert value.endswith(".Cu")
        self._obj.SetBottomLayer(get_board_layer_id(self.board, value))
        if value.startswith("In"):
            self.is_through = False

    @property
    def is_through(self) -> bool:
        """Returns False if it's a blind via OR microvia."""
        return self._obj.GetViaType() == ViaType.Through

    @is_through.setter
    def is_through(self, value: bool) -> None:
        """ thing.is_through = False results in a blind via (not a microvia)
        """
        if value:
            self._obj.SetViaType(ViaType.Through)
        else:
            self._obj.SetViaType(ViaType.Blind)

    def geohash(self) -> int:
        mine = hash((
            self.drill,
            self.size,
            self.center,
            self.get_layer_pair_hash(),
            self.is_through,
        ))
        return mine + super().geohash()
