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

#: centralized import with fallback.
#: Necessary for documentation and environment patching outside of application
#: Import in this module in subpackages with
#: from kicad import pcbnew_bare as pcbnew
import os, sys
from kicad.environment import get_pcbnew_module

try:
    pcbnew_bare = get_pcbnew_module()
except EnvironmentError:
    print('Warning: pcbnew.py is not found or PCBNEW_PATH is corrupted. '
        'Only environment commands will be available')
    pcbnew_bare = None
if pcbnew_bare:
    from .units import *
    from .point import Point
    from .size import Size
    import kicad.pcbnew

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


# Determine version
if pcbnew_bare is None:
    SWIG_version = None
    class SWIGtype: pass
else:
    if hasattr(pcbnew_bare, 'PCB_TRACK'):
        SWIG_version = 6
    else:
        SWIG_version = 5

    if SWIG_version == 6:
        class SWIGtype:
            Zone = pcbnew_bare.ZONE
            Track = pcbnew_bare.PCB_TRACK
            Via = pcbnew_bare.PCB_VIA
            Shape = pcbnew_bare.PCB_SHAPE
            Text = pcbnew_bare.PCB_TEXT
            Footprint = pcbnew_bare.FOOTPRINT
            FpText = pcbnew_bare.FP_TEXT
            FpShape = pcbnew_bare.FP_SHAPE
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
