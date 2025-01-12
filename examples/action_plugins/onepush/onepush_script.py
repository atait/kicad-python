''' Are you tired of the pcbnew GUI terminal? Me too.
    This script can be run at the press of a button (or hotkey) in the Pcbnew GUI.
    Great for semi-interactive coding.

    Usage:
    - Clear out or comment the default behavior
    - Write your own stuff below
    - In Pcbnew GUI, click the "One Push" button
        - or press Shift+Cmd+R (assuming Shift+Cmd+R is your shortcut you chose)

    See onepush_script_examples.py for documentation on how this file works and how to setup.
'''
# Default behavior. Comment these lines when ready to run your own code
from kigadgets import kireload
from onepush import onepush_script_examples
kireload(onepush_script_examples)  # Forces reimport, rerunning, and any updates to source

onepush_script_examples.hello_world()
onepush_script_examples.default()
