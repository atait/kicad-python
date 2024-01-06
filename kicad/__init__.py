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
__version__ = '0.3.0'

#: centralized import with fallback.
#: Necessary for documentation and environment patching outside of application
#: Import in this module in subpackages with
#: from kicad import pcbnew_bare as pcbnew
import os, sys
from kicad.environment import get_pcbnew_module
from kicad.exceptions import notify

# Find SWIG pcbnew
try:
    pcbnew_bare = get_pcbnew_module()
except EnvironmentError:
    print('Warning: pcbnew.py is not found or PCBNEW_PATH is corrupted. '
        'Only environment commands will be available')
    pcbnew_bare = None


# if `enum` cannot be imported (windoze!) we provide our own copy
try:
    import enum
except ImportError:
    import sys, os
    module_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.join(module_dir,'3rdparty'))


# Low-level "new" function that avoids initializer
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


# Unify v5/6/7 APIs
if pcbnew_bare is None:
    SWIG_version = None
    class SWIGtype: pass
else:
    # Determine version and map equivalent objects into consistent names
    ver = [int(x) for x in pcbnew_bare.GetMajorMinorVersion().split('.')]
    if ver[0] == 7 or (ver[0] == 6 and ver[1] == 99):
        SWIG_version = 7
    elif ver[0] == 6 or (ver[0] == 5 and ver[1] == 99):
        SWIG_version = 6
    elif ver[0] == 5 or (ver[0] == 4 and ver[1] == 99):
        SWIG_version = 5
    else:
        print('Version {} not supported by kicad-python. Some functionality might not work')
        SWIG_version = 7 if ver[0] > 7 else 5

    if SWIG_version == 7:
        class SWIGtype:
            Zone = pcbnew_bare.ZONE
            Track = pcbnew_bare.PCB_TRACK
            Via = pcbnew_bare.PCB_VIA
            Shape = pcbnew_bare.PCB_SHAPE
            Text = pcbnew_bare.PCB_TEXT
            Footprint = pcbnew_bare.FOOTPRINT
            FpText = pcbnew_bare.FP_TEXT
            FpShape = pcbnew_bare.FP_SHAPE
            # Changed in v7
            Point = pcbnew_bare.VECTOR2I
            Size = pcbnew_bare.VECTOR2I
            Rect = pcbnew_bare.BOX2I
            # End v7 changes
    elif SWIG_version == 6:
        class SWIGtype:
            # Changed in v6
            Zone = pcbnew_bare.ZONE
            Track = pcbnew_bare.PCB_TRACK
            Via = pcbnew_bare.PCB_VIA
            Shape = pcbnew_bare.PCB_SHAPE
            Text = pcbnew_bare.PCB_TEXT
            Footprint = pcbnew_bare.FOOTPRINT
            FpText = pcbnew_bare.FP_TEXT
            FpShape = pcbnew_bare.FP_SHAPE
            # End v6 changes
            Point = pcbnew_bare.wxPoint
            Size = pcbnew_bare.wxSize
            Rect = pcbnew_bare.EDA_RECT
    else:
        class SWIGtype:
            Zone = pcbnew_bare.ZONE_CONTAINER
            Track = pcbnew_bare.TRACK
            Via = pcbnew_bare.VIA
            Shape = pcbnew_bare.DRAWSEGMENT
            Text = pcbnew_bare.TEXTE_PCB
            Footprint = pcbnew_bare.MODULE
            FpText = pcbnew_bare.TEXTE_MODULE
            FpShape = pcbnew_bare.EDGE_MODULE
            Point = pcbnew_bare.wxPoint
            Size = pcbnew_bare.wxSize
            Rect = pcbnew_bare.EDA_RECT


# Broken isinstance detection of inheritance in v7
def instanceof(item, klass):
    if isinstance(klass, (tuple, list)):
        for kls in klass:
            if instanceof(item, kls):
                return True
    if isinstance(item, klass):  # This should hit in v6
        return True
    class_of_name = klass.__name__ + '_ClassOf'
    try:
        class_of_fun = getattr(pcbnew_bare, class_of_name)
        return class_of_fun(item)
    except AttributeError:
        return False


# Expose the basic classes to this package's top level
if pcbnew_bare:
    from .units import *
    from .point import Point
    from .size import Size
    import kicad.pcbnew
