# Design Rationale

```{toctree}
:titlesonly:
linker_underthehood
related_projects
why_lists
```

## History
The `kicad-python` project is more than 10 years old. Each generation introduced principles still followed by `kigadgets`.

Initially it was a [single module](https://github.com/pierstitus/kicad-python), credit to [@pierstitus](https://github.com/pierstitus). It was soon refactored into a package `kicad` with good encapsulation and the ability to install with pip -e. The concept of wrapper classes was introduced, thanks primarily to [@mangelajo](https://github.com/mangelajo). These could be initialized in `kicad` and added to boards, but any querying or mutation of existing items required the user to wander through SWIG API.

The next step was the ability to query and mutate native objects in SWIG through `kicad.pcbnew` wrapper objects. You could modify the board in the GUI from terminal and see the changes live. The user might not need to interact with SWIG at all, thanks to [@hyOzd](https://github.com/hyOzd).

Around the release of KiCad v6, development began on cross-version compatibility. GUI/plugin integrations advanced including Ctrl-Z, selection, highlighting, and notify. Wrapper API expanded to include Text, Polygon, and Zone. The introduction of `environment.py` allowed `kicad` to be used outside of the GUI and simplified how it could be used in action plugins and GUI terminal, thanks to [@atait](https://github.com/atait).

## kigadgets 5.0
`kigadgets` is the fourth generation of `kicad-python`.
The name change reflects refactoring that is not backwards-compatible with the legacy packaging.
It's primary goal is modernizing development aspects (test, documentation, packaging, zero dependencies, examples, and PyPI deployment). These changes were modeled after [`lygadgets`](https://github.com/atait/klayout-gadgets).
`kigadgets` added and/or altered string-based layer handling, shape manipulation for Polygon/Zone/Keepout, and replacement of generators with lists.

> One significant addition is `geohash`, which turns any `Board` or `BoardItem` into an integer. Any pair of boards that are logically different produce different hashes; any that are logically equivalent produce the same, even when their files are (usually) substantially different.

## KiCad 9.0 and IPC API
KiCad 9 will introduce a python API based on inter-process communication (IPC) between an external python executable and an open pcbnew application. There are pros/cons to the IPC approach vs. the child process approach used here. Here, an external process launches a new process that has the `pcbnew` module available. This allows for scripts that work the same within and outside GUI, concurrent/multiprocess scripting, python environment customization, processing over SSH, and so on. `kigadgets` attempts to provide a stable API to `pcbnew` SWIG.

Later versions of `kigadgets` might use the IPC API as a backend but will maintain its frontend API throughout the 8->9->10 transition.