import kigadgets
from kigadgets import SWIG_version, Point, DEFAULT_UNIT_IUS, instanceof
from kigadgets.layer import get_board_layer_name, get_board_layer_id


class _ABC(object):
    def __init__(self):
        raise NotImplementedError('{} has no __init__. It is an abstract and/or wrapper-only class'.format(type(self)))

    def __eq__(self, other):
        return True

    def __hash__(self):
        return 0

    def geohash(self):
        return hash(type(self).__name__)  # The leaf class, not "_ABC"


class BoardItem(_ABC):
    _obj = None
    _wraps_native_cls = None

    @property
    def native_obj(self):
        return self._obj

    @property
    def board(self):
        from kigadgets.board import Board
        brd_native = self._obj.GetBoard()
        if brd_native:
            return Board(brd_native)
        else:
            return None

    @classmethod
    def wrap(cls, instance):
        if cls._wraps_native_cls is not None:
            if not instanceof(instance, cls._wraps_native_cls):
                raise TypeError(
                    '{} cannot wrap native class {}'
                    '\n  Allowed: {}'.format(cls.__name__, type(instance).__name__, cls._wraps_native_cls)
                )
        return kigadgets.new(cls, instance)

    def __eq__(self, other):
        are_equal = True
        are_equal &= super().__eq__(other)
        return are_equal

    def __hash__(self):
        return super().__hash__()

    # def geohash(self):
    #     mine = 0  # Change this line to everything geometric when overloading
    #     return mine + super().geohash()


class HasPosition(_ABC):
    """Board items that has valid position property should inherit
    this."""

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

    def geohash(self):
        mine = hash(self.position)
        return mine + super().geohash()


class HasOrientation(_ABC):
    """Board items that has orientation property should inherit this."""
    @property
    def orientation(self):
        """Rotation of the item in degrees."""
        if SWIG_version >= 7:
            return float(self._obj.GetOrientationDegrees())
        else:
            return float(self._obj.GetOrientation()) / 10

    @orientation.setter
    def orientation(self, value):
        if SWIG_version >= 7:
            self._obj.SetOrientationDegrees(value)
        else:
            self._obj.SetOrientation(value * 10.)

    def geohash(self):
        mine = hash(self.orientation)
        return mine + super().geohash()


class HasLayer(_ABC):
    """ Layer handling based on strings like `'F.Cu'`, `'B.Silkscreen'`, `'User.12'`, etc.
        If the layer is not present, it will be caught at runtime, rather than disallowed.
    """
    @property
    def layer(self):
        layid = self._obj.GetLayer()
        try:
            brd = self.board
        except AttributeError:
            from kigadgets.board import Board
            native = self._obj.GetBoard()
            brd = Board(native) if native else None
        return get_board_layer_name(brd, layid)

    @layer.setter
    def layer(self, value):
        try:
            brd = self.board
        except AttributeError:
            from kigadgets.board import Board
            native = self._obj.GetBoard()
            brd = Board(native) if native else None
        layid = get_board_layer_id(brd, value)
        self._obj.SetLayer(layid)

    def geohash(self):
        mine = hash(self.layer)
        return mine + super().geohash()


class HasConnection(_ABC):
    """All BOARD_CONNECTED_ITEMs should inherit this."""
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

    def geohash(self):
        mine = hash(self.net_name)
        return mine + super().geohash()

class Selectable(_ABC):
    """ This influences the main window. Make sure to pcbnew.Refresh() to see it """
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


class HasWidth(_ABC):
    @property
    def width(self):
        return float(self._obj.GetWidth()) / DEFAULT_UNIT_IUS

    @width.setter
    def width(self, value):
        self._obj.SetWidth(int(value * DEFAULT_UNIT_IUS))

    def geohash(self):
        mine = hash(self.width)
        return mine + super().geohash()


class TextEsque(_ABC):
    ''' Base class for items with text-like properties

        Note:
            Text orientation and object rotation/orientation mean different things
    '''
    justification_lookups = dict(
        left='GR_TEXT_HJUSTIFY_LEFT',
        center='GR_TEXT_HJUSTIFY_CENTER',
        right='GR_TEXT_HJUSTIFY_RIGHT',
        bottom='GR_TEXT_VJUSTIFY_BOTTOM',
        middle='GR_TEXT_VJUSTIFY_CENTER',
        top='GR_TEXT_VJUSTIFY_TOP',
    )

    @property
    def text(self):
        return self._obj.GetText()

    @text.setter
    def text(self, value):
        return self._obj.SetText(value)

    @property
    def thickness(self):
        if SWIG_version >= 7:
            return float(self._obj.GetTextThickness()) / DEFAULT_UNIT_IUS
        else:
            return float(self._obj.GetThickness()) / DEFAULT_UNIT_IUS

    @thickness.setter
    def thickness(self, value):
        if SWIG_version >= 7:
            return self._obj.SetTextThickness(int(value * DEFAULT_UNIT_IUS))
        else:
            return self._obj.SetThickness(int(value * DEFAULT_UNIT_IUS))

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

    def geohash(self):
        mine = hash((
            self.text,
            self.thickness,
            self.size,
            self.orientation,
            self.justification,
        ))
        return mine + super().geohash()
