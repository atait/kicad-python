import sys
from functools import wraps
from kigadgets.util import notify


class NoDefaultUnits(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def put_import_warning_on_kicad():
    """Legacy scripts may attempt to import "kicad"
    Rather than ImportError, tell them about the rename
    """

    class NoImport(object):
        __file__ = None

        def __getattr__(self, attr):
            raise NameError(
                "kicad-python has been renamed to kigadgets. Change"
                "\n    from kicad.pcbnew.board import ..."
                "\n        # to"
                "\n    from kigadgets.board import ..."
            )

    sys.modules["kicad"] = NoImport()


deprecate_warn_fun = notify  # print is sometimes good


def deprecate_member(old, new, deadline="v0.5.0"):
    def regular_decorator(klass):
        def auto_warn(fun):
            from_str = klass.__name__ + "." + old
            to_str = klass.__name__ + "." + new
            header = f"Deprecation warning (deadline {deadline}): "
            map_str = f"{from_str} -> {to_str}"

            @wraps(fun)
            def warner(*args, **kwargs):
                deprecate_warn_fun(header + map_str)
                return fun(*args, **kwargs)

            warner.__doc__ = f"Deprecation notice. Use `{new}` instead"
            return warner

        new_meth = getattr(klass, new)
        if isinstance(new_meth, property):
            aug_meth = property(
                auto_warn(new_meth.fget),
                auto_warn(new_meth.fset),
                auto_warn(new_meth.fdel),
            )
        else:
            aug_meth = auto_warn(new_meth)
        setattr(klass, old, aug_meth)
        return klass

    return regular_decorator
