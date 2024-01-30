:py:mod:`kigadgets` Documentation
============================================

kigadgets is designed to let you interact design files or extend kicad to fit your purposes without the need to write C++ code.

.. image:: media/kiga-light-1024.png
  :width: 500
  :alt: kigadgets
  :align: center

From inside pcbnew you are able to recover the current Board object like this::

    from kigadgets.board import Board
    pcb = Board.from_editor()

From outside, you can load a board file like this::

    from kigadgets.board import Board
    pcb = Board.load('my_board.kicad_pcb')

Once you have a `Board`, all other operations behave exactly the same within the GUI or outside the GUI.::

    >>> print([track.layer for track in pcb.tracks])
    [F.Cu, B.Cu, B.Cu]
    >>> print([track.width for track in pcb.tracks if track.is_selected])
    [0.8, 0.6]


.. toctree::
   :maxdepth: 5

   getting_started/index
   ap_devs/index
   design/index
   API/index


