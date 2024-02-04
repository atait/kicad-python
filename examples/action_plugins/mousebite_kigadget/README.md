A simple example of an action plugin based on `kigadgets`.

mousebite_script.py can be applied either in GUI or in CLI. One implication is that we can put it in non-GUI pytest integrations, and it is testing the *same code* that the GUI will use.

For explanation of the plugin package structure and strategy
To make more simple plugins, look through this example. If you like reading, more explanation on AP packaging is in the documentation \<link does not exist yet\>.

## Usage
**GUI**: symlink this directory to your kicad scripting path, restart pcbnew, then click the button with a mouse. For example

```bash
ln -s examples/action_plugins/mousebite_kigadget ~/.config/kicad/scripting/plugins
```

**CLI**: `python mousebite_script.py my_example.kicad_pcb` for example. To run with the included example file,

```bash
cd examples/action_plugins
python mousebite_kigadget/mousebite_script.py tests/src_layouts/mousebite_api.kicad_pcb
pcbnew tests/src_layouts/mousebite_api-proc.kicad_pcb
```
