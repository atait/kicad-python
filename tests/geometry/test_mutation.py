'''
    `difftest_it` will look for the container's name in src_layouts,
    to find src_layouts/simple_mutate.kicad_pcb, load it, and pass it as `pcb`
'''
from lytest import contained_pcbnewBoard, difftest_it


@contained_pcbnewBoard
def simple_mutate(pcb):
    pcb.add_track([(-1, -1), (-1, -2)], 'F.Cu')

def test_simple_mutate(): difftest_it(simple_mutate)()
