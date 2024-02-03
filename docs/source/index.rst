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

    editor_board = Board.from_editor()


From outside, you can load a board file and iterate over modules this way::

    from kigadgets.board import Board

    my_board = Board.load('my_board.kicad_pcb')

    for fp in my_board.footprints:
        data = {'reference': fp.reference,
                'position': fp.position}
        print "module %(reference)s is at %(position)s" % data

API
-----

.. toctree::
   :maxdepth: 1

   API top <API/index>
   Placeholder <otherpage>
