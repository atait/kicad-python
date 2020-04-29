# kicad-python
Development of a new Python scripting API for KiCad
based on Piers Titus van der Torren work and comunity
feedback to create a less C++ tied API.

A second intention of this new API is also to provide
better documentation via sphinx.

## Warning

This library is under development and requires a fairly recent (daily)
build of KiCad. It may not work with stable versions.

## How to Use

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
