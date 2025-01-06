# Troubleshooting Installation

\[**cannot write to package directory**\] Step 3 attempts to write a file in the installation of `kigadgets`. If that fails because you don't have file permissions or something, you can instead set the environment variable "PCBNEW_PATH" to the first path to Path A. Put this line in your .bashrc or .zshrc
```bash
# In general: export PCBNEW_PATH="[Path A]"
export PCBNEW_PATH=/usr/lib/python3/dist-packages/pcbnew.py  # For example
```

\[**python version errors**\] Some external libraries might be compiled. `pcbnew.py` does depend on compiled code (called `_pcbnew.so`). That means not all versions of python work. You may get errors in your terminal that say "version `GLIBCXX_3.4.30' not found". To fix this, determine the version used in KiCad with this command in the GUI terminal
```python
>>> import sys; sys.version_info
sys.version_info(major=3, minor=10, ...)
```
Then, in your external terminal, create a conda environment with that same python version. Run the shell commands again, and do the rest of your batch processing within this conda environment. Note, sometimes python 3.8 so-files will work with 3.10, but matching these versions is the best way to guarantee compatibility.

\[**Upgrading KiCad**\] User configuration directories are different for versions 6 and 7. You may not want to keep multiple copies of script code. One approach is to keep all 3rd party code in `~/.config/kicad/scripting` (Linux), and then symbolic link that into the specific version directory.
```bash
ln -s ~/.config/kicad/scripting ~/.config/kicad/7.0/scripting
```
