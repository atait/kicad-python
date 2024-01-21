import unittest

from kigadgets import Size


class TestKicadSize(unittest.TestCase):

    def test_size_properties(self):
        size = Size(1, 2)
        self.assertEqual(1, size.width)
        self.assertEqual(2, size.height)

    def test_addition(self):
        s1 = Size(1, 2)
        s2 = Size(2, 3)
        self.assertEqual((3, 5), s1 + s2)

    def test_substraction(self):
        s1 = Size(3, 4)
        s2 = Size(1, 1)
        self.assertEqual((2, 3), s1 - s2)
