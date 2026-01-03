from typing import Union, Tuple, Any

import kigadgets
from kigadgets import units, SWIGtype
from kigadgets.units import CoordinateLike


class Size(units.BaseUnitTuple):

    def __init__(self, width: float, height: float) -> None:
        self._obj = SWIGtype.Size(
            int(width * units.DEFAULT_UNIT_IUS),
            int(height * units.DEFAULT_UNIT_IUS)
        )

    @property
    def native_obj(self) -> Any:
        return self._obj

    @staticmethod
    def build_from(t: CoordinateLike) -> 'Size':
        return Size._tuple_to_class(t, Size)

    @staticmethod
    def native_from(t: CoordinateLike) -> Any:
        return Size._tuple_to_class(t, Size).native_obj

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "Size(%g, %g)" % self.mm

    def scale(self, x: float, y: float) -> None:
        """Scale this size by x horizontally, and y vertically."""
        scaled = self.scaled(x, y)
        self.x = scaled.x
        self.y = scaled.y

    def scaled(self, x: float, y: float) -> 'Size':
        """Return a new scaled point, scaling by x and y."""
        scaled = self.Scale(x, y)
        return Size(scaled.x, scaled.y)

    @property
    def width(self) -> float:
        """Return the width of the size."""
        return self.x

    @width.setter
    def width(self, value: float) -> None:
        """Set the width of the size."""
        self.x = value

    @property
    def height(self) -> float:
        """Return the height of the size."""
        return self.y

    @height.setter
    def height(self, value: float) -> None:
        """Set the height of the size."""
        self.y = value
