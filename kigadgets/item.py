from math import radians, degrees
from kicad import units, SWIG_version
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
        """Rotation of the item in degrees."""
        if SWIG_version >= 7:
            return float(self._obj.GetOrientationDegrees())
        else:
            return float(self._obj.GetOrientation()) / 10

    @rotation.setter
    def rotation(self, value):
        if SWIG_version >= 7:
            self._obj.SetOrientationDegrees(value)
        else:
            self._obj.SetOrientation(value * 10.)


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


class TextEsque(object):
    # Note orientation and rotation mean different things
    @property
    def text(self):
        return self._obj.GetText()

    @text.setter
    def text(self, value):
        return self._obj.SetText(value)

    @property
    def thickness(self):
        if SWIG_version >= 7:
            return float(self._obj.GetTextThickness()) / units.DEFAULT_UNIT_IUS
        else:
            return float(self._obj.GetThickness()) / units.DEFAULT_UNIT_IUS

    @thickness.setter
    def thickness(self, value):
        if SWIG_version >= 7:
            return self._obj.SetTextThickness(int(value * units.DEFAULT_UNIT_IUS))
        else:
            return self._obj.SetThickness(int(value * units.DEFAULT_UNIT_IUS))

    @property
    def size(self):
        return Size.wrap(self._obj.GetTextSize())

    @size.setter
    def size(self, value):
        try:
            size = Size.build_from(value)
        except TypeError:
            size = Size.build_from((value, value))
        self._obj.SetTextSize(size.native_obj)

    @property
    def orientation(self):
        return self._obj.GetTextAngle() / 10

    @orientation.setter
    def orientation(self, value):
        self._obj.SetTextAngle(value * 10)

    @property
    def justification(self):
        hj = self._obj.GetHorizJustify()
        vj = self._obj.GetVertJustify()
        for k, v in justification_lookups.items():
            if hj == getattr(pcbnew, v):
                hjs = k
            if vj in getattr(pcbnew, v):
                vjs = k
        return hjs, vjs

    @justification.setter
    def justification(self, value):
        if isinstance(value, (list, tuple)):
            assert len(value) == 2
            self.justification = value[0]
            self.justification = value[1]
        else:
            try:
                token = justification_lookups[value]
            except KeyError:
                raise ValueError('Invalid justification {} of available {}'.format(value, list(justification_lookups.keys())))
            enum_val = getattr(pcbnew, token)
            if 'HJUSTIFY' in token:
                self._obj.SetHorizJustify(enum_val)
            else:
                self._obj.SetVertJustify(enum_val)

justification_lookups = dict(
    left='GR_TEXT_HJUSTIFY_LEFT',
    center='GR_TEXT_HJUSTIFY_CENTER',
    right='GR_TEXT_HJUSTIFY_RIGHT',
    bottom='GR_TEXT_VJUSTIFY_BOTTOM',
    middle='GR_TEXT_VJUSTIFY_CENTER',
    top='GR_TEXT_VJUSTIFY_TOP',
)
