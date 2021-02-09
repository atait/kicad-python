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
try:
    pcbnew_bare = __import__('pcbnew')
except ImportError:
    pcbnew_swig_path = os.environ.get('PCBNEW_PATH', None)
    spoofing_for_documentation = os.environ.get('KICAD_PYTHON_IN_SPHINX_GENERATION', '0')
    if pcbnew_swig_path:
        if os.path.basename(pcbnew_swig_path) != 'pcbnew.py':
            raise EnvironmentError(
                'Incorrect location for \'PCBNEW_PATH\' ({}).'
                ' It should point to a file called pcbnew.py'.format(pcbnew_swig_path))
        if not os.path.isfile(pcbnew_swig_path):
            raise EnvironmentError(
                'Incorrect location for \'PCBNEW_PATH\' ({}).'
                ' File does not exist'.format(pcbnew_swig_path))
        sys.path.insert(0, os.path.dirname(pcbnew_swig_path))
        pcbnew_bare = __import__('pcbnew')
    elif spoofing_for_documentation == '1':
        class SphinxEnumPhony:
            def __getattr__(self, attr):
                return 0
        pcbnew_bare = SphinxEnumPhony()
    else:
        raise ImportError(
            'pcbnew is required by kicad-python.'
            ' Set the environment variable with:'
            '\n    export PCBNEW_PATH=/path/to/pcbnew.py.'
            '\nThis path can be located by going in the pcbnew application, opening a terminal, and typing'
            '\n    import pcbnew; print(pcbnew.__file__)')


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
