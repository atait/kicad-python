# What is `link_kigadgets_to_pcbnew` doing for you?

The KiCad application comes with its own isolated version of python. It is not designed to install any new packages like this one. Furthermore, its python API is not installed in a place that your external python or pip can find.

`link_kigadgets_to_pcbnew` creates a bidirectional link, telling `kigadgets` (this package) and `pcbnew.py` (their builtin C++ wrapper) where to find each other. The script all does this for you.

## GUI startup script
First, it writes an initialization script for the pcbnew GUI's application terminal. It runs automatically when the shell opens and looks like this
```python
# File (for example): /home/myself/.config/kicad/PyShell_pcbnew_startup.py
import sys
sys.path.append("/env/from_which/you_called/link_kigadgets/site-packages")
from kigadgets.board import Board
pcb = Board.from_editor()  # pcb is now a global variable in the terminal
```
**Effect:** You can now use `kigadgets` features in your GUI terminal. Quick 3-line scripts can be quite useful (examples below).

## Expose `kigadgets` to all action plugins
Second, the script exposes `kigadgets` to the pcbnew GUI action plugin environment. It does this by linking this package into the "kicad/scripting/plugins" directory.

**Effect:** You can now use `kigadgets` when developing action plugins.

## Expose `pcbnew` to external pythons
Third, it exposes KiCad's `pcbnew.py` to your external python environment. The path is stored in a file called `.path_to_pcbnew_module`, which is located in the `kigadgets` package installation. Since it is a file, it persists after the first time. You can override this in an environment variable `PCBNEW_PATH`.

For `import pcbnew` to work from outside the GUI, you must first `import kigadgets`.

**Effect:** You can now use the full KiCad built-in SWIG wrapper, the `kigadgets` package, and any non-GUI plugins you are developing *outside of the pcbnew application*. It is useful for batch processing, remote computers, procedural layout, continuous integration, and use in other software such as FreeCAD and various autorouters.

