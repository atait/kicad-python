""" Automatic linker to pcbnew GUI and pcbnew python package
    Use this one time to create the link by running python -m kigadgets

    It will also symlink "kipython" for Mac users
    kipython refers to the python executable that ships with KiCad installation
"""

import os
import sys
import argparse
import shutil

# Tells this package where to find pcbnew module, locally stored after initial path finding
pcbnew_path_store = os.path.join(os.path.dirname(__file__), ".path_to_pcbnew_module")


def get_pcbnew_path_from_file():
    if not os.path.isfile(pcbnew_path_store):
        return None
    with open(pcbnew_path_store) as fx:
        return fx.read().strip()


def get_pcbnew_path():
    """Look for the real pcbnew.py from
        1. environment variable PCBNEW_PATH, then
        2. cached file ./.path_to_pcbnew_module
        3. default install locations (platform dependent)

    If none of these work, return None
    """
    pcbnew_swig_path = os.environ.get("PCBNEW_PATH", get_pcbnew_path_from_file())
    if not pcbnew_swig_path:
        populate_existing_default_paths()
        pcbnew_swig_path = _paths["pcbnew"]
    if not pcbnew_swig_path:
        return None
    # Validate pcbnew.py file characteristics
    if not os.path.basename(pcbnew_swig_path).startswith("pcbnew.py"):
        print(
            "kigadgets: Incorrect location for 'PCBNEW_PATH' ({})."
            " It should point to a file called pcbnew.py".format(pcbnew_swig_path)
        )
        return None
    if not os.path.isfile(pcbnew_swig_path):
        print(
            "kigadgets: Incorrect location for 'PCBNEW_PATH' ({})."
            " File does not exist".format(pcbnew_swig_path)
        )
        return None
    return pcbnew_swig_path


def get_pcbnew_module(verbose=True):
    """returns the imported module. Modifies sys.path so that
    subsequent "import pcbnew" will work as expected.
    """
    # os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = "/Applications/KiCad/KiCad.app/Contents/Frameworks"
    pcbnew_bare = None
    try:
        pcbnew_bare = __import__("pcbnew")  # If this works, we are probably in the pcbnew application, and we're done.
        return pcbnew_bare
    except ImportError:
        pass

    pcbnew_swig_path = get_pcbnew_path()
    if pcbnew_swig_path:
        # if 'Frameworks' in pcbnew_swig_path:
        #     dynlib_path = pcbnew_swig_path.split('Frameworks')[0] + 'Frameworks'
        #     sys.path.insert(0, dynlib_path)
        sys.path.insert(0, os.path.dirname(pcbnew_swig_path))
        try:
            pcbnew_bare = __import__("pcbnew")
        except ImportError as err:
            if verbose:
                print(
                    "kigadgets: pcbnew.py was located but could not be imported."
                    " You will be able to use kigadgets within the pcbnew GUI application,"
                    " but not in this standalone environment. Error was:\n"
                )
                print(err)
                print()
            if not sys.platform.startswith("linux"):
                macwin_on_dlopen_error()
    else:
        # failed to find pcbnew
        if verbose:
            print(
                "kigadgets: KiCad's pcbnew.py not found. pcbnew.py is required to use kigadgets."
                " If KiCad is installed in a non-default location,"
                " It gets installed when you install the KiCad application, but not necessarily on your python path."
                " Link it to kigadgets by running the command"
                "\n   python -m kigadgets"
                "\nMore information on linking at https://kigadgets.readthedocs.io"
            )
    if pcbnew_bare is None and verbose:
        print("Continuing with pcbnew = None")
    return pcbnew_bare


# --- Searching defaults

_paths = dict(kipython=None, pcbnew=None, user=None, mac_app=None)


def latest_version_configpath(config_rootpath, subpath=None):
    """Returns the latest version of a directory in the config_rootpath
        parent/kicad/
        - 7.0
        - 8.0

    latest_version_configpath('parent/kicad')  will return 'parent/kicad/8.0'
    """
    try:
        config_rootpath = os.path.normpath(config_rootpath)
        dirs = list(os.listdir(config_rootpath))
    except FileNotFoundError:
        return None
    if len(dirs) == 0:
        return None
        # raise ValueError("No contents found in {}".format(config_rootpath))
    latest_V = sorted(dirs)[-1]
    out_path = os.path.join(config_rootpath, latest_V)
    if subpath:
        out_path = os.path.join(out_path, os.path.normpath(subpath))
    return out_path


