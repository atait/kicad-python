# kicad-python: atait fork
Development of a new Python scripting API for KiCad
based on Piers Titus van der Torren work and comunity
feedback to create a less C++ tied API.

## Description
KiCAD and pcbnew expose a python API that allows plugins and other procedural processing of PCB layouts. There are limitations of using this API directly: [its documentation](https://docs.kicad.org/doxygen-python/namespacepcbnew.html) is empty (v7 does not exist yet); it is a clunky SWIG/C-style API with custom datatypes for things like lists; its API changes for every KiCAD version; and it exposes too much functionality on equal footing.

Even if the perfect built-in KiCAD python API came tomorrow, new plugins written on that API would not work in v4-v7, and old plugins would no longer work. Plugins written using `kicad-python` instead are backwards compatible, forwards compatible, and easier to understand for KiCAD newcomers.

This package is a pythonic wrapper around the various `pcbnew` APIs. It implements patterns such as objects, properties, and iterables. It performs more intuitive unit and layer handling. It only exposes functionality most relevant to editing boards, the idea being that native functionality can always be accessed through the wrapped objects if needed.

This package has been fully tested with KiCAD 5, 6, 7 and partially tested with 7.99.

> [!CAUTION]
> The atait fork is undergoing a refactor that will result in new package imports.
> Instances of `from kicad.pcbnew.board import Board` must be replaced by `from kigadgets.board import Board` by version 0.5.0

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
This simple interface is not possible with the C++ SWIG API. The python wrapper is handling things like calling the (sometimes hard to find) function names, sanitizing datatypes, looking up layers, and enabling the generator pattern. 
Don't be fooled though - `track` and `board` contain no state. They use properties to give an intuition of state, but they are dynamically interacting with the underlying C++ `PCB_TRACK` and `BOARD`. You can always access the low-level objects using `track.native_obj`.

## Installation

1. 
```
pip install kigadgets
```

2. Open the pcbnew GUI application. Open its terminal ![](doc/pcbnew_terminal_icon.png) or ![](doc/pcbnew_terminal_icon2.png) and run these commands in kicad 6+
```python
import pcbnew
pcbnew.__file__
# [Path A]: This will give something like "/usr/lib/python3/dist-packages/pcbnew.py"
pcbnew.SETTINGS_MANAGER.GetUserSettingsPath()
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
pcb.add_circle((100, 100), 20, 'F.Silkscreen'); pcbnew.Refresh()
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

## Snippet examples
These snippets are run in the GUI terminal. They are common automations that aren't worth making dedicated action plugins. There is no preceding context; the linking step above provides `pcb` to the terminal. These all should work in pcbnew 5, 6, or 7 on Mac, Windows, or Linux.

### Hide silkscreen labels of selected footprints
```python
for fp in pcb.footprints:
    if fp.is_selected:
        fp.reference_label.visible = False
pcbnew.Refresh()
```
![](doc/simple_script.png)

### Move all silk labels to fab layers
Instead, we can keep them on Fab layers so we can still see them while designing the PCB.
```python
for m in pcb.modules:
    ref = m.reference_label
    if ref.layer == 'F.Silkscreen':
        ref.layer = 'F.Fab'
    elif ref.layer == 'B.Silkscreen':
        ref.layer = 'B.Fab'
pcbnew.Refresh()
```

### Select similar vias
This snippet assumes you have selected one via
```python
og_via = next(pcb.selected_items)
for via2 in pcb.vias:
    if via2.diameter != og_via.diameter: continue
    if via2.drill != og_via.drill: continue
    via2.select()
og_via.select(False)
pcbnew.Refresh()
```
The function `next` is used because `pcb.items` is a generator, not a list. Turn it into a list using the `list` function if desired. 

See `via.py` for additional functionality related to micro and blind vias.

### Change all drill diameters
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
    pcb.add_line(t.start, t.end, 'F.SilkS' if t.layer == 'F.Cu' else 'B.SilkS', new_width)
pcbnew.Refresh()
```

### Select everything schematically connected to this footprint
```python
fp = next(pcb.selected_items)
nets = {pad.net_name for pad in fp.pads}
nets -= {'GND', '+5V'}  # because these are connected to everything
for mod in pcb.footprints:
    if any(pad.net_name in nets for pad in mod.pads):
        mod.select()
```

### Import user library for GUI/CLI
Suppose you wrote a file located in $KICAD_SCRIPTING_DIR/my_lib.py
```python
# ~/.config/kicad/scripting/my_lib.py (Linux)
# ~/Library/Preferences/kicad/scripting/my_lib.py (MacOS)
from kicad.pcbnew.board import Board

def do_something(pcb):
    ...

if __name__ == '__main__':
    pcb = Board.load(sys.argv[1])
    do_something(pcb)
    pcb.save()
```
Then you can run it in the pcbnew.app terminal like
```python
from my_lib import do_something
do_something(pcb)
pcbnew.Refresh()
```
or from the command line like
```bash
python my_lib.py some_file.kicad_pcb
```

### Keep track of live editor state
```python
from kicad.pcbnew.drawing import Rectangle
my_rect = Rectangle((0,0), (60, 40))
pcb.add(my_rect)
pcbnew.Refresh()
print(my_rect.x, my_rect.contains((1,1)))  # 30 True
# Go move the new rectangle in the editor
print(my_rect.x, my_rect.contains((1,1)))  # 15.2 False
```
`kicad-python` stays synchronized with the state of the underlying native objects even when they are modified elsewhere because it is wrapping the C++ state rather than holding a Python state.

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
Go ahead and try this out in the pcbnew terminal, although this type of thing is better to stick in a user library (see above). The sky is the limit when it comes to procedural layout!

## Related packages
KiCAD has a rich landscape of user-developed tools, libraries, and plugins. They have complementary approaches that are optimized for different use cases. It is worth understanding this landscape in order to use the right tool for the job. This is how `kicad-python` fits in.

### KiKit
[KiKit](https://github.com/yaqwsx/KiKit) has powerful user-side functionality for panelization, exporting, and other common fabrication tasks. Like `kicad-python`, `KiKit` has applications spanning GUI and batch environments; they create cross-version compatibility by modifying SWIG API; they expose libraries usable in other plugin development. Some differences are summarized here

|                   | KiKit        | kicad-python                 |
| ----------------- | ------------ | ---------------------------- |
| Primary audience  | users        | developers                   |
| CAD logic/state   | python       | C++                          |
| Entry points      | Plugin, CLI  | API                          |
| Dependencies      | 8            | 0                            |
| Lines to maintain | 15k          | 3k                           |
| Python versions   | 3.7+         | 2.\*/3.\*                    |
| Documentation     | extensive    | "documents itself" for now   |

**Audiences:** While `KiKit` is directed primarily to end users, `kicad-python` is directed moreso to developers and coders. It is lean: <2,800 lines of code, no constraints on python version, and **zero dependencies** besides `pcbnew.py`. Out of the box, `kicad-python` offers very little to the end user who doesn't want to code. It has no entry points, meaning the user must do some coding to write 10-line snippets, action plugins, and/or batch entry points. In contrast, `KiKit` comes with batteries included. It exposes highly-configurable, advanced functionality through friendly entry points in CLI and GUI action plugins.

**Internals:** `KiKit` performs a significant amount of internal state handling and CAD logic (via `shapely`). `kicad-python` does not store state; it is a thin wrapper around corresponding SWIG objects. While the first approach gives functionality beyond `pcbnew` built into KiKit, the second exposes the key functionality of underlying objects, leaving the state and logic to C++. It requires a coder to do things with those objects. If that dev wants to use `shapely` too, they are welcome to import it.

> [!TIP]
> If you don't view yourself as a coder, you can become one! Have a look at the snippets above - do you understand what they are doing? If so, you can code. 
> While you are [learning python syntax](https://docs.python.org/3/tutorial/index.html), you can just copy the examples above and modify to suit your needs. 

#### pcbnewTransition
KiKit is based on [pcbnewTransition](https://github.com/yaqwsx/pcbnewTransition) to provide cross-version compatibility. This package unifies the APIs of v5-v7 `pcbnew` into the v7 API. Something similar is happening in `kicad/__init__.py` with a sylistic difference that `kicad-python` unifies under a wrapping API instead of patching the `pcbnew` API. One nice feature of a wrapper-style API is that the contract for cross-version compatibility ends at a clearly-defined place: the `native_obj` property.

### pykicad
[pykicad](https://github.com/dvc94ch/pykicad) and various other packages use an approach of parsing ".kicad_pcb" files directly, without involvement of the KiCad's `pcbnew.py` library. In contrast, `kicad-python` wraps that SWIG library provided by KiCAD devs. Both packages work for batch processing. While `kicad-python` exposes all `pcbnew.py` state and functions, `pykicad` does not even require an installation of KiCAD, which is advantageous in certain use cases.

### The kicad-pythons
This project forks KiCAD/kicad-python and maintains its complete history. The original repo has been archived. The pointhi/kicad-python repo (tied to `pip install kicad-python`) was inspired by the 2016 version of KiCAD/kicad-python but is not maintained beyond KiCAD v4.

### lygadgets
This project adopts a philosophy similar to that of [lygadgets](https://github.com/atait/klayout-gadgets), except for PCBs instead of integrated circuits. Both attempt to harmonize between a GUI application and external python environments. Neither uses `subprocess` because who knows where that will get interpreted. Both are simple and lean with zero dependencies.

The overarching idea is workflow *interoperability* rather than uniformity. I think this works better for open source because everybody has their existing workflows, and there is no central authority to impose "the best" API or - more generally - to tell you how to do your thing. 

An example of interoperability, `kicad-python` can be lightly inserted anywhere in existing code using `wrap` and `native_obj`.
```python
# legacy_script.py
...
my_zone = get_a_zone_somewhere()
# my_zone.SetClearance(my_zone.GetClearance() * 2)  # This existing line will not work >v5
### begin insertion
from kicad.pcbnew.zone import Zone
zone_tmp = Zone.wrap(my_zone)
zone_tmp.clearance *= 2  # Works in all versions
my_zone = zone_tmp.native_obj
### end insertion
do_something_else_to(my_zone)
```
Now this code is forwards compatible without breaking backwards compatibility.
