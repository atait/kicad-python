''' Entry point for onepush_script.py
    On OSX, you can hotkey the corresponding menu item: "One Push"
'''
from kigadgets import kireload
import pcbnew
import os, sys

class OnePush(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "One Push"  # it is important that this matches the shortcut
        self.category = "Macro speedup"
        self.description = ("Run a script like a macro at the touch of a button. "
                           "Edit the script at " + os.path.join(os.path.dirname(__file__), "onepush_script.py"))
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__),
            "icons/photon-32.png")
        self.has_run = False

    def Run(self):
        # The entry function of the plugin that is executed on user action
        import onepush_script
        if self.has_run:
            kireload(onepush_script)
        self.has_run = True

