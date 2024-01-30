from kigadgets import pcbnew_bare as pcbnew

import kigadgets
from kigadgets import SWIGtype, SWIG_version, Point, DEFAULT_UNIT_IUS
from kigadgets.item import HasConnection, HasLayer, Selectable, BoardItem
from kigadgets.layer import LayerSet

class KeepoutAllowance(object):
    """ Gives key-value and dot interfaces of the form
            zz.is_keepout = True
            zz.allow['tracks'] = False
            print(my_zone.allow.tracks)
    """
    def __init__(self, zone):
        super().__setattr__('_zone', zone)
        # self._zone = zone

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

    def __getitem__(self, attr):
        return getattr(self, attr)

    def __setitem__(self, attr, value):
        setattr(self, attr, value)

    def __str__(self):
        return str({k: self[k] for k in ['tracks', 'pour', 'vias']})

    def __repr__(self):
        return type(self).__name__ + str(self)


class Zone(HasConnection, Selectable, BoardItem):
    _wraps_native_cls = SWIGtype.Zone

    def __init__(self, layer='F.Cu', board=None):
        self._obj = SWIGtype.Zone(board and board.native_obj)
        raise NotImplementedError('Constructor not supported yet')
        self.layer = layer

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
    def min_width(self):
        return float(self._obj.GetMinThickness()) / DEFAULT_UNIT_IUS

    @min_width.setter
    def min_width(self, value):
        self._obj.SetMinThickness(int(value * DEFAULT_UNIT_IUS))

    @property
    def is_keepout(self):
        if SWIG_version >= 6:
            return bool(self._obj.GetIsRuleArea())
        else:
            return bool(self._obj.GetIsKeepout())

    @is_keepout.setter
    def is_keepout(self, value):
        if SWIG_version >= 6:
            self._obj.SetIsRuleArea(bool(value))
        else:
            self._obj.SetIsKeepout(bool(value))

    @property
    def allow(self):
        return KeepoutAllowance(self)

    def delete(self):
        self._obj.DeleteStructure()

    @property
    def layerset(self):
        ''' For zones with multiple layers
            Changing this layerset will not propagate back to this zone
            until you set layerset again. Common pattern::

                zone.layerset = zone.layerset.add_layer('F.Cu')
        '''
        lset = LayerSet.wrap(self._obj.GetLayerSet())
        lset._board = self.board
        return lset

    @layerset.setter
    def layerset(self, new_lset):
        self._obj.SetLayerSet(new_lset._obj)

    @property
    def layer(self):
        raise RuntimeError(
            'Zone does not have a valid layer because there might be multiple layers. '
            'Use "zone.layers" property instead for lists of strings, '
            'or use "zone.layerset" to interact with LayerSet.add_layer and LayerSet.remove_layer')

    @property
    def layers(self):
        return self.layerset.layers

    @layers.setter
    def layers(self, new_lylist):
        self.layerset.layers = new_lylist

    def geohash(self):
        hash((
            self.clearance,
            self.min_width,
            self.is_keepout,
            str(self.allow),
            self.layerset.layers
        ))
        return mine + super().geohash()

# GetCornerSmoothingType
# GetDefaultHatchPitch

# GetThermalReliefCopperBridge
# GetThermalReliefGap

# Outline
# RawPolysList
