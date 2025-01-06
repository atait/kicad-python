import cmath

import kigadgets
from kigadgets import units, SWIGtype


class Point(units.BaseUnitTuple):

    def __init__(self, x, y):
        """Creates a point.

        :param x: x coordinate.
        :param y: y coordinate.
        """
        self._obj = SWIGtype.Point(
            int(x * units.DEFAULT_UNIT_IUS),
            int(y * units.DEFAULT_UNIT_IUS)
        )

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Point(%g, %g)" % (self.x, self.y)

    @staticmethod
    def build_from(t):
        """Return a point object from a tuple.

        It can transparently receive either a Point or a tuple,
        and a Point object will always be returned.
        """
        return Point._tuple_to_class(t, Point)

    @staticmethod
    def native_from(t):
        """Return a native C++/old API object from a tuple/Point.

        Generally not to be used, but provided for compatibility
        when migrating from old API code.
        """
        return Point._tuple_to_class(t, Point).native_obj

    @property
    def native_obj(self):
        """Returns the native wxPoint object Point is wrapping."""
        return self._obj

    def rotate(self, angle, around=(0, 0)):
        """Rotate the point.

        :param angle: rotation angle in degrees.
        :param around: rotation center.
        """
        self.x, self.y = self._rotated(angle, around)

    def rotated(self, angle, around=(0, 0)):
        """Generate a new Point.

        :param angle: rotation angle in degrees.
        :param around: rotation center.
        :returns: Point
        """
        x, y = self._rotated(angle, around)
        return Point(x, y)

    def _rotated(self, angle, around=(0, 0)):
        """Rotate coordinate around another point"""
        around = Point.build_from(around)
        p0 = self - around
        coord = (p0.x + p0.y * 1j) * cmath.exp((angle / units.rad) * 1j)
        return (coord.real + around.x, coord.imag + around.y)
