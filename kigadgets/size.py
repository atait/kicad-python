import kigadgets
from kigadgets import units, SWIGtype


class Size(units.BaseUnitTuple):

    def __init__(self, width, height):
        self._obj = SWIGtype.Size(
            int(width * units.DEFAULT_UNIT_IUS),
            int(height * units.DEFAULT_UNIT_IUS)
        )

    @property
    def native_obj(self):
        return self._obj

    @staticmethod
    def build_from(t):
        return Size._tuple_to_class(t, Size)

    @staticmethod
    def native_from(t):
        return Size._tuple_to_class(t, Size).native_obj

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Size(%g, %g)" % self.mm

    def scale(self, x, y):
        """Scale this size by x horizontally, and y vertically."""
        scaled = self.scaled(x, y)
        self.x = scaled.x
        self.y = scaled.y

    def scaled(self, x, y):
        """Return a new scaled point, scaling by x and y."""
        scaled = self.Scale(x, y)
        return Size(scaled.x, scaled.y)

    @property
    def width(self):
        """Return the width of the size."""
        return self.x

    @width.setter
    def width(self, value):
        """Set the width of the size."""
        self.x = value

    @property
    def height(self):
        """Return the height of the size."""
        return self.y

    @height.setter
    def height(self, value):
        """Set the height of the size."""
        self.y = value
