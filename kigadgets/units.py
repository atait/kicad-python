import math
import kigadgets

nm = 0.000001
mm = 1.0
inch = 25.4
mil = 0.25400

nm_ius = 1
mm_ius = 1000000
inch_ius = 254000000
mil_ius = 25400

deg = 1.0
rad = 180.0 / math.pi

DEFAULT_UNIT_IUS = mm_ius


def inch_to_mm(val):
    """Convert from inch to mm.

    Handles single values, sequences, sequences of sequences, etc.
    """
    try:
        return val * 25.4
    except TypeError:
        return [inch_to_mm(v) for v in val]


def mm_to_inch(val):
    """Convert from mm to inch.

    Handles single values, sequences, sequences of sequences, etc.
    """
    try:
        return val / 25.4
    except TypeError:
        return [mm_to_inch(v) for v in val]


class BaseUnitTuple(object):
    """Base class to provide mm, inch, mil properties.

    It's a class to be used just by Point and Size.
    """
    @classmethod
    def wrap(cls, instance):
        """Wraps a point or size native object"""
        return kigadgets.new(cls, instance)

    @property
    def x(self):
        """x coordinate."""
        return float(self.native_obj.x) / DEFAULT_UNIT_IUS

    @x.setter
    def x(self, value):
        self.native_obj.x = int(value * DEFAULT_UNIT_IUS)

    @property
    def y(self):
        """y coordinate."""
        return float(self.native_obj.y) / DEFAULT_UNIT_IUS

    @y.setter
    def y(self, value):
        self.native_obj.y = int(value * DEFAULT_UNIT_IUS)

    def __getitem__(self, index):
        return self.mm[index]

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError

    def __sub__(self, b):
        return type(self).build_from((self[0] - b[0], self[1] - b[1]))

    def __add__(self, b):
        return type(self).build_from((self[0] + b[0], self[1] + b[1]))

    def __eq__(self, _other):
        other = type(self).build_from(_other)
        return self.native_obj == other.native_obj

    def __hash__(self):
        return hash((self.x, self.y))

    def __ne__(self, other):
        return not (self == other)

    def __len__(self):
        return len(self.native_obj)

    def _unit_tuple(self, unit_multiplier):
        unit_multiplier_float = float(unit_multiplier)
        return (self.x / unit_multiplier_float, self.y / unit_multiplier_float)

    @property
    def nm(self):
        """Get the nanometers tuple."""
        return self._unit_tuple(nm)

    @property
    def mm(self):
        """Get the milimeters tuple.

        :Example:

        >>> import kigadgets
        >>> p = kigadgets.Point(1, 2)
        >>> p.mm
        (1, 2)

        """
        return (self.x, self.y)

    @property
    def inch(self):
        """Get the inches tuple."""
        return self._unit_tuple(inch)

    @property
    def mil(self):
        """Get the mils tuple."""
        return self._unit_tuple(mil)

    @staticmethod
    def _tuple_to_class(v, cls):
        if isinstance(v, cls):
            return v
        elif isinstance(v, (tuple, list)):
            if len(v) != 2:
                raise TypeError("A point parameter must be a 2 value tuple")
        return cls(v[0], v[1])
