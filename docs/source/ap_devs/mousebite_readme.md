# Kigadgets mousebite action plugin
A simple example of an action plugin based on `kigadgets`. It illustrates
- scripts that modify board contents
- dual GUI and CLI entry point strategy
- Use of Ctrl-Z and action plugins
- simple custom GUI: fbp design, user input, state caching

![Mousebite demo](https://github.com/atait/kicad-python/blob/main/examples/action_plugins/mousebite_kigadget/icons/mousebite-demo.gif?raw=true)

mousebite_script.py can be applied either in GUI or in CLI. One implication is that we can put it in non-GUI pytest integrations, and it is testing the *same code* that the GUI will use.

To make other simple plugins, look through this example. If you like reading, here is more [discussion on AP packaging](./index) with `kigadgets`.

## Usage
### GUI entry point
Symlink this directory to your kicad scripting path, for example (Linux)

```bash
ln -s /the/full/path/to/examples/action_plugins/mousebite_kigadget ~/.config/kicad/scripting/plugins
```

Reload external plugins (or restart pcbnew), then click the button with a picture of a mouse.

![Mousebite Icon](../media/mouse-128.png)

### CLI entry point
`python mousebite_script.py my_example.kicad_pcb` for example. Use `-h` flag to see options. To run with the included example file,

```bash
cd examples/action_plugins
python mousebite_kigadget/mousebite_script.py tests/src_layouts/mousebite_api.kicad_pcb
pcbnew tests/src_layouts/mousebite_api-proc.kicad_pcb  # To see the result of CLI processing
```
