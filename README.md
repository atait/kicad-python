# kicad-python
Development of a new Python scripting API for KiCad
based on Piers Titus van der Torren work and comunity
feedback to create a less C++ tied API.

A second intention of this new API is also to provide
better documentation via sphinx.

### Warning

This library is under development and requires a fairly recent (daily)
build of KiCad. It may not work with stable versions.

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
This simple interface is not possible with the SWIG API. The wrapper is handling things like calling the (sometimes hard to find) function names, sanitizing datatypes, looking up layers, and enabling the generator pattern. From the `Track` class:
```python
class Track(HasConnection, object)
    ...
    @property
    def layer(self):
        brd = self._obj.GetBoard()
        return brd.GetLayerName(self._obj.GetLayer())
```

### pykicad
[pykicad](https://github.com/dvc94ch/pykicad) is an excellent package written by David Craven. It is complementary to this one. `kicad-python` wraps the SWIG library provided by KiCAD devs, while `pykicad` works independently by implementing its own parser of ".kicad_pcb" files. This means that `pykicad` is fully transparent, while `kicad-python` is not, but it works within the pcbnew GUI with abilities to refresh and move the view window.

## Installation

### Automatic version

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
import pcbnew
print('link_kicad_python_to_pcbnew', pcbnew.__file__, pcbnew.GetKicadConfigPath())
```
which will give you something like this
```
link_kicad_python_to_pcbnew /usr/lib/python3/dist-packages/pcbnew.py /home/username/.config/kicad
```
Copy that *entire* last line.

3. From any command line interpreter, paste that thing and run it.

\[**fallback**\] If that fails because you don't have file permissions or something, you can instead set the environment variable "PCBNEW_PATH" to the first path that comes out of that command. Put this line in your .bashrc or .zshrc
```bash
export PCBNEW_PATH=/usr/lib/...
```

4. Try it out! Quit and reopen pcbnew application. Open its terminal, then run
```python
pcb.add_circle((100, 100), 20, 'F.SilkS'); pcbnew.Refresh()
```

#### What is `link_kicad_python_to_pcbnew`?
This command creates a bidirectional link, telling `kicad` (this package) and `pcbnew` (their builtin GUI-based package) where to find each other. First, it writes a pcbnew plugin that runs automatically when the application starts. It looks like this
```python
import sys
sys.path.append("/path/to/your/kicad-python/")
from kicad.pcbnew.board import Board
pcb = Board.from_editor()
```
The plugin *must* go in /home/myself/.config/kicad/scripting/plugins (depending on your system), and you have to tell it where that is in step #2.

This first step is crucial for using kicad-python in the pcbnew application and action plugins.

Then, it creates a link from your non-GUI python interpreter. This is stored in a file called `.path_to_pcbnew_module`, which is located in the package installation. Since it is a file, it persists after the first time. You can override this in an environment variable. Again, you have to give it some help to find it the first time in step #2.

This second step is crucial for using kicad-python outside of the pcbnew application: batch processing, cloud computers, or any other applications (like FreeCAD!)

## Examples

### Hide all silkscreen labels
```python
for m in pcb.modules:
    m.referenceLabel.visible = False
pcbnew.Refresh()
```

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
