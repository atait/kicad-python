from kicad import pcbnew_bare as pcbnew, SWIG_version
import kicad

class Layer():
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

# dicts for converting layer name to id, used by _get_layer
_std_layer_dict = None
_std_layer_names = None
def load_std_layers():
    # lazy import for Sphinx to run properly
    global _std_layer_dict, _std_layer_names
    if _std_layer_dict is None:
        if SWIG_version >= 7:
            native_get_layername = pcbnew.BOARD.GetStandardLayerName
        else:
            native_get_layername = pcbnew.BOARD_GetStandardLayerName
        _std_layer_dict = {native_get_layername(n): n
                           for n in range(pcbnew.PCB_LAYER_ID_COUNT)}
        try:
            # For backwards compatibility with silkscreen renames
            _std_layer_dict['F.SilkS'] = _std_layer_dict['F.Silkscreen']
            _std_layer_dict['B.SilkS'] = _std_layer_dict['B.Silkscreen']
        except KeyError:
            # Forwards compatibility
            _std_layer_dict['F.Silkscreen'] = _std_layer_dict['F.SilkS']
            _std_layer_dict['B.Silkscreen'] = _std_layer_dict['B.SilkS']
    if _std_layer_names is None:
        _std_layer_names = {s: n for n, s in _std_layer_dict.items()}


def get_board_layer_id(board, layer_name):
    """Get layer id for layer name in board, or std."""
    if board:
        return board.get_layer_id(layer_name)
    else:
        return get_std_layer_id(layer_name)


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


def get_std_layer_id(layer_name):
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
                bit_mask |= 1 << self._board.get_layer_id(layer_name)
            else:
                bit_mask |= 1 << get_std_layer_id(layer_name)
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

    def add_layer(self, layer_name):
        self._obj.AddLayer(get_board_layer_id(self._board, layer_name))
        return self

    def remove_layer(self, layer_name):
        if layer_name not in self.layer_names:
            raise KeyError('Layer {} not present in {}'.format(layer_name, self.layer_names))
        self._obj.RemoveLayer(get_board_layer_id(self._board, layer_name))
        return self
