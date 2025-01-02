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

## Installation via PyPI (auto link)
```bash
pip install kigadgets
Try it out in GUI: Quit and reopen pcbnew application. Open its terminal, then run
```python
pcb.add_circle((100, 100), 20, 'F.Silkscreen'); pcbnew.Refresh()
```

Try it out in headless mode: Download this repo to get the tests and run
```bash
pip install tests/requirements.txt
pytest tests
```
```bash
(ki) git clone git@github.com/atait/kicad-python
(ki) pip install -e kicad-python
```
Then follow the linker steps above.

[**Want to know what `link_kigadgets_to_pcbnew` is doing for you?**](../design/linker_underthehood)
