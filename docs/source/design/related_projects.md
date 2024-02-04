# Related Projects
KiCAD has a rich landscape of user-developed tools, libraries, and plugins. They have complementary approaches that are optimized for different use cases. It is worth understanding this landscape in order to use the right tool for the job, whether it turns out to be `kigadgets`, others, or multiple.

## KiKit
[KiKit](https://github.com/yaqwsx/KiKit) has powerful user-side functionality for panelization, exporting, and other common fabrication tasks. Like `kigadgets`, `KiKit` has applications spanning GUI and batch environments; they create cross-version compatibility by modifying SWIG API; they expose libraries usable in other plugin development. Some differences are summarized here

|                   | `KiKit`      | `kigadgets`                  |
| ----------------- | ------------ | ---------------------------- |
| Primary audience  | users        | developers                   |
| CAD state + logic | python       | C++                          |
| Entry points      | Plugin + CLI | API (available to plugins + CLI scripts)       |
| Dependencies      | 8            | 0                            |
| Lines of code     | 15k          | 3k                           |
| Python versions   | 3.7+         | 2.\*/3.\*                             |
| Documentation     | extensive    | "documents itself" for now                          |

**Audiences:** While `KiKit` is directed primarily to end users, `kigadgets` is directed moreso to developers and coders. It is lean: <2,800 lines of code, no constraints on python version, and **zero dependencies** besides `pcbnew.py`. Out of the box, `kigadgets` offers very little to the end user who doesn't want to code. It has no entry points, meaning the user must do some coding to write 10-line snippets, action plugins, and/or batch entry points. In contrast, `KiKit` comes with batteries included. It exposes highly-configurable, advanced functionality through friendly entry points in CLI and GUI action plugins.

**Internals:** `KiKit` performs a significant amount of internal state handling and CAD logic (via `shapely`). `kigadgets` does not store state; it is a thin wrapper around corresponding SWIG objects. While the first approach gives built-in functionality beyond `pcbnew`, the second exposes the key functionality of underlying objects, leaving the state and logic to C++. It requires a coder to do things with those objects. If that dev wants to use `shapely` too, they are welcome to import it.

### pcbnewTransition
KiKit is based on [pcbnewTransition](https://github.com/yaqwsx/pcbnewTransition) to provide cross-version compatibility. This package unifies the APIs of v5-v7 `pcbnew` into the v7 API. Something similar is happening in `kigadgets/__init__.py` with a stylistic difference that `kigadgets` unifies under a wrapping API instead of patching the `pcbnew` API. One nice feature of a wrapper-style API is that the contract for cross-version compatibility ends at a clearly-defined place: the `native_obj` property.

## pykicad
[pykicad](https://github.com/dvc94ch/pykicad) and various other packages use an approach of parsing ".kicad_pcb" files directly, without involvement of the KiCad's `pcbnew.py` library. In contrast, `kigadgets` wraps that SWIG library provided by KiCAD devs. Both packages work for batch processing. While `kigadgets` exposes all `pcbnew.py` state and functions, `pykicad` does not even require an installation of KiCAD, which is advantageous in certain use cases.

## The kicad-pythons
This project forks KiCAD/kicad-python and maintains its complete history. The original repo has been archived. The pointhi/kicad-python repo (tied to `pip install kicad-python`) was inspired by the 2016 version of KiCAD/kicad-python but is not maintained beyond KiCAD v4.

## lygadgets
This project adopts a philosophy similar to that of [`lygadgets`](https://github.com/atait/klayout-gadgets), except for PCBs instead of integrated circuits. Both attempt to harmonize between a GUI application and external python environments. Neither uses `subprocess` because who knows where that will get interpreted. Both are simple and lean with zero dependencies.

The overarching idea is workflow *interoperability* rather than uniformity. I think this works better for open source because everybody has their existing workflows, and there is no central authority to impose "the best" API or - more generally - to tell you how to do your thing. 

An example of interoperability, `kigadgets` can be delicately inserted anywhere in existing code using `wrap` and `native_obj`.
```python
# file: legacy_script.py
...
my_zone = get_a_zone_somewhere()
# my_zone.SetClearance(my_zone.GetClearance() * 2)  # This existing line will not work >v5

### begin insertion
from kigadgets.zone import Zone
zone_tmp = Zone.wrap(my_zone)  # Intake from any version
zone_tmp.clearance *= 2        # Version independent
my_zone = zone_tmp.native_obj  # Outlet to correct version
### end insertion

do_something_else_to(my_zone)
```
Now this code is forwards compatible without breaking backwards compatibility.
