from kigadgets import pcbnew_bare as pcbnew

import kigadgets
from kigadgets import SWIGtype, SWIG_version, Point, DEFAULT_UNIT_IUS, instanceof
from kigadgets.item import HasConnection, HasLayer, Selectable, BoardItem
from kigadgets.layer import LayerSet, get_board_layer_id
from kigadgets.drawing import Polygon


class RuleArea(Selectable, BoardItem):
    _wraps_native_cls = SWIGtype.Zone

    def __init__(self, coords, name="", layers=None, board=None):
        raise NotImplementedError("kigadgets Zone instantiation through __init__ not supported. Wrap an existing pcbnew Zone")
        if board is None:
            raise RuntimeError(f"{type(self).__name__} must be given a board argument that is not None")
        if type(self) is RuleArea:
            raise NotImplementedError("RuleArea is an abstract class. Instantiate using Zone(...) or Keepout(...)")
        if layers is None:
            layers = ["F.Cu"]
        if not isinstance(layers, (list, tuple)):
            layers = [layers]
        self._obj = SWIGtype.Zone(board and board.native_obj)
        self.name = name
        self.layers = layers

    @classmethod
    def wrap(cls, instance):
        if cls._wraps_native_cls and not instanceof(instance, cls._wraps_native_cls):
            raise TypeError(
                f"{cls.__name__} cannot wrap native class {type(instance).__name__}.\n"
                f"Allowed: {cls._wraps_native_cls}"
            )
        if SWIG_version >= 6:
            is_keepout = bool(instance.GetIsRuleArea())
        else:
            is_keepout = bool(instance.GetIsKeepout())
        if is_keepout:
            return kigadgets.new(Keepout, instance)
        else:
            return kigadgets.new(Zone, instance)

    @property
    def name(self):
        return self._obj.GetZoneName()

    @name.setter
    def name(self, val):
        self._obj.SetZoneName(val)

    @property
    def layerset(self):
        """Zones can have multiple layers
        Changing this layerset will not propagate back to this zone
        until you set layerset again. Common pattern::

            zone.layerset = zone.layerset.add_layer('F.Cu')
        """
        lset = LayerSet.wrap(self._obj.GetLayerSet())
        lset._board = self.board
        return lset

    @layerset.setter
    def layerset(self, new_lset):
        self._obj.SetLayerSet(new_lset._obj)

    @property
    def layer(self):
        raise RuntimeError(
            "Zone does not have a valid layer because there might be multiple layers. "
            'Use "zone.layers" property instead for lists of strings, '
            'or use "zone.layerset" to interact with LayerSet.add_layer and LayerSet.remove_layer'
        )

    @property
    def layers(self):
        return self.layerset.layers

    @layers.setter
    def layers(self, new_lylist):
        self.layerset.layers = new_lylist

    @classmethod
    def from_polygon(cls, poly, **zkws):
        coords = poly.get_vertices()
        return cls(coords, **zkws)

    def to_polygon(self, layer="Margin"):
        poly = self._obj.Outline()
        return Polygon._from_polyset(poly, multiple=False, layer=layer, board=self.board)

    @property
    def is_keepout(self):
        if SWIG_version >= 6:
            return bool(self._obj.GetIsRuleArea())
        else:
            return bool(self._obj.GetIsKeepout())

    def _set_is_keepout(self, value):
        if SWIG_version >= 6:
            self._obj.SetIsRuleArea(bool(value))
        else:
            self._obj.SetIsKeepout(bool(value))


class Zone(RuleArea, HasConnection):
    def __init__(self, coords, name="", layers=None, board=None):
        RuleArea.__init__(self, coords, name=name, layers=layers, board=board)
        self._set_is_keepout(False)

    @property
    def clearance(self):
        if SWIG_version >= 7:
            native = self._obj.GetLocalClearance()
        else:
            native = self._obj.GetClearance()
        return float(native) / DEFAULT_UNIT_IUS

    @clearance.setter
    def clearance(self, value):
        if SWIG_version >= 7:
            self._obj.SetLocalClearance(int(value * DEFAULT_UNIT_IUS))
        else:
            self._obj.SetClearance(int(value * DEFAULT_UNIT_IUS))
            self._obj.SetZoneClearance(int(value * DEFAULT_UNIT_IUS))

    @property
    def priority(self):
        return self._obj.GetAssignedPriority()

    @priority.setter
    def priority(self, val):
        self._obj.SetAssignedPriority(int(val))

    @property
    def min_width(self):
        return float(self._obj.GetMinThickness()) / DEFAULT_UNIT_IUS

    @min_width.setter
    def min_width(self, value):
        self._obj.SetMinThickness(int(value * DEFAULT_UNIT_IUS))

    @property
    def filled_area(self):
        """The area of all poured polygons, not the zone outline polygon
        Returns in units of square mm
        """
        native = self._obj.GetFilledArea()
        return float(native) / DEFAULT_UNIT_IUS**2

    def get_fill_polygons(self):
        """Returns polygons on all layers. The Polygons have corresponding layers"""
        all_polys = []
        for lay in self.layers:
            layid = get_board_layer_id(self.board, lay)
            polys_native = self._obj.GetFilledPolysList(layid)
            polys = Polygon._from_polyset(polys_native, multiple=True, layer=lay, board=self.board)
            all_polys += polys
        return all_polys

    def geohash(self):
        fill_hashes = []
        for poly in self.get_fill_polygons():
            fill_hashes.append(poly.geohash())
        mine = hash((
            self.name,
            self.priority,
            self.clearance,
            self.min_width,
            tuple(sorted(self.layers)),
            self.to_polygon().geohash(),
            tuple(sorted(fill_hashes)),
        ))
        return mine + super().geohash()


class _KeepoutAllowance(object):
    """Gives key-value and dot interfaces of the form

    zz.is_keepout = True
    zz.allow['tracks'] = False
    print(my_zone.allow.tracks)
    """
    def __init__(self, zone):
        self._zone = zone

    @property
    def tracks(self):
        return not self._zone._obj.GetDoNotAllowTracks()

    @tracks.setter
    def tracks(self, value):
        self._zone._obj.SetDoNotAllowTracks(not bool(value))

    @property
    def pour(self):
        return not self._zone._obj.GetDoNotAllowCopperPour()

    @pour.setter
    def pour(self, value):
        self._zone._obj.SetDoNotAllowCopperPour(not bool(value))

    @property
    def vias(self):
        return not self._zone._obj.GetDoNotAllowVias()

    @vias.setter
    def vias(self, value):
        self._zone._obj.SetDoNotAllowVias(not bool(value))

    @property
    def footprints(self):
        return not self._zone._obj.GetDoNotAllowFootprints()

    @footprints.setter
    def footprints(self, value):
        self._zone._obj.SetDoNotAllowFootprints(not bool(value))

    def __getitem__(self, attr):
        return getattr(self, attr)

    def __setitem__(self, attr, value):
        setattr(self, attr, value)

    def __str__(self):
        return str({k: self[k] for k in ["tracks", "pour", "vias", "footprints"]})

    def __repr__(self):
        return type(self).__name__ + str(self)


class Keepout(RuleArea):
    def __init__(self, coords, name="", layers=None, board=None):
        RuleArea.__init__(self, coords, name=name, layers=layers, board=board)
        self._set_is_keepout(True)

    @property
    def allow(self):
        return _KeepoutAllowance(self)

    def geohash(self):
        mine = hash((
            self.name,
            (self.allow.tracks, self.allow.pour, self.allow.vias),
            tuple(sorted(self.layers))
        ))
        return mine + super().geohash()
