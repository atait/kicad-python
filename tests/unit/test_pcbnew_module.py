import unittest

from kicad import *
from kicad.pcbnew.board import *


REFERENCE = 'M1'
OTHER_REFERENCE = 'M2'
POSITION = (1, 2)
OTHER_POSITION = (3, 4)


class TestPcbnewModule(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.module = self.board.add_module(REFERENCE, pos=POSITION)

    def test_module_reference(self):
        self.assertEqual(REFERENCE, self.module.reference)
        self.module.reference = OTHER_REFERENCE
        self.assertEqual(OTHER_REFERENCE, self.module.reference)

    def test_module_position(self):
        self.assertEqual(POSITION, self.module.position)
        self.module.position = OTHER_POSITION
        self.assertEqual(OTHER_POSITION, self.module.position)

    def test_module_copy(self):
        module_copy = self.module.copy(OTHER_REFERENCE)
        self.assertEqual(OTHER_REFERENCE, module_copy.reference)
        self.assertEqual(POSITION, module_copy.position)

    def test_module_copy_in_board_and_position(self):
        module_copy = self.module.copy(
            OTHER_REFERENCE, pos=OTHER_POSITION, board=self.board)
        self.assertEqual(OTHER_POSITION, module_copy.position)
