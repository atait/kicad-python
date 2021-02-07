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

## How to Use

### Quick start

1. Clone this repository to any location

2. Add these lines to kicad python shell startup file
   (PyShell_pcbnew_startup.py) with correct path to 'kicad-python'

```
import sys
sys.path.append("/path/to/kicad-python/")
from kicad.pcbnew.board import Board

board = Board.from_editor()
```

3. Launch the python shell from kicad and access the board components
   via the global object `board`.

### From outside of pcbnew GUI
The SWIG bindings are exposed in the file `pcbnew.py`, which is installed with KiCAD. The problem is that nobody knows where it is, especially not your python installation. To find it, open the pcbnew application. Open its terminal and run
```python
>>> import pcbnew
>>> print(pcbnew.__file__)
/usr/lib/python3/pcbnew.py  # for example
```
For `kicad-python` to find it, set the environment variable
```bash
export PCBNEW_PATH=/usr/lib/python3/pcbnew.py
```
according to the output of the prior command. Put this line in your .bashrc or .zshrc or conda using these commands
```bash
conda create -n pcb-development  # you might have done this already
conda activate pcb-development

mkdir -p ${CONDA_PREFIX}/etc/conda/activate.d
echo "export PCBNEW_PATH=/usr/lib/python3/pcbnew.py" > ${CONDA_PREFIX}/etc/conda/activate.d/find_pcbnew.sh
```

Finally, make `kicad-python` visible system-wide with
```bash
cd /path/to/kicad-python
pip install .
```
