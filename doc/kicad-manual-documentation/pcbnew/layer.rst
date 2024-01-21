layers
======

.. automodule:: kicad.pcbnew.layer

.. autoclass:: LayerSet
   :members:
   :undoc-members:

.. autofunction:: get_board_layer_id

.. autofunction:: get_board_layer_name

.. autofunction:: get_std_layer_name

.. autofunction:: get_std_layer_id

Layer enumerations
------------------
.. code-block:: python

    class Layer(IntEnum):
        Front           = pcbnew.F_Cu
        Back            = pcbnew.B_Cu

        FrontAdhesive   = pcbnew.F_Adhes
        BackAdhesive    = pcbnew.B_Adhes
        FrontSilkScreen = pcbnew.F_SilkS
        BackSilkScreen  = pcbnew.B_SilkS
        FrontPaste      = pcbnew.F_Paste
        BackPaste       = pcbnew.B_Paste
        FrontMask       = pcbnew.F_Mask
        BackMask        = pcbnew.B_Mask

        DrawingsUser    = pcbnew.Dwgs_User
        CommentsUser    = pcbnew.Cmts_User
        ECO1User        = pcbnew.Eco1_User
        ECO2User        = pcbnew.Eco2_User

        EdgeCuts        = pcbnew.Edge_Cuts
        Margin          = pcbnew.Margin
        FrontFab        = pcbnew.F_Fab
        BackFab         = pcbnew.B_Fab
        FrontCourtyard  = pcbnew.F_CrtYd
        BackCourtyard   = pcbnew.B_CrtYd
