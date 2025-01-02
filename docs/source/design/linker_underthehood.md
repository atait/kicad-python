# What is `python -m kigadgets` doing for you?

The KiCad application comes with its own isolated version of python. It is not designed to manage nontrivial python environments. Furthermore, its python interface is not installed in a place that your external python or pip can find.

`python -m kigadgets` creates a bidirectional link, telling `kigadgets` (this package) and `pcbnew.py` (their builtin C++ wrapper) where to find each other. The script all does this for you.

### 1. GUI startup script
First, it writes an initialization script for the pcbnew GUI's application terminal. It runs automatically when the shell opens and looks like this
```python
# File (for example): /home/myself/.config/kicad/PyShell_pcbnew_startup.py
import sys
sys.path.append("/path/to/kicad-python")
from kigadgets.board import Board
pcb = Board.from_editor()  # pcb is now a global variable in the terminal
```
**Effect:** You can now use `kigadgets` features in your GUI terminal. Quick 3-line scripts can be quite useful (examples below).

### 2. Expose `kigadgets` to all action plugins
Second, the script exposes `kigadgets` to the pcbnew GUI action plugin environment. It does this by linking this package into the "kicad/scripting/plugins" directory.

**Effect:** You can now use `kigadgets` when developing action plugins.

### 3. Expose `pcbnew` to external pythons
Third, it exposes KiCad's `pcbnew.py` to your external python environment. The path is stored in a file called `.path_to_pcbnew_module`, which is located in the `kigadgets` package installation. Since it is a file, it persists after the first time. You can override this in an environment variable `PCBNEW_PATH`.

For `import pcbnew` to work from outside the GUI, you must first `import kigadgets`.

**Effect:** You can now use the full KiCad built-in SWIG wrapper, the `kigadgets` package, and any non-GUI plugins you are developing *outside of the pcbnew application*. It is useful for batch processing, remote computers, procedural layout, continuous integration, and use in other software such as FreeCAD and various autorouters.


## Manual linking
Regualar developers should not have to do this since kigadgets 5.0 unless you are using multiple and/or custom installations of KiCAD

1. Open the pcbnew GUI application. Open its terminal and run this command
```python
import pcbnew; print(pcbnew.__file__, pcbnew.SETTINGS_MANAGER.GetUserSettingsPath())
```
This will print 2 paths. *Copy that entire line.*

> For kicad 5, replace that last command with `pcbnew.SETTINGS_MANAGER_GetUserSettingsPath()` (note the last underscore).

> If these paths have any spaces, you must put double quotes around it

2. Go back to your external command line or Terminal shell, and run this command, replacing \[paste here\] with what you copied
```bash
python -m kigadgets [paste here]
```
For example,
```bash
python -m kigadgets /usr/lib/python3/dist-packages/pcbnew.py /home/username/.config/kicad
```