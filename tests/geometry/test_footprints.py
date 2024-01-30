from lytest import contained_pcbnewBoard, difftest_it
from kigadgets.drawing import TextPCB

@contained_pcbnewBoard
def simple_footprint(pcb):
    for fp in pcb.footprints:
        pass
    # fp = next(pcb.footprints)
    assert fp.reference == 'U1'
    assert fp.value == 'LM555xM'
    assert len(list(fp.pads)) == 8

    for dw in pcb.drawings:
        if isinstance(dw, TextPCB):
            assert dw.text == 'Microvias'
            break
    else:
        raise RuntimeError('Text not found')

    # for pad in fp.pads:

    fp.flip()
    fp.x -= 10
    fp.orientation += 90
    fp.y += 20

def test_simple_footprint(): difftest_it(simple_footprint)()

