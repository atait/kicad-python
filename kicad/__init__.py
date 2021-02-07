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

from .units import *
from .point import *
from .size import *

# if `enum` cannot be imported (windoze!) we provide our own copy
try:
    import enum
except ImportError:
    import sys, os
    module_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.join(module_dir,'3rdparty'))

class BareClass(object):
    pass


def new(class_type, instance):
    """Returns an object of class without calling __init__.

    This could lead to inconsistent objects, use only when you
    know what you're doing.
    In kicad-python this is used to construct wrapper classes
    before injecting the native object.
    """
    obj = BareClass()
    obj.__class__ = class_type
    obj._obj = instance
    return obj
