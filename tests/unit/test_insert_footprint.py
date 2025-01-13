#
# An example script to insert a footprint
#
import os
from kigadgets.board import Board
from kigadgets.module import Module

def test_insert_footprint():
    pcb = Board()
    # full path to library folder
    lib_path = os.path.join(os.path.dirname(__file__), "test_lib.pretty")
    # lib_path = "/usr/share/kicad/footprints/Diode_SMD.pretty"
    # name of footprint in the library
    mod_name = "D_SOD-323F"

    m = Module.load_from_library(lib_path, mod_name)
    m.position = (10, 10)
    pcb.add(m)

    assert len(pcb.footprints) == 1, "Footprint not added to the board"

