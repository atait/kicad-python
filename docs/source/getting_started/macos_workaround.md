# MacOS/v7 Bug Workaround

`pcbnew.py` from KiCAD v7 does not import on MacOS because its Mach-O file uses @executable_path instead of relative linker paths. Everything works fine when inside the GUI, but not outside in headless mode. The workaround for now is to use KiCad's bundled `python3` executable and then give it a short name: `kipython`.

## KiCAD's builtin python
### Symlinking (one time)
Run the usual setup `python -m kigadgets`, it will detect if you need this workaround and take care of it.

What is happening is effectively this
```bash
ln -s "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3" /usr/local/bin/kipython
```
plus checks to make sure those places exist and are writable. It will prompt you before making the symlink in case you want to replace `/usr/local/bin` with somewhere else on your `PATH`. Check that `kipython` symlink is working like this
```bash
$ which kipython
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
```

### External python packages
`kipython` is within KiCad.app, so modifications made will be installed Application-wide. It is the same python used in the GUI by action plugins. `kipython` *does not* see your venv or conda environment packages active in a given Terminal. It does see your shell environment variables, including `$PYTHONPATH`.

Suppose we have a script or module that combines headless pcbnew and some heavier packages
```python
# myscript.py
import kigadgets, pcbnew, numpy, tensorflow

def do_some_pcb_AI():
    ...
```
We typically get dependencies and launch that with
```bash
$ pip install kigadgets numpy tensorflow
$ python myscript.py
```

**On Linux** (and sometimes Windows): this works as expected out of the box.

**On Mac**: you can do this, but it takes an extra step because you are using bundled `kipython` while Linux/Windows can use any python interpreter.

#### App install method
| Caution |
| --- |
| Installing things with `kipython` will get installed in the GUI's environment as well. The packages will not be encapsulated between particular environments, and there is a risk of angering System Integrity Protection. |

The best way is with `--user` flag with bundled `pip`
```bash
$ kipython -m pip install --user numpy tensorflow
```
That's it. It won't corrupt your system or your KiCAD.

I know many install instructions include `--user` for the sake of good practice. Here, it is actually very important to use the `--user` flag. It will install somewhere safe like "~/Library/.../site-packages".

If you forget `--user`, then pip will modify things within KiCad.app/Contents/Frameworks. When you inject new software into an Application package, MacOS gets suspicious and might invalidate KiCad. If you forget --user and then try to install binaries, and everything breaks, then read [KiKit's explanation](https://yaqwsx.github.io/KiKit/latest/installation/macos/) of KiCad code signatures.

#### Explicit installation paths
**Using bundled pip with an external package location**
This is doing the same thing as `--user` except putting it in a custom location. It is useful if you want to create multiple encapsulated pseudo-environments
```bash
$ mkdir -p ~/Documents/KiCad/python3rdparty/site-packages
$ kipython -m pip install --target ~/Documents/KiCad/python3rdparty/site-packages numpy tensorflow
```
Then make sure that is on the `sys.path` that `kipython` will search for imports.
Option 1: call your entry point like this. It does see your shell environment variables, including `$PYTHONPATH`.
```bash
$ export PYTHONPATH="~/Documents/KiCad/python3rdparty/site-packages:$PYTHONPATH"
$ kipython my_script.py
```
Option 2: write your entry point like this.
```python
# myscript.py - edited
import sys
sys.path.insert(0, '~/Documents/KiCad/python3rdparty/site-packages')
import kigadgets, pcbnew, numpy, tensorflow
```

**External package managers**
```bash
$ kipython --version
Python 3.9.13
$ mamba create -n pcbtf python=3.9.13
$ mamba activate pcbtf
(pcbtf) $ pip install tensorflow
(pcbtf) $ pip show tensorflow
...
Location: /Users/username/micromamba/envs/pcbtf/lib/python3.9/site-packages
...
$
```
and then put that Location on `sys.path` using a method above.
```bash
$ export PYTHONPATH="/Users/username/micromamba/envs/pcbtf/lib/python3.9/site-packages:$PYTHONPATH"
$ kipython my_script.py
```
This is not *guaranteed* to work because there are two pips trying to coordinate, yet it almost always does when using the same python version on the same machine.

To skip typing that export line, you can add it as an environment activation hook at: ~/micromamba/envs/pcbtf/etc/conda/activate.d/explicit_pythonpath.sh. Run then looks like
```bash
$ mamba activate pcbtf
(pcbtf) $ kipython my_script.py
```

