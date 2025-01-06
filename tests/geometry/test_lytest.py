import os
from lytest import contained_pcbnewBoard, difftest_it
from lytest.kdb_xor import run_xor_pcbnew
from lytest.utest_buds import get_ref_dir

def test_lytest_xor_works():
    ''' If this fails, the testing framework itself is broken. '''
    file1 = 'simple_footprint.kicad_pcb'
    file1 = os.path.join(get_ref_dir(), file1)
    run_xor_pcbnew(file1, file1, tolerance=.001, verbose=False, hash_geom=True)

@contained_pcbnewBoard
def simple_track(pcb):
    pcb.add_track([(1, 1), (1, 2)], 'B.Cu')

def test_simple_track(): difftest_it(simple_track)()


@contained_pcbnewBoard
def largeboard(pcb):
    pcb.add_track_segment((0, 0), (1, 1))
    pcb.add_track_segment((5, 0), (6, 1), layer='B.Cu')
    pcb.add_track_segment((10, 0), (11, 1), layer='B.Cu', width=2)

    pcb.add_track([(0, 5), (1, 6), (3, 6), (20, 0)], 'B.Cu', width=2)

    pcb.add_via((-10, -10))
    pcb.add_via((-10, -15), layer_pair=('B.Cu', 'F.Cu'), size=1)
    pcb.add_via((-10, -20), layer_pair=('In1.Cu', 'F.Cu'), size=1, drill=.5)
    pcb.add_via((-10, -20), layer_pair=('In2.Cu', 'In1.Cu'), size=1)

    pcb.add_line((0, 0), (1, 1), layer='B.SilkS', width=1)
    pcb.add_circle((1, 1), 1)
    pcb.add_arc((0, 0), 5, 0, 90)

def test_largeboard(): difftest_it(largeboard)()
