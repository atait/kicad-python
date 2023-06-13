"""Base classes and mixins for KiCad PCB objects using wrapper pattern.

This module implements property-like access to KiCad's native SWIG object methods.
Mixin classes (position, connections, etc.) provide reusable, modular, composable functionality

Key Components:
- GeoHashable: Base class for geometric comparison and testing
- BoardItem: Wrapper foundation for all PCB objects
- Mixins: HasPosition, HasConnection, HasLayer, Selectable, TextEsque
"""

import kigadgets
from kigadgets import SWIG_version, Point, Size, DEFAULT_UNIT_IUS, instanceof
from kigadgets.layer import get_board_layer_name, get_board_layer_id
import pcbnew
from typing import Optional, Any, Tuple, Union


class GeoHashable(object):
    """Base class for objects that can be geometrically hashed.

    A geohash is a hash of the geometric properties of an object.
    It is used to compare two objects for geometric equality,
    independent of non-geometric properties like iteration order of traces.
    Any tiny design change will result in a substantially different geohash.

    Equivalence testing is essential for regression testing, versioning, and ensuring design integrity.
    KiCAD PCB formats do not guarantee binary equivalence of identical designs, even within a major version.
    Geohashing guarantees design equivalence, within and across KiCAD versions, enabling reliable change detection.
    """
    def __init__(self) -> None:
        raise NotImplementedError(
            f"{type(self)} has no __init__. "
            "It is an abstract and/or wrapper-only class"
        )

    def geohash(self) -> int:
        return hash(type(self).__name__)  # The leaf class, not "_ABC"


class BoardItem(GeoHashable):
    """Base class for all PCB board items."""
    _obj = None
    _wraps_native_cls = None

    @property
    def native_obj(self) -> Any:
        return self._obj

    @property
    def board(self) -> Optional['Board']:
        from kigadgets.board import Board
        brd_native = self._obj.GetBoard()
        if brd_native:
            return Board(brd_native)
        else:
            return None

    @classmethod
    def wrap(cls, instance: Any) -> 'BoardItem':
        if cls._wraps_native_cls and not instanceof(instance, cls._wraps_native_cls):
            raise TypeError(
                f"{cls.__name__} cannot wrap native class {type(instance).__name__}.\n"
                f"Allowed: {cls._wraps_native_cls}"
            )
        return kigadgets.new(cls, instance)


class HasPosition(GeoHashable):
    """Mixin for board items with position properties."""

    @property
    def position(self) -> Point:
        return Point.wrap(self._obj.GetPosition())

    @position.setter
    def position(self, value: Union[Point, Tuple[float, float]]) -> None:
        self._obj.SetPosition(Point.native_from(value))

    @property
    def x(self) -> float:
        return self.position.x

    @x.setter
    def x(self, value: float) -> None:
        self.position = (value, self.y)

    @property
    def y(self) -> float:
        return self.position.y

    @y.setter
    def y(self, value: float) -> None:
        self.position = (self.x, value)

    def geohash(self) -> int:
        mine = hash(self.position)
        return mine + super().geohash()


class HasOrientation(GeoHashable):
    """Mixin for board items with orientation properties."""
    @property
    def orientation(self) -> float:
        """Rotation of the item in degrees."""
        if SWIG_version >= 7:
            return float(self._obj.GetOrientationDegrees())
        else:
            return float(self._obj.GetOrientation()) / 10

    @orientation.setter
    def orientation(self, value: float) -> None:
        if SWIG_version >= 7:
            self._obj.SetOrientationDegrees(value)
        else:
            self._obj.SetOrientation(value * 10.0)

    def geohash(self) -> int:
        mine = hash(self.orientation)
        return mine + super().geohash()


class HasLayer(GeoHashable):
    """Mixin for layer handling based on *strings* (like `'F.Cu'`, `'B.Silkscreen'`, `'User.12'`, etc.).
    If the layer is not present, it will be caught at runtime, rather than disallowed.
    """
    @property
    def layer(self) -> str:
        layid = self._obj.GetLayer()
        try:
            brd = self.board
        except AttributeError:
            from kigadgets.board import Board
            native = self._obj.GetBoard()
            brd = Board(native) if native else None
        return get_board_layer_name(brd, layid)

    @layer.setter
    def layer(self, value: str) -> None:
        try:
            brd = self.board
        except AttributeError:
            from kigadgets.board import Board
            native = self._obj.GetBoard()
            brd = Board(native) if native else None
        layid = get_board_layer_id(brd, value)
        self._obj.SetLayer(layid)

    def geohash(self) -> int:
        mine = hash(self.layer)
        return mine + super().geohash()


class HasConnection(GeoHashable):
    """Mixin for board items with electrical connections.
    All BoardItems that wrap BOARD_CONNECTED_ITEMs should inherit this.
    """
    @property
    def net_name(self) -> str:
        return self._obj.GetNetname()

    @net_name.setter
    def net_name(self, value: str) -> None:
        """Takes a name and attempts to look it up based on the containing board"""
        if not self._obj:
            raise TypeError("Cannot set net_name without a containing Board.")
        try:
            new_code = self._obj.GetBoard().GetNetcodeFromNetname(value)
        except IndexError:
            raise KeyError("Net name '{}' not found in board nets.".format(value))
        self._obj.SetNetCode(new_code)

    @property
    def net_code(self) -> int:
        return self._obj.GetNetCode()

    @net_code.setter
    def net_code(self, value: int) -> None:
        self._obj.SetNetCode(value)

    def geohash(self) -> int:
        mine = hash(self.net_name)
        return mine + super().geohash()


