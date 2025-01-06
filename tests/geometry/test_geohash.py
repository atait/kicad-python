import os
import unittest
from kigadgets.board import Board
from kigadgets.via import Via
import tempfile
import pytest
from . import iprepeat


def test_repeatable_str():
    if not iprepeat:
        pytest.skip('Cannot compare hashes to literal integer unless PYTHONHASHSEED=0')
    from kigadgets.via import Via
    via = Via((20, 20))
    assert via.geohash() == 1551763526998012866


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
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_pcbfile = os.path.join(temp_dir, 'kigadgets_copying.kicad_pcb')
            self.pcb.save(temp_pcbfile)
            new_pcb = Board.load(temp_pcbfile)
        assert self.pcb.geohash() == new_pcb.geohash()

    @pytest.mark.skip(reason='Unknown. Need to investigate')
    def test_surface_copy(self):
        new_pcb = Board()
        for item in self.pcb.items:
            new_pcb.add(item)
        assert new_pcb.geohash() == self.pcb.geohash()

    def test_nitems_difference(self):
        new_pcb = self.pcb.copy()
        new_pcb.remove(new_pcb.tracks[0])
        assert self.pcb.geohash() != new_pcb.geohash()

    def test_value_difference(self):
        new_pcb = self.pcb.copy()
        tt = new_pcb.tracks[0]
        tt.start = tt.start + (0.001, 0)
        assert self.pcb.geohash() != new_pcb.geohash()

    @pytest.mark.skip(reason='Unknown. Need to investigate')
    def test_deletion(self):
        blank_pcb = Board()
        new_pcb = self.pcb.copy()
        for item in new_pcb.items:
            new_pcb.remove(item)
        assert new_pcb.geohash() == blank_pcb.geohash()
        new_pcb.restore_removed()
        assert new_pcb.geohash() == self.pcb.geohash()

def test_track_startend():
    pcb1 = Board()
    pcb1.add_track([(1, 1), (1, 2)])
    pcb2 = Board()
    pcb2.add_track([(1, 2), (1, 1)])
    assert pcb1.geohash() == pcb2.geohash()


def test_microvia():
    via_thru = Via((1, 1), layer_pair=('F.Cu', 'B.Cu'))
    via_tinv = Via((1, 1), layer_pair=('B.Cu', 'F.Cu'))
    assert via_thru.geohash() == via_tinv.geohash()

    via_uvia = Via((1, 1), layer_pair=('In2.Cu', 'B.Cu'))
    via_uinv = Via((1, 1), layer_pair=('B.Cu', 'In2.Cu'))
    assert via_uvia.geohash() == via_uinv.geohash()


def test_via_mutation():
    via_uvia = Via((1, 1), layer_pair=('In2.Cu', 'B.Cu'))
    via_thru = Via((1, 1))
    via_thru.top_layer = 'In2.Cu'
    # via_thru.is_through = False  # This should be extraneous
    assert via_thru.geohash() == via_uvia.geohash()


def test_uvia_mutation():
    via_thru = Via((1, 1))
    via_uvia = Via((1, 1), layer_pair=('In2.Cu', 'B.Cu'))
    via_uvia.top_layer = 'F.Cu'
    via_uvia.is_through = True  # This is necessary
    assert via_thru.geohash() == via_uvia.geohash()

    via_uvia = Via((1, 1), layer_pair=('In2.Cu', 'B.Cu'))
    via_uvia.set_layer_pair(('B.Cu', 'F.Cu'))
    via_uvia.is_through = True
    assert via_thru.geohash() == via_uvia.geohash()
