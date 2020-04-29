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
from kicad import pcbnew_bare as pcbnew
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

    DrawingsUser    = pcbnew.Dwgs_User
    CommentsUser    = pcbnew.Cmts_User
    ECO1User        = pcbnew.Eco1_User
    ECO2User        = pcbnew.Eco2_User

    EdgeCuts        = pcbnew.Edge_Cuts
    Margin          = pcbnew.Margin
    FrontFab        = pcbnew.F_Fab
    BackFab         = pcbnew.B_Fab
    FrontCourtyard  = pcbnew.F_CrtYd
    BackCourtyard   = pcbnew.B_CrtYd

    # TODO: add inner layer names

# dicts for converting layer name to id, used by _get_layer
_std_layer_dict = None
_std_layer_names = None
def load_std_layers():
    # lazy import for Sphinx to run properly
    global _std_layer_dict, _std_layer_names
    if _std_layer_dict is None:
        _std_layer_dict = {pcbnew.BOARD_GetStandardLayerName(n): n
                           for n in range(pcbnew.PCB_LAYER_ID_COUNT)}
    if _std_layer_names is None:
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
    load_std_layers()
    return _std_layer_names[layer_id]


def get_std_layer(layer_name):
    """Get layer id from layer name

    If it is already an int just return it.
    """
    load_std_layers()
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
        return [l for l in self._obj.Seq()]
