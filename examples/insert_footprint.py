# -*- coding: utf-8 -*-
#
# An example script to insert a footprint
#

from kicad.pcbnew.board import Board
from kicad.pcbnew.module import Module
board = Board.from_editor()

# full path to library folder
lib_path = "/usr/share/kicad/footprints/Diode_SMD.pretty"
# name of footprint in the library
mod_name = "D_SOD-323F"

m = Module.load_from_library(lib_path, mod_name)
m.position = (10, 10)
board.add(m)

import pcbnew
pcbnew.Refresh()

