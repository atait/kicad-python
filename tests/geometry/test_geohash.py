import unittest
from kigadgets.board import Board
from kigadgets.via import Via


class TestGeohash(unittest.TestCase):
    def setUp(self):
        self.pcb = Board()
        self.pcb.add_track([(1, 1), (1, 2)], 'B.Cu')
        self.pcb.add_via((10, 10))
        self.pcb.add_line((0, 0), (1, 1), layer='B.Silkscreen')
        self.pcb.add_circle((1, 1), 1)
        self.pcb.add_arc((0, 0), 5, 0, 90)

    def test_identity(self):
        assert self.pcb.geohash() == self.pcb.geohash()

    def test_copy(self):
        new_pcb = self.pcb.copy()
        assert self.pcb.geohash() == new_pcb.geohash()

    def test_saveload(self):
        self.pcb.save('tmp.kicad_pcb')
        new_pcb = Board.load('tmp.kicad_pcb')
        os.remove('tmp.kicad_pcb')
        assert self.pcb.geohash() == new_pcb.geohash()

    def test_difference(self):
        new_pcb = self.pcb.copy()
        new_pcb.remove(next(new_pcb.tracks))
        assert self.pcb.geohash() != new_pcb.geohash()

