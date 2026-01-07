# Using KiCad’s Python (“kipython”) for headless pcbnew

`pcbnew.py` from KiCad v7+ does not import reliably when running Python from a Terminal (outside the KiCad GUI). Everything works fine when inside the GUI, but not outside in this “headless” mode.

The workaround is to use KiCad's bundled `python3` executable and give it a short name on your `PATH`. We will call it `kipython`.

## When do I need this?
If you want to use `pcbnew.py` for scripting *independent of a GUI Application* and you are using MacOS or Windows, you will need this workaround step. Linux does not need it.

## Quick start

1. Run the setup:
   ```bash
   python -m kigadgets
   ```
2. Verify `kipython` works:
   ```bash
   kipython -c "import pcbnew; print('pcbnew import OK')"
   ```
3. If you need third-party packages for your script, install them for `kipython`:
   ```bash
   kipython -m pip install --user numpy
   ```

## Detailed Setup


### macOS: symlink (one time)
Run the usual setup script `python -m kigadgets`. It will detect if you need this workaround and guide you through it.

On macOS, it is effectively running this command:
```bash
ln -s "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3" /usr/local/bin/kipython
```
plus checks to make sure those places exist and are writable. It will prompt you before making the symlink in case you want to replace `/usr/local/bin` with somewhere else on your `PATH`. Check that `kipython` symlink is working like this
```bash
$ which kipython
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
```

### Windows: PowerShell function / alias
Run the usual setup script `python -m kigadgets`. It will detect if you need this workaround and guide you through it.

On Windows, automatic symlinking is disabled. The `python -m kigadgets` setup will *print* a PowerShell alias command for you that looks like:

```powershell
function kipython { & 'C:\\Program Files\\KiCad\\8.0\\bin\\python.exe' @args }
```

It is up to you how to make this alias persistent. Put it in your PowerShell profile (see `$PROFILE`). Or, if you use a different shell, create the equivalent alias/function for that shell.

## Verify

Basic import test. Run this in any terminal:

```bash
$ kipython -c "import pcbnew; print('pcbnew import OK')"
```

For more verification about the interpreter:

```bash
$ kipython --version
$ kipython -c "import sys; print('Executable:', sys.executable)"
$ kipython -m kigadgets
```

## Using third-party packages with `kipython`

`kipython` is within KiCad.app, so modifications made will be installed Application-wide. It is the same python used in the GUI by action plugins. `kipython` *does not* see your venv or conda environment packages active in a given Terminal. It does see your shell environment variables, including `$PYTHONPATH`.

| Caution |
| --- |
| Installing things with `kipython` will get installed in the GUI's environment as well. Read this section before installing third-party python packages. |

Suppose we have a script or module that combines headless pcbnew and some heavier packages
```python
# myscript.py
import kigadgets, pcbnew, numpy, tensorflow

def do_some_pcb_AI():
    ...
```

Typically, we get dependencies and launch that like this:
```bash
$ python -m pip install numpy tensorflow
$ python myscript.py
```

**On Linux**: this works as expected out of the box in any terminal with any compatible python interpreter.

**On macOS and Windows**: you need to use bundled `kipython` for both execution and installation, and you need to install in such a way to not pollute the KiCAD environment unintentionally.

### Don't do this
```bash
$ kipython -m pip install numpy tensorflow
$ kipython myscript.py
```

This will ususally run; however, `kipython -m pip` will install packages directly into the KiCad application bundle. The change is seen Application-wide, and this can cause code signature issues on macOS. You can break the entire KiCAD application this way.

### Recommended: install with `--user`

The simple solution is with `--user` flag with KiCAD-bundled `pip`
```bash
$ kipython -m pip install --user numpy tensorflow
$ kipython myscript.py
```
That's it. It won't corrupt your system or your KiCad installation.

I know: many install instructions include `--user` for the sake of good practice. Here, it is *actually very important* to use the `--user` flag. It will install somewhere safe like "~/Library/.../site-packages", rather than somewhere inside the KiCad application bundle.

If you forget `--user` and then try to install binaries and MacOS invalidates the application's code signature, read [KiKit's explanation](https://yaqwsx.github.io/KiKit/latest/installation/macos/) of KiCad code signatures. Otherwise, reinstall the app to restore the code signature.

### Advanced: explicit installation paths
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

### Advanced: external package managers
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
