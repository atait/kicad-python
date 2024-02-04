.. KiCad Python API documentation master file, created by
   sphinx-quickstart on Fri Jan 23 20:40:38 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

kigadgets documentation
============================================

kigadgets is designed to let you interact design files or extend
kicad to fit your purposes without the need to write C++ code.

From inside pcbnew you are able to recover the current Board object like this::

    from kigadgets.board import Board
    pcb = Board.from_editor()

From outside, you can load a board file like this::

    from kigadgets.board import Board
    pcb = Board.load('my_board.kicad_pcb')

Once you have a `Board`, all other operations behave exactly the same within the GUI or outside the GUI.::

    print([track.layer for track in pcb.tracks])
    print([track.width for track in pcb.tracks if track.is_selected])


API
-----

.. toctree::
   :maxdepth: 1

   API top <API/index>
   Placeholder page <otherpage>