def get_default_paths():
    """This function will not execute anything from pcbnew or KiCad.
    populate_optimal_paths() will do that
    """
    default_locations = dict()
    if sys.platform.startswith("linux"):
        default_locations["kipython"] = "/usr/bin/python3"  # It can't be that easy
        default_locations["pcbnew"] = [
            "/usr/lib/python3/dist-packages/pcbnew.py",
            "/usr/lib/python3/site-packages/pcbnew.py",
        ]
        root = os.path.expanduser("~/.config/kicad")
        default_locations["user"] = [
            latest_version_configpath(root),
            root
        ]
    elif sys.platform.startswith("darwin"):
        application = "/Applications/KiCad/KiCad.app"  # This is not guaranteed. User could have renamed it
        default_locations["mac_app"] = application
        framework = os.path.join(application, "Contents/Frameworks/Python.framework/Versions/Current")

        default_locations["kipython"] = os.path.join(framework, "bin/python3")
        default_locations["pcbnew"] = os.path.join(framework, "lib/python3.9/site-packages/pcbnew.py")
        default_locations["user"] = [
            os.path.expanduser("~/Documents/KiCad"),  # Used in 8.0
            os.path.expanduser("~/Library/Preferences/kicad"),
        ]
    elif sys.platform.startswith("win"):
        root = "C:/Program Files/KiCad/"

        default_locations["kipython"] = latest_version_configpath(root, "bin/python.exe")
        default_locations["pcbnew"] = latest_version_configpath(root, "bin/Lib/site-packages/pcbnew.py")
        default_locations["user"] = [
            latest_version_configpath(os.path.expanduser("~/Documents/KiCad")),
            latest_version_configpath(os.path.expanduser("~/AppData/Roaming/kicad")),
        ]
    else:
        raise RuntimeError(
            f"kigadgets: Unsupported operating system: {sys.platform}"
        )
    # Expand to lists
    for k, v in default_locations.items():
        if not isinstance(v, list):
            default_locations[k] = [v]
    return default_locations


def populate_existing_default_paths():
    # What to do when there are multiple or zero default search paths that resolved
    # Constrain to the first existing path
    # Modifies the module-level _paths dictionary
    defaults = get_default_paths()
    for k, v in defaults.items():
        for path in v:
            if path and os.path.exists(path):
                _paths[k] = path
                break
        else:
            # None of the paths exist. Make it None
            # raise ValueError('Nothing found for {}'.format(k))
            _paths[k] = None


def kipython_one_liner(script):
    # This works whether or not "kipython" is on the PATH
    if sys.platform.startswith("linux"):
        try:
            return exec(script)
        except ImportError:
            return None
    import subprocess

    if _paths["kipython"] is None:
        raise ValueError("No kipython executable found")
    cmd = [_paths["kipython"], "-c", script]
    ret = subprocess.run(cmd, capture_output=True)
    if ret.returncode:
        raise RuntimeError("kigadgets: One-liner failed\n" + cmd)
    return ret.stdout.decode().strip()


def get_ver():
    assert _paths["kipython"] is not None
    try:
        verstr = kipython_one_liner("import pcbnew; print(pcbnew.GetMajorMinorVersion())")
        assert verstr is not None
    except (ImportError, AssertionError):
        verstr = '1.0'
    ver = tuple(int(x) for x in verstr.split("."))
    majver = ver[0]
    if ver[1] == 99:
        majver += 1
    return majver


def get_cfg_script():
    majver = get_ver()
    cfg_script = "import pcbnew; print(pcbnew.SETTINGS_MANAGER{}GetUserSettingsPath())"
    cfg_script = cfg_script.format("." if majver >= 6 else "_")
    return cfg_script


