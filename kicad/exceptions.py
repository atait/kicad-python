#  Copyright 2015 Miguel Angel Ajo Pelayo <miguelangel@ajo.es>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
from functools import wraps

class NoDefaultUnits(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def notify(*args):
    ''' Show text in a popup window while in the GUI.
        Arguments act the same as print(*args)
        It is not the best debugging tool ever created, but
        it is handy for debugging action plugins
    '''
    text = ' '.join(str(arg) for arg in args)
    try:
        import wx
    except ImportError:
        print(text)
        return
    try:
        dialog = wx.MessageDialog(None, text, 'kicad-python debug output', wx.OK)
        sg = dialog.ShowModal()
        return sg
    except:
        print(text)

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
