__version__ = "0.5.1"

#: centralized import with fallback.
#: Necessary for documentation and environment patching outside of application
#: Import in this module in subpackages with
#: from kigadgets import pcbnew_bare as pcbnew
import os, sys
from kigadgets.environment import get_pcbnew_module
from kigadgets.util import notify, query_user, kireload
from kigadgets.exceptions import put_import_warning_on_kicad

# Find SWIG pcbnew
try:
    pcbnew_bare = get_pcbnew_module()
except EnvironmentError:
    print(
        "kigadgets: pcbnew.py is not found or PCBNEW_PATH is corrupted. "
        "Only kigadget.environment commands will be available"
    )
    pcbnew_bare = None


# Low-level "new" function that avoids initializer
class __BareClass(object):
    pass


def new(class_type, instance):
    """Returns an object of class without calling __init__.

    This could lead to inconsistent objects, use only when you
    know what you're doing.
    In kigadgets this is used to construct wrapper classes
    before injecting the native object.
    """
    obj = __BareClass()
    obj.__class__ = class_type
    obj._obj = instance
    return obj


def pcbnew_version(asstr=False):
    try:
        verstr = pcbnew_bare.GetMajorMinorVersion()
    except AttributeError:
        verstr = "5.0"
    if asstr:
        return verstr
    ver = tuple(int(x) for x in verstr.split("."))
    if len(ver) < 2:
        ver = (ver[0], 0)
    return ver


# Unify v5/6/7 APIs
SWIG_version = None
class SWIGtype:
    pass
if pcbnew_bare is not None:
    # Determine version and map equivalent objects into consistent names
    ver = pcbnew_version()
    if ver[0] >= 9 or (ver[0] == 8 and ver[1] == 99):
        SWIG_version = 9
    elif ver[0] == 8 or (ver[0] == 7 and ver[1] == 99):
        SWIG_version = 8
    elif ver[0] == 7 or (ver[0] == 6 and ver[1] == 99):
        SWIG_version = 7
    elif ver[0] == 6 or (ver[0] == 5 and ver[1] == 99):
        SWIG_version = 6
    elif ver[0] == 5 or (ver[0] == 4 and ver[1] == 99):
        SWIG_version = 5
    else:
        print(
            "Version {} not supported by kigadgets. "
            "Some functionality might not work".format(ver)
        )
        SWIG_version = 8

    # if SWIG_version == 9:
    #     # It appears to be the same as 8, based on the pytests.
    if SWIG_version >= 8:
        class SWIGtype:
            Zone = pcbnew_bare.ZONE
            Track = pcbnew_bare.PCB_TRACK
            Via = pcbnew_bare.PCB_VIA
            Shape = pcbnew_bare.PCB_SHAPE
            Text = pcbnew_bare.PCB_TEXT
            Footprint = pcbnew_bare.FOOTPRINT
            Point = pcbnew_bare.VECTOR2I
            Size = pcbnew_bare.VECTOR2I
            Rect = pcbnew_bare.BOX2I
            # Changed in v8
            FpText = pcbnew_bare.PCB_TEXT
            FpShape = pcbnew_bare.PCB_SHAPE
            # End v8 changes
    elif SWIG_version == 7:
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
    elif SWIG_version == 5:
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
    class_of_name = klass.__name__ + "_ClassOf"
    try:
        class_of_fun = getattr(pcbnew_bare, class_of_name)
        return class_of_fun(item)
    except AttributeError:
        return False


# Alters sys.modules so that "import kicad" gives more information
put_import_warning_on_kicad()

# Expose the basic classes to this package's top level
from kigadgets.units import DEFAULT_UNIT_IUS
if pcbnew_bare:
    from kigadgets.point import Point
    from kigadgets.size import Size
    # CAD modules must be imported explicitly
else:
    Point = None
    Size = None