def populate_optimal_paths():
    """Populate the paths for kipython, pcbnew, and user settings directory.
    Runs pcbnew or kipython to ensure they are synchronized with one another.
    """
    populate_existing_default_paths()
    if _paths["pcbnew"] and sys.platform.startswith("linux"):
        # This fallback might not work on Mac/Windows
        sys.path.insert(0, os.path.dirname(_paths["pcbnew"]))
        import pcbnew
        if get_ver() >= 6:
            _paths["user"] = pcbnew.SETTINGS_MANAGER.GetUserSettingsPath()
        else:
            _paths["user"] = pcbnew.SETTINGS_MANAGER_GetUserSettingsPath()
    elif _paths["kipython"]:
        _paths["pcbnew"] = kipython_one_liner("import pcbnew; print(pcbnew.__file__)")
        _paths["user"] = kipython_one_liner(get_cfg_script())
    else:
        raise ValueError(
            "Default installation of pcbnew.py and kipython not found. Must find paths manually"
        )


# --- Symbolic linking for MacOS
def macwin_on_dlopen_error():
    """If this is called, we have given up on importing pcbnew.py.
    Almost always this is because non-KiCad python is being used on Mac or Windows
    """
    if sys.platform.startswith("linux"):
        return False
    populate_existing_default_paths()
    if not _paths["kipython"]:
        print(
            "kipython executable not found. Is KiCad installed in /Applications/KiCad/KiCad.app?"
        )
        return False
    # Most likely, they just forgot to call kipython
    print(
        "To use pcbnew outside of GUI, you need to run this with"
        "\n  kipython <your script> instead of  python <your script>\n"
    )
    if sys.platform.startswith("win"):
        alias = "    Function kipython [~ & '{}' $args ]~\n".format(_paths["kipython"])
        alias = alias.replace("[~", "{").replace("]~", "}")
        print(
            f'You should symlink or alias "kipython" to {_paths["kipython"]}. '
            f'In any command line, run this command,\n{alias}'
        )
    else:
        if not shutil.which("kipython"):
            print(
                f'kipython is not yet symlinked to {_paths["kipython"]}. '
                'In any command line, run this command:\n'
                '    python -m kigadgets\n'
            )
    return True


def input_preferred_PATH():
    """Prompts the user to select a preferred PATH for symbolic linking of 'kipython'.

    If no existing symlink is found, it lists valid destination paths for creating
    the 'kipython' symlink and prompts the user to select one. The user can cancel
    the operation by entering 'q' or press enter to select the default path.
    """
    shell_paths = os.environ["PATH"].split(":")
    valid_paths = []
    for pp in shell_paths:
        if not os.path.isdir(pp):
            continue
        if not os.access(pp, os.W_OK):
            continue
        if "brew" in pp:
            continue
        ppath = pp.replace(os.path.expanduser("~"), "~", 1)
        pclean = os.path.join(ppath, "kipython")
        if pp == "/usr/local/bin":
            valid_paths.insert(0, pclean)
        else:
            valid_paths.append(pclean)

    print("Valid destination paths for symbolic linking kipython:")
    for i, pp in enumerate(valid_paths):
        line = f"  {i}. {pp}"
        if os.path.exists(pp):
            line += " (exists)"
        if pp == "/usr/local/bin/kipython":
            line += " (recommended)"
        print(line)

    def input_number():
        select_index = input("Pick a path [q to cancel] [Press enter for 0]: ")
        if not select_index:
            select_index = 0
        if select_index == "q":
            return None
        try:
            select_index = int(select_index)
        except ValueError:
            print("Invalid selection. Try again")
            return input_number()
        if select_index < 0 or select_index >= len(valid_paths):
            print("Invalid selection. Try again")
            return input_number()
        return select_index

    select_index = input_number()
    if select_index is None:
        return None
    else:
        return valid_paths[select_index]


