from math import radians, degrees
from kicad.point import Point
from kicad.exceptions import deprecate_member
import kicad.pcbnew.layer as pcbnew_layer

class BoardItem(object):
    _obj = None

    @property
    def native_obj(self):
        return self._obj

    @property
    def board(self):
        from kicad.pcbnew.board import Board
        brd_native = self._obj.GetBoard()
        if brd_native:
            return Board(brd_native)
        else:
            return None


class HasPosition(object):
    """Board items that has valid position property should inherit
    this."""

    def __init__(self):
        raise NotImplementedError("This is an abstract class!")

    @property
    def position(self):
        return Point.wrap(self._obj.GetPosition())

    @position.setter
    def position(self, value):
        self._obj.SetPosition(Point.native_from(value))

    @property
    def x(self):
        return self.position.x

    @x.setter
    def x(self, value):
        self.position = (value, self.y)

    @property
    def y(self):
        return self.position.y

    @y.setter
    def y(self, value):
        self.position = (self.x, value)


class HasRotation(object):
    """Board items that has rotation property should inherit this."""
    def __init__(self):
        raise NotImplementedError("This is an abstract class!")

    @property
    def rotation(self):
        """Rotation of the item in radians."""
        return radians(self._obj.GetOrientation() / 10.)

    @rotation.setter
    def rotation(self, value):
        self._obj.SetOrientation(degrees(value) * 10.)


class HasLayerEnumImpl(object):
    """Board items that has layer should inherit this."""
    def __init__(self):
        raise NotImplementedError("This is an abstract class!")

    @property
    def layer(self):
        return pcbnew_layer.Layer(self._obj.GetLayer())

    @layer.setter
    def layer(self, value):
        self._obj.SetLayer(value.value)


class HasLayer(HasLayerEnumImpl):
    _has_warned = False

    def print_warning(self):
        if not self._has_warned:
            print('\nDeprecation warning (HasLayer): Use either HasLayerEnumImpl or HasLayerStrImpl.'
                  '\nDefault will change from Enum to Str in the future.')
            self._has_warned = True

    @property
    def layer(self):
        self.print_warning()
        return pcbnew_layer.Layer(self._obj.GetLayer())

    @layer.setter
    def layer(self, value):
        self.print_warning()
        self._obj.SetLayer(value.value)


class HasLayerStrImpl(object):
    """ Board items that has layer outside of standard layers should inherit this.
        String implementation can sometimes be more intuitive, and accomodates custom layer names.
        If the layer is not present, it will be caught at runtime, rather than disallowed.
    """
    def __init__(self):
        raise NotImplementedError("This is an abstract class!")

    @property
    def layer(self):
        layid = self._obj.GetLayer()
        try:
            brd = self.board
        except AttributeError:
            from kicad.pcbnew.board import Board
            native = self._obj.GetBoard()
            brd = Board(native) if native else None
        return pcbnew_layer.get_board_layer_name(brd, layid)

    @layer.setter
    def layer(self, value):
        try:
            brd = self.board
        except AttributeError:
            from kicad.pcbnew.board import Board
            native = self._obj.GetBoard()
            brd = Board(native) if native else None
        layid = pcbnew_layer.get_board_layer_id(brd, value)
        self._obj.SetLayer(layid)


@deprecate_member('netName', 'net_name')
@deprecate_member('netCode', 'net_code')
class HasConnection(object):
    """All BOARD_CONNECTED_ITEMs should inherit this."""
    def __init__(self):
        raise NotImplementedError("This is an abstract class!")

    @property
    def net_name(self):
        return self._obj.GetNetname()

    @net_name.setter
    def net_name(self, value):
        """ Takes a name and attempts to look it up based on the containing board """
        if not self._obj:
            raise TypeError("Cannot set net_name without a containing Board.")
        try:
            new_code = self._obj.GetBoard().GetNetcodeFromNetname(value)
        except IndexError:
            raise KeyError("Net name '{}' not found in board nets.".format(value))
        self._obj.SetNetCode(new_code)

    @property
    def net_code(self):
        return self._obj.GetNetCode()

    @net_code.setter
    def net_code(self, value):
        self._obj.SetNetCode(value)


class Selectable(object):
    """ This influences the main window. Make sure to pcbnew.Refresh() to see it """
    def __init__(self):
        raise NotImplementedError("This is an abstract class!")

    @property
    def is_selected(self):
        return bool(self._obj.IsSelected())

    def select(self, value=True):
        """ Selecting changes the appearance and also plays a role in determining
            what will be the subject of a subsequent command (delete, move to layer, etc.)
        """
        if value:
            self._obj.SetSelected()
        else:
            self._obj.ClearSelected()

    def deselect(self):
        self.select(False)

    def brighten(self, value=True):
        """ Brightening gives a bright green appearance """
        if value:
            self._obj.SetBrightened()
        else:
            self._obj.ClearBrightened()


class HasWidth(object):
    @property
    def width(self):
        return float(self._obj.GetWidth()) / units.DEFAULT_UNIT_IUS

    @width.setter
    def width(self, value):
        self._obj.SetWidth(int(value * units.DEFAULT_UNIT_IUS))
