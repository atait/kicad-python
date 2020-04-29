# -*- coding: utf-8 -*-
#
# An example script to check for annular ring violations
#

from kicad.pcbnew.board import Board

def annring_size(pad):
    return min(pad.size) - max(pad.drill)

MIN_AR_SIZE = .25

board = Board.from_editor()

for m in board.modules:
    for pad in m.pads:
        if annring_size(pad) < MIN_AR_SIZE:
            print("AR violation at %s." % pad.position)
