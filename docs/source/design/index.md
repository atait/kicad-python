# Design Rationale

```{toctree}
:titlesonly:
related_projects
why_lists
linker_underthehood
```

The `kicad-python` project is more than 10 years old. Each generation introduced principles still followed by `kigadgets`. 

Initially it was a [single module](https://github.com/pierstitus/kicad-python), credit to [@pierstitus](https://github.com/pierstitus). It was soon refactored into a package `kicad` with good encapsulation and the ability to install with pip -e. The concept of wrapper classes was introduced, thanks primarily to [@mangelajo](https://github.com/mangelajo). These could be initialized in `kicad` and added to boards, but any querying or mutation of existing items required the user to wander through SWIG API.

The next step was the ability to query and mutate native objects in SWIG through `kicad.pcbnew` wrapper objects. You could modify the board in the GUI from terminal and see the changes live. The user might not need to interact with SWIG at all, thanks to [@hyOzd](https://github.com/hyOzd).

Around the release of KiCAD v6, development began on cross-version compatibility. GUI/plugin integrations advanced including Ctrl-Z, selection, highlighting, and notify. Wrapper API expanded to include Text, Polygon, and Zone. The introduction of `environment.py` allowed `kicad` to be used outside of the GUI and simplified how it could be used in action plugins and GUI terminal, thanks to [@atait](https://github.com/atait).

`kigadgets` is the fourth generation of `kicad-python`. 
The name change reflects refactoring that is not backwards-compatible with the legacy packaging. 
It's primary goal is modernizing development aspects (test, documentation, packaging, zero dependencies, examples, and PyPI deployment). These changes were modeled after [`lygadgets`](https://github.com/atait/klayout-gadgets).
`kigadgets` added and/or altered string-based layer handling, shape manipulation for Polygon/Zone/Keepout, and replacement of generators with lists. 
> One of the most significant additions is `geohash`, which turns any `Board` or `BoardItem` into an integer. Any pair of boards that are logically different produce different hashes; any that are logically equivalent produce the same, even when their files are (usually) substantially different.
> `geohash` enables testing of geometric behavior, as opposed to just tests of import/run. When combined with [`lytest`](https://github.com/atait/lytest), all of this testing is now automated and ready for Continuous Integration.
