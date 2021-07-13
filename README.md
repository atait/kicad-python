# kicad-python
Development of a new Python scripting API for KiCad
based on Piers Titus van der Torren work and comunity
feedback to create a less C++ tied API.

A second intention of this new API is also to provide
better documentation via sphinx.

### Warning

This library and kicad API itself are under development. It has been tested for pcbnew plugins and shell with python 2 and 3. Standalone processing requires a python 3 build of kicad, which is currently only released for Linux. This has not been tested with kicad v6, although it should adapt to the v6 programming framework without modification, to the extent that v6 is backwards compatible.

## Description
KiCAD and `pcbnew` expose a python API that allows plugins and other procedural processing of PCB layouts. There are limitations of using this API directly: [its documentation](https://docs.kicad.org/doxygen-python/namespacepcbnew.html) is empty and outdated; it is a clunky SWIG/C-style API with custom datatypes for things like lists; and it exposes too much functionality on equal footing.

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

2. Open the pcbnew application. Open its terminal ![](doc/pcbnew_terminal_icon.png) and run
```python
import pcbnew; print('link_kicad_python_to_pcbnew ' + pcbnew.__file__ + ' ' + pcbnew.GetKicadConfigPath())
```
which will give you something like this
```
link_kicad_python_to_pcbnew /usr/lib/python3/dist-packages/pcbnew.py /home/username/.config/kicad
```
Copy that *entire* last line.

3. From any command line shell, paste that thing and run it.

\[**fallback**\] If that fails because you don't have file permissions or something, you can instead set the environment variable "PCBNEW_PATH" to the first path that comes out of that command. Put this line in your .bashrc or .zshrc
```bash
export PCBNEW_PATH=/usr/lib/python3/dist-packages/pcbnew.py
```

4. Try it out! Quit and reopen pcbnew application. Open its terminal, then run
```python
pcb.add_circle((100, 100), 20, 'F.SilkS'); pcbnew.Refresh()
```

#### What is `link_kicad_python_to_pcbnew`?
This command creates a bidirectional link, telling `kicad` (this package) and `pcbnew` (their builtin C++ wrapper) where to find each other. 

First, it writes a script for the pcbnew application shell. This first step is crucial for using kicad-python for on-the-fly macros and plugin development. It runs automatically when the shell opens. It looks like this
```python
import sys
sys.path.append("/path/to/your/kicad-python/")
from kicad.pcbnew.board import Board
pcb = Board.from_editor()  # pcb is now a global variable
```
The script *must* go in /home/myself/.config/kicad/PyShell_pcbnew_startup.py (depending on your system).

Second, it exposes kicad-python to the pcbnew action plugin environment. This is a script that goes in the "scripting/plugins" directory and is imported automatically when the application opens. It is crucial in order to use kicad-python in your action plugins.

Third, it exposes `pcbnew` to this pythonic package. This is crucial for using kicad-python outside of the pcbnew application: batch processing, cloud computers, or any other applications (like FreeCAD!)

The path is stored in a file called `.path_to_pcbnew_module`, which is located in the package installation. Since it is a file, it persists after the first time. You can override this in an environment variable `PCBNEW_PATH`.

### pykicad
[pykicad](https://github.com/dvc94ch/pykicad) is an excellent package written by David Craven. It is complementary to this one. `kicad-python` wraps the SWIG library provided by KiCAD devs, while `pykicad` works independently by implementing its own parser of ".kicad_pcb" files. This means that `pykicad` is pure python, while `kicad-python` is not. It also means that `kicad-python` can work within the pcbnew GUI with abilities to refresh and move the view window. Both work for batch processing. 

Because it wraps the official kicad API, `kicad-python` can also adapt to file format updates - this version works with any python3 version of kicad.


## Examples
These all can be run in the pcbnew application console on Mac/Windows/Linux and python 2/3.

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
Go ahead and try this out in the pcbnew console. The sky is the limit when it comes to procedural layout.
