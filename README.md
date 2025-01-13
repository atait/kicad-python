# kigadgets
**a.k.a. kicad-python: atait fork**
Development of a stable Python scripting API for KiCad based on Piers Titus van der Torren work and community feedback.

[Documentation](https://kigadgets.readthedocs.io)

<img src="docs/source/media/kiga-dark-1024.png" width="40%" margin="auto">

KiCad and pcbnew expose a python interface that allows plugins and other procedural processing of PCB layouts. While it is a major differentiator of KiCad, there are limitations of using this python API directly. `kigadgets` attempts to simplify the software design to a level where hardware designers are able to write (and maintain) their own code for software-assisted layout.

`kigadgets` implements cross-version compatible and more intuitive patterns for objects, properties, units, string layers, and so on.
It constructs an environment where `pcbnew.py` functionality can be used headless (outside the GUI), and the pcbnew GUI can import external python packages at runtime.
Furthermore, it enables patterns for more advanced software engineering such as multiple entry points, layout hashes, and regression tests.

This package has been fully tested with KiCad 5.0 through KiCad 9.0 (Mac/Windows/Linux).

See `tests` to reproduce headless behavior and `examples` to reproduce GUI behavior. Note that v9 will give warnings about SWIG.

### An excerpt
A simple pythonic script might look like this
```python
print([track.layer for track in pcb.tracks])
print([track.width for track in pcb.tracks if track.is_selected])
```
which produces
```
[F.Cu, B.Cu, B.Cu]
[0.8, 0.6]
```
The python wrapper is handling things like calling the (sometimes hard to find) function names, sanitizing datatypes, looking up layers, and enabling the list comprehension.

`track` and `board` use properties to give an intuition of state, but they are dynamically interacting with the underlying C++ `PCB_TRACK` and `BOARD` that you see in the layout editor.

> [!CAUTION]
> **MacOS Users:**
> pcbnew.py from KiCAD v7 does not import due to something in the linking process to pcbnew.so. Everything works fine when inside the GUI. Outside the GUI, the workaround is to use the `python` that comes bundled with KiCAD. I recommend aliasing/symlinking it. Bonus points for encapsulating in a conda environment.
>
```bash
(base) $ kipython_path="/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
(base) $ conda_envbin_path="~/miniconda3/envs/ki/bin/kipython"
(base) $ ln -s $kipython_path $conda_envbin_path
```
> Replacing "miniconda3" with your conda (or mamba) root; replacing "ki" with the name of desired environment.
> You will need to reinstall all needed packages using kicad's pip like this
```bash
(base) $ conda activate ki
(ki) $ kipython -m pip install kigadgets ...
```
> Now you can run tests with
```bash
kipython -m pip install tests/requirements.txt
kipython -m pip install -e .
kipython -m pytest tests
```
> Double caution: installing things with `kipython` will get installed in the GUI's environment as well. The packages will not be encapsulated between particular conda environments.
> That is potentially bad but can be purged by reinstalling KiCAD.

<!-- ## Installation via package manager
**IN PROGRESS**

v6+ only

1. Open kicad menu Tools > Plugin and Content Manager.
2. Scroll down to `kigadgets`
3. Double click. Apply transaction.
4. You are done
 -->


## Installation via PyPI
```bash
pip install kigadgets
python -m kigadgets
```

The `python -m kigadgets` command automatically links paths needed for headless scripts to import the `pcbnew` module and for GUI plugins to find python packages external to KiCad, including `kigadgets`. For more detail on what the linker is doing, why, and advanced options, see [here](../design/linker_underthehood).

> **Mac users:** There is an extra step. The above command will walk you through it. For more information about [kipython on Mac](./macos_workaround), see the docs.

Try it out: Quit and reopen pcbnew application. Open its terminal, then run
```python
pcb.add_circle((100, 100), 20, 'F.Silkscreen'); pcbnew.Refresh()
```

## Snippet examples
These snippets are run in the GUI terminal. There is no preceding context; the linking step above provides `pcb` to the terminal. [More examples in the docs](kigadgets.readthedocs.io/getting_started/snippet_examples.html).

### Hide silkscreen labels of selected footprints
```python
for fp in pcb.footprints:
    if fp.is_selected:
        fp.reference_label.visible = False
pcbnew.Refresh()
```
![](doc/simple_script.png)

### Change all drill diameters
Because planning ahead doesn't always work
```python
for v in pcb.vias:
    if v.drill > 0.4 and v.drill < 0.6:
        v.drill = 0.5
pcbnew.Refresh()
```

### Select everything schematically connected to this footprint
```python
footprint = pcb.selected_items[0]
nets = {pad.net_name for pad in footprint.pads}
nets -= {'GND', '+5V'}  # because these are connected to everything
for mod in pcb.footprints:
    if any(pad.net_name in nets for pad in mod.pads):
        mod.select()
```

### User input via layout
```python
from kigadgets.drawing import Rectangle
my_rect = Rectangle((0,0), (60, 40))
pcb.add(my_rect)
pcbnew.Refresh()
print(my_rect.x, my_rect.contains((1,1)))  # 30 True
input('Go move that rectangle. When done, refocus in this terminal and press enter.')
# Go move the new rectangle in the editor
print(my_rect.x, my_rect.contains((1,1)))  # 15.2 False
pcb.remove(my_rect)
pcbnew.Refresh()
```

## Stodgier features
While helpful for small scripting (above), `kigadgets` also provides significant support for maintaining more complicated codebases that use `pcbnew.py`. It can give cross-version compatibility, code that reads better, and multiple CLI/API/GUI entry points.
All `kigadgets.BoardItem`s are hashable based on their geometric contents.

Together with [`lytest`](https://github.com/atait/lytest), these enable automated testing and things like diff --stat, ultimately giving more workflow options for developing action plugins and batch processing scripts.

TODO verify this link:
[See discussion on software engineering features in the docs.](kigadgets.readthedocs.io/ap_devs/developer_guide.html)

## Related Projects
KiCad has a rich landscape of user-developed tools, libraries, and plugins. It is worth understanding this landscape in order to use the right tool for the job, whether it turns out to be `kigadgets`, others, or multiple.
See discussion of the landscape in [the documentation](kigadgets.readthedocs.io/design/related_projects.html).
