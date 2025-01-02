# Getting Started

```{toctree}
:titlesonly:
troubleshooting
macos_workaround
```

## Installation via package and content manager
**IN PROGRESS**

v6+ only

1. Open kicad menu Tools > Plugin and Content Manager.
2. Scroll down to `kigadgets`
3. Double click. Apply transaction.
4. You are done

## Installation via PyPI
```bash
pip install kigadgets
python -m kigadgets
```
The second command links paths needed for headless scripts to find `pcbnew` and for GUI plugins to find python packages external to KiCad, including `kigadgets`. It does not need special privileges and will report everything it does to the command line.
For more information on what the linker is doing, why, and advanced options, read more detail [here](../design/linker_underthehood).

> **Mac users:** There is an extra step. Read about python on Mac [here](./macos_workaround).

Try it out in GUI: Quit and reopen pcbnew application. Open its terminal, then run
```python
pcb.add_circle((100, 100), 20, 'F.Silkscreen'); pcbnew.Refresh()
```

Try it out in headless mode: Download this repo to get the tests and run
```bash
pip install tests/requirements.txt
pytest tests
```
on MacOS, after doing the [extra Mac step](./macos_workaround), run this instead
```bash
kipython -m pip install
kipython -m pytest tests
```