class Selectable(GeoHashable):
    """Mixin for board items that can be selected in the GUI.
    Selection influences the main window. Make sure to pcbnew.Refresh() to see the effects
    """
    @property
    def is_selected(self) -> bool:
        return bool(self._obj.IsSelected())

    def select(self, value: bool = True) -> None:
        """Selecting changes the appearance and also plays a role in determining
        what will be the subject of a subsequent command (delete, move to layer, etc.)
        """
        if value:
            self._obj.SetSelected()
        else:
            self._obj.ClearSelected()

    def deselect(self) -> None:
        self.select(False)

    def brighten(self, value: bool = True) -> None:
        """Brightening gives a bright green appearance"""
        if value:
            self._obj.SetBrightened()
        else:
            self._obj.ClearBrightened()


class HasWidth(GeoHashable):
    """Mixin for board items with width properties."""
    @property
    def width(self) -> float:
        return float(self._obj.GetWidth()) / DEFAULT_UNIT_IUS

    @width.setter
    def width(self, value: float) -> None:
        self._obj.SetWidth(int(value * DEFAULT_UNIT_IUS))

    def geohash(self) -> int:
        mine = hash(self.width)
        return mine + super().geohash()


if SWIG_version < 7:
    just_lookups_vcurrent = dict(
        left="GR_TEXT_HJUSTIFY_LEFT",
        center="GR_TEXT_HJUSTIFY_CENTER",
        right="GR_TEXT_HJUSTIFY_RIGHT",
        bottom="GR_TEXT_VJUSTIFY_BOTTOM",
        middle="GR_TEXT_VJUSTIFY_CENTER",
        top="GR_TEXT_VJUSTIFY_TOP",
    )
else:
    just_lookups_vcurrent = dict(
        left="GR_TEXT_H_ALIGN_LEFT",
        center="GR_TEXT_H_ALIGN_CENTER",
        right="GR_TEXT_H_ALIGN_RIGHT",
        bottom="GR_TEXT_V_ALIGN_BOTTOM",
        middle="GR_TEXT_V_ALIGN_CENTER",
        top="GR_TEXT_V_ALIGN_TOP",
    )


class TextEsque(GeoHashable):
    """Base class for items with text-like properties

    Note:
        Text orientation and object rotation/orientation mean different things
    """

    justification_lookups = just_lookups_vcurrent

    @property
    def text(self) -> str:
        return self._obj.GetText()

    @text.setter
    def text(self, value: str) -> None:
        return self._obj.SetText(value)

    @property
    def thickness(self) -> float:
        if SWIG_version >= 6:
            return float(self._obj.GetTextThickness()) / DEFAULT_UNIT_IUS
        else:
            return float(self._obj.GetThickness()) / DEFAULT_UNIT_IUS

    @thickness.setter
    def thickness(self, value: float) -> None:
        assert value > 0, "Thickness must be positive"
        if SWIG_version >= 6:
            return self._obj.SetTextThickness(int(value * DEFAULT_UNIT_IUS))
        else:
            return self._obj.SetThickness(int(value * DEFAULT_UNIT_IUS))

    @property
    def mirrored(self) -> bool:
        return self._obj.IsMirrored()

    @mirrored.setter
    def mirrored(self, value: bool) -> None:
        self._obj.SetMirrored(value)

    @property
    def size(self) -> Size:
        return Size.wrap(self._obj.GetTextSize())

    @size.setter
    def size(self, value: Union[Size, Tuple[float, float], float]) -> None:
        try:
            size = Size.build_from(value)
        except TypeError:
            size = Size.build_from((value, value))
        self._obj.SetTextSize(size.native_obj)

    @property
    def orientation(self) -> float:
        """Rotation of the item in degrees."""
        if SWIG_version >= 8:
            return float(self._obj.GetTextAngleDegrees())
        else:
            return float(self._obj.GetTextAngle()) / 10

    @orientation.setter
    def orientation(self, value: float) -> None:
        if SWIG_version >= 8:
            self._obj.SetTextAngleDegrees(value)
        else:
            self._obj.SetTextAngle(value * 10.0)

    @property
    def justification(self) -> Tuple[str, str]:
        hj = self._obj.GetHorizJustify()
        vj = self._obj.GetVertJustify()
        for k, v in TextEsque.justification_lookups.items():
            if hj == getattr(pcbnew, v):
                hjs = k
            if vj == getattr(pcbnew, v):
                vjs = k
        return hjs, vjs

    @justification.setter
    def justification(self, value: Union[str, Tuple[str, str]]) -> None:
        if isinstance(value, (list, tuple)):
            assert len(value) == 2
            self.justification = value[0]
            self.justification = value[1]
        else:
            try:
                token = TextEsque.justification_lookups[value]
            except KeyError:
                valids = list(TextEsque.justification_lookups.keys())
                raise ValueError(f"Invalid justification {value} of available {valids}")
            enum_val = getattr(pcbnew, token)
            is_horizontal = "_H" in token
            if is_horizontal:
                self._obj.SetHorizJustify(enum_val)
            else:
                self._obj.SetVertJustify(enum_val)

    def geohash(self) -> int:
        mine = hash((
            self.text,
            self.thickness,
            self.size,
            self.orientation,
            self.justification,
        ))
        return mine + super().geohash()
