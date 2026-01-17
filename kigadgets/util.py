""" Utilities for interacting with pcbnew in GUI and headless modes.

    "kireload" is useful for on-the-fly updates to action plugin scripts without manually refreshing plugins.::

        from kigadgets import kireload
        class MyScript(pcbnew.ActionPlugin):
            def Run(self):
                import myscript.core
                kireload(myscript.core)
                # Any source changes in myscript/core.py have now been picked up
                myscript.core.run()

    "notify" and "query_user" decide whether to show a GUI dialog or print to console
    based on whether the code is running in GUI mode or headless mode.
"""

from typing import Any, Optional, Union
import importlib
import sys
import traceback

try:
    import wx
except (ImportError, AttributeError):
    wx = None


try:
    from importlib import reload as _kireload
except ImportError:
    try:
        from imp import reload as _kireload
    except ImportError:
        _kireload = locals().get('reload', None)
        if _kireload is None:
            def _kireload(mod: Any) -> None:
                pass


def kireload(mod: Any) -> None:
    """Reload a module. If it is not in sys.modules, it will be imported."""
    if isinstance(mod, str):
        if mod not in sys.modules:
            try:
                importlib.import_module(mod)
            except Exception as err:
                notify("Import failed for", mod, '\n\n', traceback.format_exc())
            return
        else:
            mod = sys.modules[mod]
    try:
        _kireload(mod)
    except Exception as err:
        notify("Reload failed for", mod, '\n\n', traceback.format_exc())


def notify(*args: Any) -> Optional[int]:
    """Show text in a popup window while in the GUI.
    Arguments act the same as print(args).
    Not the best debugging tool ever created, but
    it is handy for debugging action plugins::

        notify('Debug info:', 'x =', x)

    """
    text = " ".join(str(arg) for arg in args)
    if wx:
        parent = get_app_window()
        dialog = wx.MessageDialog(parent, text, "kigadgets notification", wx.OK)
        sg = dialog.ShowModal()
        return sg
    else:
        print(text)


def query_user(prompt: Optional[str] = None, default: Union[str, int, float] = "") -> Optional[str]:
    """Simple GUI dialog asking for a single value.
    Returns what was entered by the user as a string::

        retstr = query_user('Enter a drill width in mm', 0.5)
        if retstr is None:  # User cancelled
            return
        else:
            drill = float(retstr)
    """
    if not wx:
        print("Skipping query_user outside of GUI")
        return None
    if prompt is None:
        prompt = "Enter a value"
    default = str(default)
    parent = get_app_window()
    dialog = wx.TextEntryDialog(parent, prompt, "kigadgets query", default, wx.CANCEL | wx.OK)
    sg = dialog.ShowModal()
    if sg != wx.ID_OK:
        return None
    return dialog.GetValue()


def get_app_window() -> Optional[Any]:
    """Get a parent for action plugin dialogs.
    Returns None if outside of GUI
    """
    if not wx:
        return None
    for frame in wx.GetTopLevelWindows():
        if "PCB Editor" in frame.GetTitle():
            return frame
    else:
        return None


def in_GUI() -> bool:
    return get_app_window() is not None
