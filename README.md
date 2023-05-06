# kicad-python: atait fork
Development of a new Python scripting API for KiCad
based on Piers Titus van der Torren work and comunity
feedback to create a less C++ tied API.

A second intention of this new API is also to provide
better documentation via sphinx.

This repo has been fully tested with KiCAD 5/6 and partially tested with KiCAD 7.
Note: the KiCAD/kicad-python and pointhi/kicad-python and PyPI:kicad-python are not working with KiCAD versions 5, 6, or 7.

## Description
KiCAD and `pcbnew` expose a python API that allows plugins and other procedural processing of PCB layouts. There are limitations of using this API directly: [its documentation](https://docs.kicad.org/doxygen-python/namespacepcbnew.html) is empty; it is a clunky SWIG/C-style API with custom datatypes for things like lists; and it exposes too much functionality on equal footing.

This package is a more pythonic wrapper around the `pcbnew` API. It implements patterns such as objects, properties, and iterables. It performs more intuitive unit and layer handling. It only exposes functionality most relevant to editing boards, the idea being that native functionality can always be accessed through the wrapped objects if needed.

### An excerpt
A simple pythonic script might look like this
```python
print([track.layer for track in board.tracks])
print([track.width for track in board.tracks])
```
which produces
```
[F.Cu, B.Cu, B.Cu]
[0.8, 0.8, 0.6]
```
This simple interface is not possible with the C++ SWIG API. The python wrapper is handling things like calling the (sometimes hard to find) function names, sanitizing datatypes, looking up layers, and enabling the generator pattern.

## Installation

<!-- 1. Users: 
```bash
pip install kicad
```
 
For developers: Clone this repository to any location, and run `pip install kicad-python/.` -->

1. 
```
git clone git@github.com:atait/kicad-python
pip install kicad-python/.
```

2. Open the pcbnew GUI application. Open its terminal ![](doc/pcbnew_terminal_icon.png) and run these commands in kicad 6 or 7
```python
>>> import pcbnew
>>> pcbnew.__file__
# [Path A]: This will give something like "/usr/lib/python3/dist-packages/pcbnew.py"
>>> pcbnew.SETTINGS_MANAGER.GetUserSettingsPath()
# [Path B]: This will give something like "home/username/.config/kicad"
```
For kicad 5, replace that last command with `pcbnew.SETTINGS_MANAGER_GetUserSettingsPath()` (note the last underscore).

3. Go back to your external command line or Terminal shell, and run this command, replacing Path A and Path B with what you got above.
```bash
link_kicad_python_to_pcbnew [Path A] [Path B]
```
For example,
```bash
link_kicad_python_to_pcbnew /usr/lib/python3/dist-packages/pcbnew.py /home/username/.config/kicad
```

4. Try it out! Quit and reopen pcbnew application. Open its terminal, then run
```python
pcb.add_circle((100, 100), 20, 'F.SilkS'); pcbnew.Refresh()  # Works in anything (F.SilkS > alias to -> F.Silkscreen)
# or
pcb.add_circle((100, 100), 20, 'F.Silkscreen'); pcbnew.Refresh()  # Works in 6/7 only
```

### Troubleshooting
\[**cannot write to package directory**\] Step 3 attempts to write a file in the installation of `kicad-python`. If that fails because you don't have file permissions or something, you can instead set the environment variable "PCBNEW_PATH" to the first path to Path A. Put this line in your .bashrc or .zshrc
```bash
# In general: export PCBNEW_PATH="[Path A]"
export PCBNEW_PATH=/usr/lib/python3/dist-packages/pcbnew.py  # For example
```

\[**python version errors**\] Some external libraries might be compiled. `pcbnew.py` does depend on compiled code (called `_pcbnew.so`). That means not all versions of python work. You may get errors in your terminal that say "version `GLIBCXX_3.4.30' not found". To fix this, determine the version used in KiCad with this command in the GUI terminal
```python
>>> import sys; sys.version_info
# sys.version_info(major=3, minor=10, ...)
```
Then, in your external terminal, create a conda environment with that same python version. Run the shell commands again, and do the rest of your batch processing within this conda environment. Note, sometimes python 3.8 so-files will work with 3.10, but matching these versions is the best way to guarantee compatibility.

\[**Upgrading kicad**\] User configuration directories are different for versions 6 and 7. You may not want to keep multiple copies of script code. One approach is to keep all 3rd party code in `~/.config/kicad/scripting` (Linux), and then symbolic link that into the specific version directory.
```bash
ln -s ~/.config/kicad/scripting ~/.config/kicad/7.0/scripting
```
In *Step 3* above, you can then use either path for Path B: ".../kicad" or ".../kicad/7.0".

### What is `link_kicad_python_to_pcbnew` doing for you?
As long as the above procedure works, you do not have to read this part.

The KiCad application comes with its own isolated version of python. It is not designed to install any new packages like this one. Furthermore, its python API is not installed in a place that your external python or pip can find.

`link_kicad_python_to_pcbnew` creates a bidirectional link, telling `kicad-python` (this package) and `pcbnew.py` (their builtin C++ wrapper) where to find each other. The script all does this for you.

First, it writes an initialization script for the pcbnew GUI's application terminal. It runs automatically when the shell opens and looks like this
```python
# File (for example): /home/myself/.config/kicad/PyShell_pcbnew_startup.py
import sys
sys.path.append("/path/to/your/kicad-python/")
from kicad.pcbnew.board import Board
pcb = Board.from_editor()  # pcb is now a global variable in the terminal
```
**Effect:** You can now use `kicad-python` features in your GUI terminal. Quick 3-line scripts can be quite useful (examples below).

Second, the script exposes `kicad-python` to the pcbnew GUI action plugin environment. It does this by linking this package into the "kicad/scripting/plugins" directory.

**Effect:** You can now use `kicad-python` when developing action plugins.

Third, it exposes KiCad's `pcbnew.py` to your external python environment. The path is stored in a file called `.path_to_pcbnew_module`, which is located in the `kicad-python` package installation. Since it is a file, it persists after the first time. You can override this in an environment variable `PCBNEW_PATH`.

**Effect:** You can now use the full KiCad built-in SWIG wrapper, the `kicad-python` package, and any non-GUI plugins you are developing *outside of the pcbnew application*. It is useful for batch processing, remote computers, procedural layout, continuous integration, and use in other software such as FreeCAD and various autorouters.

### pykicad
[pykicad](https://github.com/dvc94ch/pykicad) is an excellent package written by David Craven. It is complementary to this one. `kicad-python` wraps the SWIG library provided by KiCAD devs, while `pykicad` works independently by implementing its own parser of ".kicad_pcb" files. This means that `pykicad` is pure python, while `kicad-python` is not. It also means that `kicad-python` can work within the pcbnew GUI terminal. It can also control GUI features, such as refreshing display, processing based on selections, and moving the view window. 

Both packages work for batch processing; however, ".kicad_pcb" format changed between versions. Because it wraps the official kicad API, `kicad-python` can also adapt to file format updates - this version should work with any version of KiCad 5/6/7/(8?)

## Examples
These all should work in the pcbnew 5 or 6 GUI terminal on Mac/Windows/Linux.

### Hide silkscreen labels of selected footprints
```python
for m in pcb.modules:
    if m.is_selected:
        m.referenceLabel.visible = False
pcbnew.Refresh()
```

### Move all silk labels to fab layers
Instead, we can keep them on Fab layers so we can still see them while designing the PCB.
```python
for m in pcb.modules:
    ref = m.referenceLabel
    if ref.layer == Layer.FrontSilkScreen:
        ref.layer = Layer.FrontFab
    elif ref.layer == Layer.BackSilkScreen:
        ref.layer = Layer.BackFab
pcbnew.Refresh()
```

### Give unique references to every footprint
Making arrays of components can lead to massive reference conflicts. References should be unique, even if you don't care exactly what they are. Very useful for panelization.
```python
from collections import defaultdict
counters = defaultdict(lambda: 1)
for m in pcb.modules:
    component_class = m.reference[0]
    counters[component_class] += 1
    m.reference = '{}{:03d}'.format(component_class, counters[component_class])
pcbnew.Refresh()
```
The `:03d` means three decimal places like "C003". Iteration order is not guaranteed, although you could figure it out using the `Module.position` properties.

### Change all drill sizes
Because planning ahead doesn't always work
```python
for v in pcb.vias:
    if v.drill > 0.4 and v.drill < 0.6:
        v.drill = 0.5
pcbnew.Refresh()
```

### Put silkscreen over tracks
Not sure why to do this besides a nice look.
```python
for t in pcb.tracks:
    new_width = t.width * 1.1
    pcb.add_line(t.start, t.end, 'F.SilkS' if t.layer == 'F.Cu' else 'B.Silks', new_width)
pcbnew.Refresh()
```

### Procedural layout
Suppose you want to test various track width resistances.
```python
y = 0
length = 50
widths = [.12, .24, .48, .96]
r_contact = 5
for w in widths:
    pcb.add_track([(0, y), (length, y)], 'F.Cu', width=w)
    for lay in ['F.Cu', 'F.Mask']:
        for x in [0, length]:
            pcb.add_circle((x, y), r_contact / 2, lay, r_contact)
    pcb.add_text((length/2, y - 2), 'width = {:.2f}mm'.format(w), 'F.SilkS')
    y += 20
pcbnew.Refresh()
```
Go ahead and try this out in the pcbnew terminal. The sky is the limit when it comes to procedural layout.
