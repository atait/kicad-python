from kigadgets import pcbnew_bare as pcbnew

import kigadgets
from kigadgets import SWIGtype, SWIG_version, Point, DEFAULT_UNIT_IUS
from kigadgets.item import HasPosition, HasConnection, Selectable, BoardItem
from kigadgets.layer import get_std_layer_id, get_std_layer_name

if SWIG_version >= 6:
    class ViaType():
        Through = pcbnew.VIATYPE_THROUGH
        Micro = pcbnew.VIATYPE_MICROVIA
        Blind = pcbnew.VIATYPE_BLIND_BURIED
else:
    class ViaType():
        Through = pcbnew.VIA_THROUGH
        Micro = pcbnew.VIA_MICROVIA
        Blind = pcbnew.VIA_BLIND_BURIED


class Via(HasPosition, HasConnection, Selectable, BoardItem):
    def __init__(self, coord, layer_pair, diameter, drill, board=None):
        self._obj = SWIGtype.Via(board and board.native_obj)
        self.diameter = diameter
        coord_point = Point.build_from(coord)
        self._obj.SetEnd(coord_point.native_obj)
        self._obj.SetStart(coord_point.native_obj)
        if board:
            self._obj.SetLayerPair(board.get_layer_id(layer_pair[0]),
                                   board.get_layer_id(layer_pair[1]))
        else:
            self._obj.SetLayerPair(get_std_layer_id(layer_pair[0]),
                                   get_std_layer_id(layer_pair[1]))
        self.drill = drill

    @staticmethod
    def wrap(instance):
        """Wraps a C++ api VIA object, and returns a `Via`."""
        return kigadgets.new(Via, instance)

    @property
    def drill(self):
        """Via drill diameter"""
        return float(self._obj.GetDrill()) / DEFAULT_UNIT_IUS

    @drill.setter
    def drill(self, value):
        self._obj.SetDrill(int(value * DEFAULT_UNIT_IUS))

    @property
    def diameter(self):
        """Via diameter"""
        return float(self._obj.GetWidth()) / DEFAULT_UNIT_IUS

    @diameter.setter
    def diameter(self, value):
        self._obj.SetWidth(int(value * DEFAULT_UNIT_IUS))

    @property
    def center(self):
        """Via center"""
        return Point.wrap(self._obj.GetCenter())

    @center.setter
    def center(self, value):
        self._obj.SetCenter(Point.native_from(value))

    @property
    def top_layer(self):
        if self.board:
            return self.board.get_layer_name(self._obj.TopLayer())
        else:
            return get_std_layer_name(self._obj.TopLayer())

    @top_layer.setter
    def top_layer(self, value):
        if self.board:
            self._obj.SetTopLayer(self.board.get_layer_id(value))
        else:
            self._obj.SetTopLayer(get_std_layer_id(value))

    @property
    def bottom_layer(self):
        if self.board:
            return self.board.get_layer_name(self._obj.BottomLayer())
        else:
            return get_std_layer_name(self._obj.BottomLayer())

    @bottom_layer.setter
    def bottom_layer(self, value):
        if self.board:
            self._obj.SetTopLayer(self.board.get_layer_id(value))
        else:
            self._obj.SetTopLayer(get_std_layer_name(value))

    @property
    def is_through(self):
        return self._obj.GetViaType() == ViaType.Through
        # self._obj.GetViaType() in [ViaType.Micro, ViaType.Blind]

    @is_through.setter
    def is_through(self, value):
        if value:
            self._obj.SetViaType(ViaType.Through)
        else:
            self._obj.SetViaType(ViaType.Blind)
