''' Get reload: useful for on-the-fly updates to action plugin scripts without refreshing plugins

        from kigadgets import reload
        def run(self):
            import action_script  # Only runs the first time during this instance of pcbnew, even if file changed
            reload(action_script)  # Forces reimport, rerunning, and any updates to source
'''
try:
    from importlib import reload
except ImportError:
    try:
        from imp import reload
    except ImportError:
        try:
            _ = reload
        except NameError as err:
            def reload(mod):
                pass


def notify(*args):
    ''' Show text in a popup window while in the GUI.
        Arguments act the same as print(\*args).
        Not the best debugging tool ever created, but
        it is handy for debugging action plugins::

            notify('Debug info:', 'x =', x)
    '''
    text = ' '.join(str(arg) for arg in args)
    try:
        import wx
    except ImportError:
        print(text)
        return
    try:
        dialog = wx.MessageDialog(None, text, 'kigadgets notification', wx.OK)
        sg = dialog.ShowModal()
        return sg
    except:
        print(text)


def query_user(prompt=None, default=''):
    ''' Simple GUI dialog asking for a single value.
        Returns what was entered by the user as a string::

            retstr = query_user('Enter a drill width in mm', 0.5)
            if retstr is None:
                return
            drill = float(retstr)
    '''
    if prompt is None:
        prompt = 'Enter a value'
    try:
        import wx
    except ImportError:
        # Try from the command line. Unused since it might hang
        # retval = input(prompt + ': ')
        # return retval
        raise
    default = str(default)
    dialog = wx.TextEntryDialog(None, prompt, 'kigadgets query', default, wx.CANCEL | wx.OK)
    sg = dialog.ShowModal()
    if sg != wx.ID_OK:
        return None
    return dialog.GetValue()