def symlink_kipython_executable(dest_path=None):
    """Creates a symbolic link to the kipython executable in a location that is in the PATH"""
    if not _paths["kipython"]:
        print("Default bundled python executable is not available. Is KiCad installed?")
        return None
    if sys.platform.startswith("win"):
        print(
            f"Your bundled kipython executable was found at {_paths['kipython']}\n"
            "Use that version of python. "
            "Recommended to create a symbolic link to the bundled python."
        )
        return None
    # print('Bundled python executable exists at', _paths['kipython'])
    if dest_path is None and shutil.which("kipython"):
        print("kipython is already on your PATH")
        return None
    if dest_path is None:
        print("kipython is not on your PATH. Let's create a symlink, or press q to cancel")
        dest_path = input_preferred_PATH()
    if not dest_path:
        print("No path selected. Exiting")
        return None
    try:
        os.symlink(_paths["kipython"], dest_path)
        print("Success: ln -s {} {}".format(_paths["kipython"], dest_path))
    except OSError as err:
        print("kigadgets: Error creating symlink:", err)
        dest_path = None
    return dest_path


# --- Define scripts and do linking

# Tells pcbnew application where to find this package
startup_script = """### Auto generated by kigadgets initialization for pcbnew console
import sys, pcbnew
sys.path.append("{}")
import kigadgets
print('kigadgets (v{{}}) located at:'.format(kigadgets.__version__), kigadgets.__path__)
from kigadgets.board import Board
pcb = Board.from_editor()
"""

plugin_script = """### Auto generated by kigadgets initialization for pcbnew action plugins
import sys
sys.path.append("{}")
"""

if sys.platform.startswith("win"):
    _print_file = print
    _print_contents = print
else:
    def _print_file(arg):
        print("\033[4m\033[91m" + arg + "\033[0m")

    def _print_contents(arg):
        print("\033[92m" + arg + "\033[0m")


def write_PyShell_startup_script(kicad_config_path, dry_run=False, cleanup=False):
    # Determine what to put in the startup script
    kigadgets_package_path = os.path.dirname(__file__)
    kigadgets_search_path = os.path.dirname(kigadgets_package_path)
    if sys.platform.startswith("win"):
        kigadgets_search_path = "\\\\".join(kigadgets_search_path.split("\\"))
    startup_contents = startup_script.format(kigadgets_search_path)
    # Determine where to put the startup script
    startup_file = os.path.join(kicad_config_path.strip(), "PyShell_pcbnew_startup.py")

    # Check that we are not overwriting something
    write_is_safe = True
    if os.path.isfile(startup_file):
        with open(startup_file) as fx:
            line = fx.readline()
        if line.startswith("### DEFAULT STARTUP FILE"):
            pass
        elif line.startswith("### Auto generated by kigadgets"):
            pass
        else:
            write_is_safe = False

    # Check for write access
    if not os.access(kicad_config_path, os.W_OK):
        print(f"No write access to {kicad_config_path}. Continuing without writing.")
        return

    # Write the startup script
    _print_file(startup_file)
    if write_is_safe:
        if not dry_run:
            if cleanup:
                os.remove(startup_file)
            else:
                with open(startup_file, "w") as fx:
                    fx.write(startup_contents)
    else:
        print(
            f"kigadgets: Warning: Startup file is not empty:\n{startup_file}"
            "You can delete this file with\n\n"
            f"    rm {startup_file}\n\n"
            "or manually write it with these contents"
        )
    if not cleanup:
        _print_contents(startup_contents)


def write_plugin_importer_script(kicad_config_path, dry_run=False, cleanup=False):
    """Mac: this has no effect because you have to install kigadgets using kipython"""
    # Write the plugin importer
    kigadgets_package_path = os.path.dirname(__file__)
    kigadgets_search_path = os.path.dirname(kigadgets_package_path)
    if sys.platform.startswith("win"):
        kigadgets_search_path = "\\\\".join(kigadgets_search_path.split("\\"))
    plugin_dir = os.path.join(kicad_config_path.strip(), "scripting", "plugins")
    os.makedirs(plugin_dir, exist_ok=True)
    plugin_file = os.path.join(plugin_dir, "expose_kigadgets_plugin.py")
    plugin_contents = plugin_script.format(kigadgets_search_path)
    _print_file(plugin_file)

    if not dry_run:
        if cleanup:
            os.remove(plugin_file)
        else:
            with open(plugin_file, "w") as fx:
                fx.write(plugin_contents)
    if not cleanup:
        _print_contents(plugin_contents)

    # Cleanup old script if it exists
    old_plugin_file = os.path.join(plugin_dir, "initialize_kicad_python_plugin.py")
    if not dry_run and os.path.isfile(old_plugin_file):
        with open(old_plugin_file) as fx:
            line = fx.readline()
        if line.startswith("### Auto generated by kicad-python"):
            os.remove(old_plugin_file)
            if os.path.isfile(old_plugin_file + "c"):
                os.remove(old_plugin_file + "c")


