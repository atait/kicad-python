import unittest

from kigadgets.board import Board


REFERENCE = 'M1'
OTHER_REFERENCE = 'M2'
POSITION = (1, 2)
OTHER_POSITION = (3, 4)


class TestPcbnewFootprint(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.footprint = self.board.add_footprint(REFERENCE, pos=POSITION)

    def test_footprint_reference(self):
        self.assertEqual(REFERENCE, self.footprint.reference)
        self.footprint.reference = OTHER_REFERENCE
        self.assertEqual(OTHER_REFERENCE, self.footprint.reference)

    def test_footprint_position(self):
        self.assertEqual(POSITION, self.footprint.position)
        self.footprint.position = OTHER_POSITION
        self.assertEqual(OTHER_POSITION, self.footprint.position)

    def test_footprint_copy(self):
        footprint_copy = self.footprint.copy(OTHER_REFERENCE)
        self.assertEqual(OTHER_REFERENCE, footprint_copy.reference)
        self.assertEqual(POSITION, footprint_copy.position)

    def test_footprint_copy_in_board_and_position(self):
        footprint_copy = self.footprint.copy(
            OTHER_REFERENCE, pos=OTHER_POSITION, board=self.board)
        self.assertEqual(OTHER_POSITION, footprint_copy.position)
