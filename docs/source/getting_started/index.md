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

1. 
```
pip install kigadgets
```

2. Open the pcbnew GUI application. Open its terminal and run this command in kicad 6+
```python
import pcbnew; print(pcbnew.__file__, pcbnew.SETTINGS_MANAGER.GetUserSettingsPath())
```
This will print 2 paths. *Copy that entire line.*

> For kicad 5, replace that last command with `pcbnew.SETTINGS_MANAGER_GetUserSettingsPath()` (note the last underscore).

3. Go back to your external command line or Terminal shell, and run this command, replacing \[paste here\] with what you copied
```bash
link_kigadgets_to_pcbnew [paste here]
```
For example,
```bash
link_kigadgets_to_pcbnew /usr/lib/python3/dist-packages/pcbnew.py /home/username/.config/kicad
```

4. Try it out! Quit and reopen pcbnew application. Open its terminal, then run
```python
pcb.add_circle((100, 100), 20, 'F.Silkscreen'); pcbnew.Refresh()
```

## Developer Installation
```bash
(ki) git clone git@github.com/atait/kicad-python
(ki) pip install -e kicad-python
```
Then follow the linker steps above.

[**Want to know what `link_kigadgets_to_pcbnew` is doing for you?**](../design/linker_underthehood)
