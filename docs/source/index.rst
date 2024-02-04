:py:mod:`kigadgets` Documentation
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


.. toctree::
   :maxdepth: 5

   getting_started/index
   ap_devs/index
   design/index
   API/index


