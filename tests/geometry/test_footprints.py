''' Another mutation example

    `difftest_it` will look for the container's name in src_layouts,
    to find src_layouts/simple_footprint.kicad_pcb, load it, and pass it as `pcb`

    As ususal, afterwards, a new output is generated in run_layouts and compared
    against the correspoinding one stored in ref_layouts
'''
from lytest import contained_pcbnewBoard, difftest_it
from kigadgets.drawing import TextPCB

@contained_pcbnewBoard
def simple_footprint(pcb):
    fp = pcb.footprints[0]
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