def create_link(pcbnew_module_path=None, kicad_config_path=None, dry_run=False, cleanup=False):
    """Create the link between kigadgets and pcbnew
    All of this works with pcbnew=None (i.e. not discoverable yet)
    """
    if pcbnew_module_path is None or kicad_config_path is None:
        if cleanup:
            populate_existing_default_paths()
        else:
            populate_optimal_paths()
        if pcbnew_module_path is None:
            pcbnew_module_path = _paths["pcbnew"]
        if kicad_config_path is None:
            kicad_config_path = _paths["user"]

    # Check if it imported
    if not get_pcbnew_module(verbose=False) and get_pcbnew_path():
        if not sys.platform.startswith("linux") and _paths["kipython"]:
            symlink_kipython_executable()

    # Write the scripts
    writing = "Would write" if dry_run else "Writing"
    if cleanup:
        writing = "Would remove" if dry_run else "Removing"
    print(f"\n1. {writing} console startup script: for GUI snippet scripting")
    write_PyShell_startup_script(kicad_config_path, dry_run, cleanup=cleanup)
    print(f"2. {writing} plugin importer: for action plugin development")
    write_plugin_importer_script(kicad_config_path, dry_run, cleanup=cleanup)

    # Store the location of pcbnew module
    print(f"3. {writing} pcbnew path: for batch processing outside KiCad")
    _print_file(pcbnew_path_store)

    if not dry_run:
        if cleanup:
            os.remove(pcbnew_path_store)
        else:
            with open(pcbnew_path_store, "w") as fx:
                fx.write(pcbnew_module_path.strip())
    if not cleanup:
        _print_contents(pcbnew_module_path)

    # Try it
    if dry_run or cleanup:
        return
    print("Successfully linked kigadgets with pcbnew")


# --- CLI

help_msg = """
Create bidirectional link between kigadgets and pcbnew.

Usage:
    python -m kigadgets [pcbnew_module_path] [kicad_config_path] [-n]

Arguments:
    pcbnew_module_path   Path to the pcbnew.py module
    kicad_config_path   Path to the KiCad user configuration directory you want to use
    -n, --dry-run       Do not write any files, just show what would be done

Path arguments are usually detected automatically.
To use explicit arguments or custom install locations, see
kigadgets.readthedocs.io/en/latest/installation.html#optional-installation-steps
"""


parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=help_msg)
parser.add_argument("pcbnew_module_path", type=str, nargs="?", default=None)
parser.add_argument("kicad_config_path", type=str, nargs="?", default=None)
parser.add_argument("-n", "--dry-run", action="store_true")
parser.add_argument("-c", "--cleanup", action="store_true")


def cl_main():
    from kigadgets import __version__, pcbnew_version

    vkga = "kigadgets v{}".format(__version__)
    vpcb = "pcbnew    v{}".format(pcbnew_version(asstr=True))
    verz = vkga + "\n" + vpcb
    parser.add_argument("-v", "--version", action="version", version=verz)
    args = parser.parse_args()
    create_link(
        args.pcbnew_module_path,
        args.kicad_config_path,
        dry_run=args.dry_run,
        cleanup=args.cleanup,
    )


def cl_geohash():
    """Print geohash for a board - WIP"""
    filename = sys.argv[1] if len(sys.argv) > 1 else "my_board.kicad_pcb"
    from kigadgets import Board, pcbnew_bare as pcbnew

    pcb = Board.load(filename)
    print("Geohash:", pcb.geohash())
