# Developing Action Plugins

`kigadgets` was developed with action plugins (and batch processing) in mind. It can give cross-version compatibility, code that is easier to understand, and the possibility for triple CLI/API/GUI entry points.

An example is included in "examples/action_plugins/mousebite_kigadget". All of the mousebite logic is in "mousebite_script.py" (<200 lines). Other files do registration and GUI dialog stuff.

## New plugins
Anyone can make action plugins! They don't all need to be deployed through Package and Content Manager, and they don't need to follow software enginering good practice whatsoever. It is likely that you have some kind of task that you do repetitively but not many others do. You'll want to automate that task, then bestow upon it a proper menu button (explained here).

### Start with the examples
To get started, use the example in "examples/action_plugins/mousebite_kigadget" as a template. [See Readme here](./mousebite_readme). For it to show up in GUI, copy that directory to your kicad-user plugin directory, for example (Linux) ~/.config/kicad/scripting/plugins/. Copy it again but rename it to your plugin's name.

Most of the work happens in "mousebite_script.py". This will contain your automation. The other ".py" files can be very similar for other action plugins. Go through them and rename files, imports, and classes appropriately (`Mousebite` --> `MyPlugin` and so on). Don't forget to write tests like in the example/action_plugins/tests.

If your action plugin needs complex dialogs, I recommend wxformbuilder (see the included .fbp file). For simple dialogs, you can use `kigadgets.notify` and `kigadgets.query_user`.

## Existing plugins
Automation, open-source plugins, python scripting, and procedural layout are some of the key differentiating features of KiCad. It is the #1 reason I migrated from Eagle to KiCad in 2018.

KiCAD v9 is coming; some people still use v5; nobody knows what is currently in the auto-generated SWIG interface, let alone what will change. Maintaining different branches/releases for different KiCAD versions, then deploying via PCM, is the accepted method. It is tedious and requires developer dedication that would be remarkable for a hardware designer.

The cross-version compatibility of `kigadgets` can help. It can be delicately inserted anywhere in existing code using `wrap` and `native_obj`.

```python
# file: legacy_script.py
...
my_zone = get_a_zone_somewhere()
my_zone.SetClearance(my_zone.GetClearance() * 2)
# The above line will not work >v5
do_something_else_to(my_zone)
```
Modify that code like this:
```python
...
my_zone = get_a_zone_somewhere()

### Begin insertion
from kigadgets.zone import Zone
zone_tmp = Zone.wrap(my_zone)  # Intake from any version
zone_tmp.clearance *= 2        # Version independent
my_zone = zone_tmp.native_obj  # Outlet to correct version
### end insertion

do_something_else_to(my_zone)
```
Now this code is forwards compatible without breaking backwards compatibility.
