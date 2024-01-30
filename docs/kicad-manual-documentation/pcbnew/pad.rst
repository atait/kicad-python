pad
===

.. automodule:: kicad.pcbnew.pad

.. autoclass:: Pad
   :members:
   :undoc-members:

Pad enumerations
----------------
.. code-block:: python

    class DrillShape(IntEnum):
        Circle = pcbnew.PAD_DRILL_SHAPE_CIRCLE
        Oval = pcbnew.PAD_DRILL_SHAPE_OBLONG

    class PadShape(IntEnum):
        Circle = pcbnew.PAD_SHAPE_CIRCLE
        Oval = pcbnew.PAD_SHAPE_OVAL
        Rectangle = pcbnew.PAD_SHAPE_RECT
        RoundedRectangle = pcbnew.PAD_SHAPE_ROUNDRECT
        Trapezoid = pcbnew.PAD_SHAPE_TRAPEZOID
