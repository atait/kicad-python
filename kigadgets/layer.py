from kigadgets import pcbnew_bare as pcbnew
import kigadgets
from kigadgets import SWIG_version, instanceof

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
        _std_layer_dict = {native_get_layername(n): n for n in range(pcbnew.PCB_LAYER_ID_COUNT)}
        try:
            # For backwards compatibility with silkscreen renames
            _std_layer_dict["F.SilkS"] = _std_layer_dict["F.Silkscreen"]
            _std_layer_dict["B.SilkS"] = _std_layer_dict["B.Silkscreen"]
        except KeyError:
            # Forwards compatibility
            _std_layer_dict["F.Silkscreen"] = _std_layer_dict["F.SilkS"]
            _std_layer_dict["B.Silkscreen"] = _std_layer_dict["B.SilkS"]
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
    """Get layer name from layer id."""
    load_std_layers()
    return _std_layer_names[layer_id]


def get_std_layer_id(layer_name):
    """Get layer id from layer name

    If it is already an int just return it.
    """
    load_std_layers()
    return _std_layer_dict[layer_name]


class LayerSet:

    _wraps_native_cls = pcbnew.LSET

    def __init__(self, layer_names, board=None):
        self._board = board
        self._build_layer_set(layer_names)

    @property
    def native_obj(self):
        return self._obj

    @classmethod
    def wrap(cls, instance):
        if cls._wraps_native_cls and not instanceof(instance, cls._wraps_native_cls):
            raise TypeError(
                f"{cls.__name__} cannot wrap native class {type(instance).__name__}.\n"
                f"Allowed: {cls._wraps_native_cls}"
            )
        return kigadgets.new(cls, instance)

    def _build_layer_set(self, layers):
        """Create LayerSet used for defining pad layers"""
        bit_mask = 0
        for layer_name in layers:
            bit_mask |= 1 << get_board_layer_id(self._board, layer_name)
        hex_mask = "{0:013x}".format(bit_mask)
        self._obj = pcbnew.LSET()
        self._obj.ParseHex(hex_mask, len(hex_mask))

    @property
    def layers(self):
        """Returns the list of Layer names in this LayerSet."""
        return [get_board_layer_name(self._board, lay_id) for lay_id in self._obj.Seq()]

    @layers.setter
    def layers(self, new_lylist):
        for layer_name in self.layers:
            self.remove_layer(layer_name)
        for layer_name in new_lylist:
            self.add_layer(layer_name)

    def add_layer(self, layer_name):
        self._obj.AddLayer(get_board_layer_id(self._board, layer_name))
        return self

    def remove_layer(self, layer_name):
        if layer_name not in self.layers:
            raise KeyError(f"Layer {layer_name} not present in {self.layer_names}")
        self._obj.RemoveLayer(get_board_layer_id(self._board, layer_name))
        return self
