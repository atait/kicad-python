from functools import wraps

class NoDefaultUnits(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


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


deprecate_warn_fun = notify  # print is sometimes good
def deprecate_member(old, new, deadline='v0.5.0'):
    def regular_decorator(klass):
        def auto_warn(fun):
            from_str = klass.__name__ + '.' + old
            to_str = klass.__name__ + '.' + new
            header = 'Deprecation warning (deadline {}): '.format(deadline)
            map_str = '{} -> {}'.format(from_str, to_str)
            @wraps(fun)
            def warner(*args, **kwargs):
                deprecate_warn_fun(header + map_str)
                return fun(*args, **kwargs)
            warner.__doc__ = 'Deprecation notice. Use `{}` instead'.format(new)
            return warner

        new_meth = getattr(klass, new)
        if isinstance(new_meth, property):
            aug_meth = property(
                auto_warn(new_meth.fget),
                auto_warn(new_meth.fset),
                auto_warn(new_meth.fdel)
            )
        else:
            aug_meth = auto_warn(new_meth)
        setattr(klass, old, aug_meth)
        return klass
    return regular_decorator
