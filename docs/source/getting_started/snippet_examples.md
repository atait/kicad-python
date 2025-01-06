## Snippet examples
These snippets are run in the GUI terminal. They are common automations that aren't worth making dedicated action plugins. There is no preceding context; the linking step above provides `pcb` to the terminal. These all should work in pcbnew 5, 6, 7, 8, and 8.99 on Mac, Windows, or Linux.

### Hide silkscreen labels of selected footprints
```python
for fp in pcb.footprints:
    if fp.is_selected:
        fp.reference_label.visible = False
pcbnew.Refresh()
```
![](doc/simple_script.png)

### Move all silk labels to fab layers
Instead, we can keep them on Fab layers so we can still see them while designing the PCB.
```python
for m in pcb.footprints:
    ref = m.reference_label.layer.split('.')  # Gives tuple like ('B', 'Silkscreen')
    if len(ref) > 1 and ref[1].startswith('Silk'):
        ref.layer = ref[0] + '.Fab'
pcbnew.Refresh()
```

### Select similar vias
This snippet assumes you have selected one via
```python
og_via = pcb.selected_items[0]
for via2 in pcb.vias:
    if via2.diameter != og_via.diameter: continue
    if via2.drill != og_via.drill: continue
    via2.select()
og_via.select(False)
pcbnew.Refresh()
```
See `via.py` for additional functionality related to micro and blind vias.

### Change all drill diameters
Because planning ahead doesn't always work
```python
for v in pcb.vias:
    if v.drill > 0.4 and v.drill < 0.6:
        v.drill = 0.5
pcbnew.Refresh()
```

### Put silkscreen over tracks
Not sure why to do this besides a nice look.
```python
for t in pcb.tracks:
    new_width = t.width * 1.1
    pcb.add_line(t.start, t.end, 'F.SilkS' if t.layer == 'F.Cu' else 'B.SilkS', new_width)
pcbnew.Refresh()
```

### Select everything schematically connected to this footprint
```python
footprint = pcb.selected_items[0]
nets = {pad.net_name for pad in footprint.pads}
nets -= {'GND', '+5V'}  # because these are connected to everything
for mod in pcb.footprints:
    if any(pad.net_name in nets for pad in mod.pads):
        mod.select()
```

### Keep track of live editor state
In GUI, `kigadgets` stays synchronized with the state of the underlying native objects even when they are modified elsewhere because it is wrapping the C++ state rather than holding a Python state.
```python
from kigadgets.drawing import Rectangle
my_rect = Rectangle((0,0), (60, 40))
pcb.add(my_rect)
pcbnew.Refresh()
print(my_rect.x, my_rect.contains((1,1)))  # 30 True
input('Go move that rectangle. When done, refocus in this terminal and press enter.')
# Go move the new rectangle in the editor
print(my_rect.x, my_rect.contains((1,1)))  # 15.2 False
pcb.remove(my_rect)
pcbnew.Refresh()
```
This gives some cool options for capturing user input interactively based on their actions in the layout editor.

### Procedural layout
Suppose you want to test various track width resistances.
```python
y = 0
length = 50
widths = [.12, .24, .48, .96]
r_contact = 5
for w in widths:
    pcb.add_track([(0, y), (length, y)], 'F.Cu', width=w)
    for lay in ['F.Cu', 'F.Mask']:
        for x in [0, length]:
            pcb.add_circle((x, y), r_contact / 2, lay, r_contact)
    pcb.add_text((length/2, y - 2), 'width = {:.2f}mm'.format(w), 'F.SilkS')
    y += 20
pcbnew.Refresh()
```
Go ahead and try this out in the pcbnew terminal, although this type of thing is better to stick in a user library (see above). The sky is the limit when it comes to procedural layout!

> [!TIP]
> If you don't view yourself as a coder, you can become one! Have a look at the snippets above - do you understand what they are doing? If so, you can code.
> While you are [learning python syntax](https://docs.python.org/3/tutorial/index.html), you can just copy the examples above and modify to suit your needs.