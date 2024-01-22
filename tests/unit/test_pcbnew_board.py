import unittest

from kigadgets.board import Board


class TestPcbnewBoard(unittest.TestCase):
    #TODO(mangelajo): currently we're just testing that the parameter
    #                 combinations work, we may need to check that the
    #                 actual objects were created and added to the Board
    def setUp(self):
        self.board = Board()

    def test_module_creation(self):
        self.board.add_footprint('M1')
        self.assertEqual(1, len(list(self.board.footprints)))
        self.board.add_footprint('M2')
        self.assertEqual(2, len(list(self.board.footprints)))
        refs = [module.reference for module in self.board.footprints]
        self.assertIn('M1', refs)
        self.assertIn('M2', refs)

    def test_track_segment_creation(self):
        self.board.add_track_segment((0, 0), (1, 1))
        self.board.add_track_segment((0, 0), (1, 1), layer='B.Cu')
        self.board.add_track_segment((0, 0), (1, 1), layer='B.Cu', width=2)

    def test_track_creation(self):
        self.board.add_track([(0, 0), (1, 1)])
        self.board.add_track([(1, 1), (1, 2)], 'B.Cu')
        self.board.add_track([(1, 2), (2, 2)], 'B.Cu', width=2)

    def test_via_creation(self):
        self.board.add_via((1, 1))
        self.board.add_via((1, 2), layer_pair=('B.Cu', 'F.Cu'), size=2)
        self.board.add_via((1, 3), layer_pair=('B.Cu', 'F.Cu'), size=2, drill=1)

    def test_default_via_props(self):
        self.assertGreater(self.board.default_via_size, 0.1)
        self.assertGreater(self.board.default_via_drill, 0.1)

    def test_line_creation(self):
        self.board.add_line((0, 0), (1, 1))
        self.board.add_line((0, 0), (1, 1), layer='B.SilkS')
        self.board.add_line((0, 0), (1, 1), layer='B.SilkS', width=1)

    def test_polyline_creation(self):
        self.board.add_polyline([(0, 0), (1, 1), (2, 2)])

    def test_add_circle(self):
        self.board.add_circle((1, 1), 1)

    def test_add_arc(self):
        self.board.add_arc((0, 0), 5, 0, 90)
