""" Utilities for interacting with pcbnew in GUI and headless modes.

    "reload" is the builtin reload, which comes from different places depending on python version.
    "kireload" is useful for on-the-fly updates to action plugin scripts without refreshing plugins.::

        from kigadgets import kireload
        def run(self):
            import action_script  # Only runs the first time during this instance of pcbnew, even if file changed
            kireload(action_script)  # Forces reimport, rerunning, and any updates to source

    "notify" and "query_user" decide whether to show a GUI dialog or print to console
    based on whether the code is running in GUI mode or headless mode.
"""

from typing import Any, Optional, Union

try:
    import wx
except (ImportError, AttributeError):
    wx = None


try:
    from importlib import reload as kireload
except ImportError:
    try:
        from imp import reload as kireload
    except ImportError:
        kireload = locals().get('reload', None)
        if kireload is None:
            def kireload(mod: Any) -> None:
                pass


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
