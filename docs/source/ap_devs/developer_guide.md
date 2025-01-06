# Software developer examples
## Multiple entry point pattern
Scripts based on `kigadgets` can have multiple entry points between headless and GUI. If you are working on a headless program, develop it in the GUI first, then use the same code; if you are maintaining a GUI action plugin, run it headless as part of a testing framework to ensure repeatable behavior.

Suppose you wrote a file located in $KICAD_SCRIPTING_DIR/my_lib.py and want to run it in batch mode or GUI mode without needing to change it.
```python
# ~/.config/kicad/scripting/my_lib.py (Linux)
# ~/Library/Preferences/kicad/scripting/my_lib.py (MacOS)
from kigadgets.board import Board

def do_something(pcb):
    ...

if __name__ == '__main__':
    pcb = Board.load(sys.argv[1])
    do_something(pcb)
    newname = os.path.splitext(pcb.filename)[0] + '-proc.kicad_pcb'  # Prevent overwrite of source file
    pcb.save(newname)
```

(GUI terminal entry point) You can run it in the pcbnew.app terminal
```python
from my_lib import do_something
do_something(pcb)
pcbnew.Refresh()
```
(headless CLI entry point) from the command line like
```bash
python my_lib.py some_file.kicad_pcb
```
(API entry point) `my_lib` can be imported by any other action plugins *or* any external python interpreter (as long as it is discoverable on `sys.path`).

Even for a GUI-only application, having headless entry points is useful for automated testing for repeatable behavior.

## Regression testing with `geohash`
kigadgets `Board` and `BoardItem`s implement `geohash`, which returns a hash value that depends on every item in the PCB. It provides a fast and well-defined way to detect whether two boards are logically equivalent or not. This is difficult because a) different .kicad_pcb files can correspond to logically identical PCBs, and b) different `pcbnew` object states can be logically equivalent, such as with track orientation:

```python
pcb1 = Board()
pcb1.add_track([(1, 1), (1, 2)])
pcb2 = Board()
pcb2.add_track([(1, 2), (1, 1)])
assert pcb1.geohash() == pcb2.geohash()  # Succeeds
```

Geometry hashing enables layout regression testing, git-diff, CI, and behavioral verification. We want to know that `kigadgets` is importing *and also* that it is producing correct behavior. Ok, "correct" is subjective. What we can do is ensure that behavior is logically unchanged when there are other changes: user code, kigadgets code, pcbnew.so, KiCad version, operating system, kicad_pcb encoding, dependency updates, and so on.

Utilities specific to automated regression testing are provided by [`lytest`](https://github.com/atait/lytest). See tests in the kigadgets repository for examples.

Note, for security reasons, `geohash` uses a random seed that changes when python is invoked. It is not repeatable between interpreter sessions. That means:
- do not store the geohash value for reference; instead store the .kicad_pcb for reference. When loaded, it will get the seed corresponding to this session.
- `geohash` should not be used for autenthification checksums; instead use md5 on the file itself

## Updating existing plugins
Maintaining different branches/releases for different KiCad versions, then deploying via PCM, is the accepted method. It requires developer dedication that would be remarkable for a hardware designer. The cross-version compatibility of `kigadgets` can help with this problem.

If you want to make an existing piece of pcbnew code version-independent, you can delicately insert kigadgets anywhere in existing code using `wrap` and `native_obj`.

```python
# file: legacy_script.py
...
my_zone = get_a_zone_somewhere()
my_zone.SetClearance(my_zone.GetClearance() * 2)
# The above line will not work >v5
do_something_else_to(my_zone)
```
Modify that code like this:
```python
...
my_zone = get_a_zone_somewhere()

### Begin insertion
from kigadgets.zone import Zone
zone_tmp = Zone.wrap(my_zone)  # Intake from any version
zone_tmp.clearance *= 2        # Version independent
my_zone = zone_tmp.native_obj  # Outlet to correct version
### end insertion

do_something_else_to(my_zone)
```
Now this code is forwards compatible without breaking backwards compatibility.
