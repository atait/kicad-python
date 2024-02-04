''' Entry point for onepush_script.py
    On OSX, you can hotkey the corresponding menu item: "One Push"
'''
import wx
import pcbnew
import os, sys
from kigadgets import kireload

from mousebite_kigadget.gui_dialog import MousebiteGUI
from mousebite_kigadget import objview

class MouseBiteDialog(MousebiteGUI):
    _previous_selections = None

    def __init__(self, parent):
        super(MouseBiteDialog, self).__init__(parent)
        self.m_bitmap1.SetBitmap(wx.Bitmap(
            os.path.join(os.path.dirname(__file__), 'icons/mouse-128.png'), wx.BITMAP_TYPE_ANY
        ))
        self.terminal_choiceOK.SetDefault()

        self.setup_GUI_selections(type(self)._previous_selections)

    def get_user_selections(self):
        # Process files and which boards will be done
        sel = objview()
        sel.slay = self.m_layerCombo.GetValue()
        sel.tab_width = float(self.m_tab_width.GetValue())
        sel.fillet = float(self.m_fillet.GetValue())
        sel.pitch = float(self.m_pitch.GetValue())
        sel.drill = float(self.m_drill.GetValue())
        sel.inset = float(self.m_inset.GetValue())

        type(self)._previous_selections = sel
        return sel

    def setup_GUI_selections(self, sel=None):
        if sel is None:
            return
        self.m_layerCombo.SetValue(sel.slay)
        def set_float(textctrl, value):
            val_str = '{:.2f}' if value < 1.0 else '{:.1f}'
            textctrl.SetValue(val_str.format(value))
        set_float(self.m_tab_width, sel.tab_width)
        set_float(self.m_fillet, sel.fillet)
        set_float(self.m_pitch, sel.pitch)
        set_float(self.m_drill, sel.drill)
        set_float(self.m_inset, sel.inset)

class MouseBite(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "MouseBite"  # it is important that this matches the shortcut
        self.category = "Fabrication"
        self.description = ("MouseBites on Eco1")
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__),
            "icons/mouse-32.png")

    def Run(self):
        # The entry function of the plugin that is executed on user action
        from . import mousebite_script
        kireload(mousebite_script)

        from .mousebite_script import Board
        pcb = Board.from_editor()

        # Quick run with defaults
        if False:
            mousebite_script.main(pcb)
            pcbnew.Refresh()
            return

        # show dialog
        _pcbnew_frame = [x for x in wx.GetTopLevelWindows() if 'PCB Editor' in x.GetTitle()][0]
        main_dialog = MouseBiteDialog(_pcbnew_frame)
        main_res = main_dialog.ShowModal()
        sel = main_dialog.get_user_selections()
        if main_res == wx.ID_OK:
            mousebite_script.main(pcb, sel)
            pcbnew.Refresh()
