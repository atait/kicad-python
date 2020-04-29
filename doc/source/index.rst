.. KiCad Python API documentation master file, created by
   sphinx-quickstart on Fri Jan 23 20:40:38 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to KiCad Python API's documentation!
============================================

KiCad Python API is designed to let you interact design files or extend
kicad to fit your purposes without the need to write C++ code.

From inside pcbnew you are able to recover the current Board object like this::

    from kicad.pcbnew import Board

    editor_board = Board.from_editor()


From outside, you can load a board file and iterate over modules this way::

    from kicad.pcbnew import Board

    my_board = Board.load('my_board.kicad_pcb')

    for module in my_board.modules:
        data = {'reference': module.reference,
                'position': module.position}
        print "module %(reference)s is at %(position)s" % data

kicad
-----

.. toctree::
   :maxdepth: 3

   kicad/point
   kicad/size
   kicad/pcbnew/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

