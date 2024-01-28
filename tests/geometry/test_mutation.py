from lytest import contained_pcbnewBoard, difftest_it

@contained_pcbnewBoard
def simple_mutate(pcb):
    pcb.add_track([(-1, -1), (-1, -2)], 'F.Cu')

def test_simple_mutate(): difftest_it(simple_mutate)()
