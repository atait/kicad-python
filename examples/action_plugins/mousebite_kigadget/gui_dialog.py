# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-284-gf026a8e1)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MousebiteGUI
###########################################################################

class MousebiteGUI ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"kigadgets-mousebite", pos = wx.Point( 100,100 ), size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )


        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


###########################################################################
## Class MousebiteGUI
###########################################################################

class MousebiteGUI ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"kigadgets-mousebite", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer18 = wx.BoxSizer( wx.VERTICAL )

        self.m_bitmap1 = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.Point( -1,-1 ), wx.Size( -1,100 ), 0 )
        bSizer18.Add( self.m_bitmap1, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

        bSizer20 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText23 = wx.StaticText( self, wx.ID_ANY, u"Creates mousebite tabs in the Edge.Cuts layer. Location is determined by segments in the Slicing Layer. Each cutter segment must intersect two Edge.Cuts segments. Currently, only horizontal/vertical segments are supported.\nPress <Enter> to Apply.\nFully compatible with Undo/Redo (Cmd-Z/Y)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText23.Wrap( 300 )

        bSizer20.Add( self.m_staticText23, 3, wx.ALL, 5 )


        bSizer18.Add( bSizer20, 0, wx.EXPAND, 5 )

        gSizer2 = wx.GridSizer( 5, 2, 0, 0 )

        self.m_staticText24 = wx.StaticText( self, wx.ID_ANY, u"Slicing Layer", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText24.Wrap( -1 )

        gSizer2.Add( self.m_staticText24, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        m_layerComboChoices = [ u"User.Eco1", u"User.Eco2", u"User.1", u"User.2", u"User.3", u"User.4", u"User.5", u"User.6", wx.EmptyString ]
        self.m_layerCombo = wx.ComboBox( self, wx.ID_ANY, u"User.Eco1", wx.DefaultPosition, wx.DefaultSize, m_layerComboChoices, 0 )
        gSizer2.Add( self.m_layerCombo, 0, wx.ALL, 5 )

        self.m_staticText811 = wx.StaticText( self, wx.ID_ANY, u"Tab width (mm)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText811.Wrap( -1 )

        gSizer2.Add( self.m_staticText811, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.m_tab_width = wx.TextCtrl( self, wx.ID_ANY, u"3.0", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.m_tab_width, 0, wx.ALL, 5 )

        self.m_staticText01 = wx.StaticText( self, wx.ID_ANY, u"Pitch (mm)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText01.Wrap( -1 )

        gSizer2.Add( self.m_staticText01, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

        self.m_pitch = wx.TextCtrl( self, wx.ID_ANY, u"1.3", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.m_pitch, 0, wx.ALL, 5 )

        self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"Fillet radius (mm)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText8.Wrap( -1 )

        gSizer2.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

        self.m_fillet = wx.TextCtrl( self, wx.ID_ANY, u"1.0", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.m_fillet, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_staticText81 = wx.StaticText( self, wx.ID_ANY, u"Drill (mm)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText81.Wrap( -1 )

        gSizer2.Add( self.m_staticText81, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.m_drill = wx.TextCtrl( self, wx.ID_ANY, u"0.80", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.m_drill, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_staticText813 = wx.StaticText( self, wx.ID_ANY, u"Inset (mm)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText813.Wrap( -1 )

        gSizer2.Add( self.m_staticText813, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

        self.m_inset = wx.TextCtrl( self, wx.ID_ANY, u"0.25", wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer2.Add( self.m_inset, 0, wx.ALL, 5 )


        bSizer18.Add( gSizer2, 1, wx.EXPAND, 5 )

        terminal_choice = wx.StdDialogButtonSizer()
        self.terminal_choiceOK = wx.Button( self, wx.ID_OK )
        terminal_choice.AddButton( self.terminal_choiceOK )
        self.terminal_choiceCancel = wx.Button( self, wx.ID_CANCEL )
        terminal_choice.AddButton( self.terminal_choiceCancel )
        terminal_choice.Realize();

        bSizer18.Add( terminal_choice, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


        self.SetSizer( bSizer18 )
        self.Layout()
        bSizer18.Fit( self )

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


