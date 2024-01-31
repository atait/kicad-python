''' kireload is the builtin reload, which comes from different places depending on python version.
    It is useful for on-the-fly updates to action plugin scripts without refreshing plugins.::

        from kigadgets import kireload
        def run(self):
            import action_script  # Only runs the first time during this instance of pcbnew, even if file changed
            kireload(action_script)  # Forces reimport, rerunning, and any updates to source
'''
from functools import wraps
from Pyro5.errors import DaemonError

try:
    from importlib import reload as kireload
except ImportError:
    try:
        from imp import reload as kireload
    except ImportError:
        try:
            kireload = reload
        except NameError as err:
            def kireload(mod):
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


def _do_register(daemon, result):
    """Registers the result in the Pyro daemon
    if it's not already there."""
    if pyro_id := getattr(result, "_pyroId", None):
        if daemon.objectsById[pyro_id] is not result:
            daemon.register(result, force=True)
    else:
        daemon.register(result)


def register_return(method):
    """Decorator to register the return value
    of a method in the Pyro daemon."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        daemon = self._pyroDaemon
        result = method(self, *args, **kwargs)
        _do_register(daemon, result)
        return result

    return wrapper


def register_yielded(method):
    """Decorator to register the return value
    of a method in the Pyro daemon."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        daemon = self._pyroDaemon
        for result in method(self, *args, **kwargs):
            _do_register(daemon, result)
            yield result
    return wrapper
