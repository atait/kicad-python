# MacOS/v7 Bug Workaround

`pcbnew.py` from KiCAD v7 does not import on MacOS. There is some issue in the linking process to `pcbnew.so`. Everything works fine when inside the GUI, but not outside.

## Expose KiCAD's builtin python
Outside the GUI, the workaround is to use the `python` that comes bundled with KiCAD. I recommend aliasing it.

```bash
# ~/.profile, or ~/.zshrc, etc.
...
alias kipython="/Applications/KiCad/KiCad.app/Contents/Frameworks/ython.framework/Versions/Current/bin/python3"
...
```

or symlinking it. Bonus points for encapsulating in a conda environment.
```bash
(base) $ kipython_path="/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
(base) $ conda_envbin_path="~/miniconda3/envs/ki/bin/kipython"
(base) $ ln -s $kipython_path $conda_envbin_path
```
replacing "miniconda3" with your conda (or mamba) root; replacing "ki" with the name of desired environment.

## Configuring builtin environment
You will need to reinstall all needed packages using kicad's pip like this
```bash
(base) $ conda activate ki
(ki) $ kipython -m pip install -e .  # For kigadgets development
(ki) $ kipython -m pip install <other packages>
```

| Caution |
| --- |
| Installing things with `kipython` will get installed in the GUI's environment as well. The packages will not be encapsulated between particular conda environments. That is potentially bad but can always be reverted by reinstalling KiCAD. |

## Test it
Now you can run tests when cd'ed inside the repo top level
```bash
(ki) $ kipython -m pip install tests/requirements.txt
(ki) $ kipython -m pytest tests
```
