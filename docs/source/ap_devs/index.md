# Developing Action Plugins

```{toctree}
:titlesonly:
mousebite_readme
onepush_readme
developer_guide
```

`kigadgets` was developed with action plugins (and batch processing) in mind. It can give cross-version compatibility, code that is easier to understand, and the possibility for triple CLI/API/GUI entry points.

Anyone can make action plugins! They don't all need to be deployed through Package and Content Manager, and they don't need to follow software enginering good practice whatsoever. It is likely that you have some kind of task that you do repetitively but not many others do. You'll want to automate that task, then bestow upon it a proper menu button (explained here).

## Start with the examples
An example is included in "examples/action_plugins/mousebite_kigadget". All of the mousebite logic is in "mousebite_script.py" (<200 lines). Other files do registration and GUI dialog stuff. [See Mousebite Readme here](./mousebite_readme). Follow its instructions to use the plugin.

To make your own plugin, use this example as a template. Most of the work happens in "mousebite_script.py". This will contain your automation. The other ".py" files can be very similar for other action plugins, just renamed for your action plugin. Go through them and rename files, imports, and classes appropriately (`Mousebite` --> `MyPlugin` and so on).

Mousebite gives examples of dialog creation with wxformbuilder (see the included .fbp file) and also simple dialogs like `kigadgets.notify` and `kigadgets.query_user`. Mousebite illustrates dual-entry point pattern and a basic automated testing setup (see example/action_plugins/tests).


