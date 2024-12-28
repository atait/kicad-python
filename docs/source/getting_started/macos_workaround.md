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
or symlinking it.
```bash
# One time, anywhere
ln -s "/Applications/KiCad/KiCad.app/Contents/Frameworks/ython.framework/Versions/Current/bin/python3" /usr/local/bin/kipython
```
You can replace `/usr/local/bin` with anything on your `PATH`.

```bash
$ kipython -m pip install -e .  # For kigadgets development
$ kipython -m pip install <other packages>  # Things get installed Application-wide
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
