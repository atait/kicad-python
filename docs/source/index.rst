:py:mod:`kigadgets` Documentation
============================================

kigadgets makes KiCad and Python work better together.

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

This package has been fully tested with KiCad 5.0-9.0 (Mac/Windows/Linux). See ./tests to reproduce headless behavior and ./examples to reproduce GUI behavior. Note that v9 will give warnings about SWIG.

.. toctree::
   :maxdepth: 5

   getting_started/index
   ap_devs/index
   design/index
   API/index


