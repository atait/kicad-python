import unittest

from kigadgets import Point, units


class TestKicadUnits(unittest.TestCase):

    def test_converters(self):
        self.assertEqual(units.inch_to_mm(1), 25.4)
        self.assertEqual(units.mm_to_inch(25.4), 1.0)

    def test_converters_seq(self):
        self.assertEqual(units.inch_to_mm([1, 2]), [25.4, 50.8])
        self.assertEqual(units.mm_to_inch([25.4, 50.8]), [1.0, 2.0])

    def test_base_unit_tuple_mm(self):
        bunit = Point(1, 2)
        self.assertEqual(bunit.mm, (1.0, 2.0))

    def test_base_unit_tuple_inch(self):
        bunit = Point(1 * units.inch, 2 * units.inch)
        self.assertEqual(bunit.inch, (1.0, 2.0))

    def test_base_unit_tuple_mil(self):
        bunit = Point(1 * units.mil, 2 * units.mil)
        self.assertEqual(bunit.mil, (1.0, 2.0))

    def test_base_unit_tuple_nm(self):
        bunit = Point(1 * units.nm, 2 * units.nm)
        self.assertEqual(bunit.nm, (1, 2))
