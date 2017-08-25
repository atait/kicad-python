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
pcbnew = __import__('pcbnew')
import kicad

from enum import IntEnum

class Layer(IntEnum):
    Front           = pcbnew.F_Cu
    Back            = pcbnew.B_Cu

    FrontAdhesive   = pcbnew.F_Adhes
    BackAdhesive    = pcbnew.B_Adhes
    FrontSilkScreen = pcbnew.F_SilkS
    BackSilkScreen  = pcbnew.B_SilkS
    FrontPaste      = pcbnew.F_Paste
    BackPaste       = pcbnew.B_Paste
    FrontMask       = pcbnew.F_Mask
    BackMask        = pcbnew.B_Mask

    EdgeCuts        = pcbnew.Edge_Cuts
    FrontCourtyard  = pcbnew.F_CrtYd
    BackCourtyard   = pcbnew.B_CrtYd

    # TODO: add all layer names

# dicts for converting layer name to id, used by _get_layer
_std_layer_dict = {pcbnew.BOARD_GetStandardLayerName(n): n
                   for n in range(pcbnew.PCB_LAYER_ID_COUNT)}
_std_layer_names = {s: n for n, s in _std_layer_dict.iteritems()}


def get_board_layer(board, layer_name):
    """Get layer id for layer name in board, or std."""
    if board:
        return board.get_layer(layer_name)
    else:
        return get_std_layer(layer_name)


def get_board_layer_name(board, layer_id):
    """Get layer name for layer_id in board, or std."""
    if board:
        return board.get_layer_name(layer_id)
    else:
        return get_std_layer_name(layer_id)


def get_std_layer_name(layer_id):
    """Get layer name from layer id. """
    return _std_layer_names[layer_id]


def get_std_layer(layer_name):
    """Get layer id from layer name

    If it is already an int just return it.
    """
    return _std_layer_dict[layer_name]


class LayerSet:
    def __init__(self, layer_names, board=None):
        self._board = board
        self._build_layer_set(layer_names)

    @property
    def native_obj(self):
        return self._obj

    @staticmethod
    def wrap(instance):
        """Wraps a C++/old api LSET object, and returns a LayerSet."""
        return kicad.new(LayerSet, instance)

    def _build_layer_set(self, layers):
        """Create LayerSet used for defining pad layers"""
        bit_mask = 0
        for layer_name in layers:
            if self._board:
                bit_mask |= 1 << self._board.get_layer(layer_name)
            else:
                bit_mask |= 1 << get_std_layer(layer_name)
        hex_mask = '{0:013x}'.format(bit_mask)
        self._obj = pcbnew.LSET()
        self._obj.ParseHex(hex_mask, len(hex_mask))

    @property
    def layer_names(self):
        """Returns the list of layer names in this LayerSet."""
        return [get_board_layer_name(self._board, layer_id)
                for layer_id in self.layers]

    @property
    def layers(self):
        """Returns the list of Layer IDs in this LayerSet."""
        layer_ids = []
        bin_str = self._obj.FmtBin().replace('_', '').replace('|', '')
        bit_pos = len(bin_str) - 1
        for bit in bin_str:
            if bit == '1':
                layer_ids.append(bit_pos)
            bit_pos -= 1
        return layer_ids
