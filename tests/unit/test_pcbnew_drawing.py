import unittest

from kigadgets import *
from kigadgets.drawing import Drawing, Segment, Circle, Arc


class TestPcbnewDrawing(unittest.TestCase):
    def test_segment_from_native(self):
        native_segment = Segment((0, 0), (1, 1))._obj
        new_segment = Drawing.wrap(native_segment)
        self.assertEqual(Segment, type(new_segment))

    def test_circle_from_native(self):
        native_circle = Circle((0, 0), 10.0)._obj
        new_circle = Drawing.wrap(native_circle)
        self.assertEqual(Circle, type(new_circle))

    def test_arc_from_native(self):
        native_arc = Arc((0, 0), 10.0, -90, 90)._obj
        new_arc = Drawing.wrap(native_arc)
        self.assertEqual(Arc, type(new_arc))
        self.assertEqual(new_arc.angle, 180)
        new_arc.angle = 40  # This will be rounded within 1e-3
        self.assertTrue(abs(new_arc.angle - 40) < 0.001)
