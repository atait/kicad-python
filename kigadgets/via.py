from kigadgets import pcbnew_bare as pcbnew

from kigadgets import SWIGtype, SWIG_version, Point, DEFAULT_UNIT_IUS
from kigadgets.item import HasPosition, HasConnection, Selectable, BoardItem
from kigadgets.layer import get_board_layer_id, get_board_layer_name

if SWIG_version >= 6:
    class ViaType:
        Through = pcbnew.VIATYPE_THROUGH
        Micro = pcbnew.VIATYPE_MICROVIA
        Blind = pcbnew.VIATYPE_BLIND_BURIED
else:
    class ViaType:
        Through = pcbnew.VIA_THROUGH
        Micro = pcbnew.VIA_MICROVIA
        Blind = pcbnew.VIA_BLIND_BURIED


class Via(HasPosition, HasConnection, Selectable, BoardItem):
    """Careful setting top_layer, then getting top_layer may
    return different values if the new top_layer is below the existing bottom layer
    """
    _wraps_native_cls = SWIGtype.Via

    def __init__(self, center, size=None, drill=None, layer_pair=None, board=None):
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
    def drill(self):
        """Via drill diameter"""
        return float(self._obj.GetDrill()) / DEFAULT_UNIT_IUS

    @drill.setter
    def drill(self, value):
        self._obj.SetDrill(int(value * DEFAULT_UNIT_IUS))

    @property
    def size(self):
        """Via diameter"""
        return float(self._obj.GetWidth()) / DEFAULT_UNIT_IUS

    @size.setter
    def size(self, value):
        self._obj.SetWidth(int(value * DEFAULT_UNIT_IUS))

    @property
    def center(self):
        """Via center"""
        try:
            return Point.wrap(self._obj.GetStart())
        except AttributeError:
            return Point.wrap(self._obj.GetCenter())

    @center.setter
    def center(self, value):
        try:
            self._obj.SetEnd(Point.native_from(value))
            self._obj.SetStart(Point.native_from(value))
        except AttributeError:
            self._obj.SetCenter(Point.native_from(value))

    def set_layer_pair(self, layer_pair):
        try:
            if len(layer_pair) != 2:
                raise TypeError
            if layer_pair[0] == layer_pair[1]:
                raise TypeError
        except TypeError:
            raise TypeError("layer_pair must have two uniqe layers as strings")
        self.top_layer = layer_pair[0]
        self.bottom_layer = layer_pair[1]

    def get_layer_pair_hash(self):
        layer_pair = self.top_layer, self.bottom_layer
        sorting_key = lambda name: get_board_layer_id(self.board, name)
        sorted_pair = sorted(layer_pair, key=sorting_key)
        return hash(tuple(sorted_pair))

    @property
    def top_layer(self):
        return get_board_layer_name(self.board, self._obj.TopLayer())

    @top_layer.setter
    def top_layer(self, value):
        assert value.endswith(".Cu")
        self._obj.SetTopLayer(get_board_layer_id(self.board, value))
        if value.startswith("In"):
            self.is_through = False

    @property
    def bottom_layer(self):
        return get_board_layer_name(self.board, self._obj.BottomLayer())

    @bottom_layer.setter
    def bottom_layer(self, value):
        assert value.endswith(".Cu")
        self._obj.SetBottomLayer(get_board_layer_id(self.board, value))
        if value.startswith("In"):
            self.is_through = False

    @property
    def is_through(self):
        return self._obj.GetViaType() == ViaType.Through

    @is_through.setter
    def is_through(self, value):
        if value:
            self._obj.SetViaType(ViaType.Through)
        else:
            self._obj.SetViaType(ViaType.Blind)

    def geohash(self):
        mine = hash((
            self.drill,
            self.size,
            self.center,
            self.get_layer_pair_hash(),
            self.is_through,
        ))
        return mine + super().geohash()
