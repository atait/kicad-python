import unittest

from kigadgets import Point


class TestKicadPoint(unittest.TestCase):

    def test_rotation(self):
        p = Point(1, 1)
        x, y = p.rotated(180).mm
        self.assertAlmostEqual(x, -1.0, places=5)
        self.assertAlmostEqual(y, -1.0, places=5)

    def test_rotation_around(self):
        p = Point(1, 1)
        p_rotated = p.rotated(180, around=(1, 1))
        self.assertEqual(p_rotated.mm, (1.0, 1.0))

    def test_equal(self):
        p1 = Point(2, 2)
        p2 = Point(2, 2)
        self.assertTrue(p1 == p2)
        self.assertTrue(p1 == (2, 2))
