''' Automatic linker to pcbnew GUI and pcbnew python package
    Use this one time to create the link.

    1. In pcbnew's terminal window:

        >>> import pcbnew; print(pcbnew.__file__, pcbnew.SETTINGS_MANAGER.GetUserSettingsPath())
        /usr/lib/python3/dist-packages/pcbnew.py /home/username/.config/kicad

    2. Copy the entire output.

    3. In an external terminal, with environment of choice activated::

        (myenv) $ link_kigadgets_to_pcbnew [paste here]
'''
import os
import sys
import argparse

# Tells this package where to find pcbnew module
pcbnew_path_store = os.path.join(os.path.dirname(__file__), '.path_to_pcbnew_module')


def get_pcbnew_path_from_file():
    if not os.path.isfile(pcbnew_path_store):
        return None
    with open(pcbnew_path_store) as fx:
        return fx.read().strip()


def get_pcbnew_path():
    # Look for the real pcbnew from environment and then file
    pcbnew_swig_path = os.environ.get('PCBNEW_PATH', get_pcbnew_path_from_file())
    if pcbnew_swig_path:
        # Validate
        if not os.path.basename(pcbnew_swig_path).startswith('pcbnew.py'):
            raise EnvironmentError(
                'Incorrect location for \'PCBNEW_PATH\' ({}).'
                ' It should point to a file called pcbnew.py'.format(pcbnew_swig_path))
        if not os.path.isfile(pcbnew_swig_path):
            raise EnvironmentError(
                'Incorrect location for \'PCBNEW_PATH\' ({}).'
                ' File does not exist'.format(pcbnew_swig_path))
    else:
        raise EnvironmentError(
            'You have not yet populated .path_to_pcbnew_module.'
            '\nUse the command "link_kigadgets_to_pcbnew" to set it up.')
    return pcbnew_swig_path


def get_pcbnew_module():
    ''' returns the imported <module>. Modifies sys.path so that
        subsequent `import pcbnew` will work
    '''
    # os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = "/Applications/KiCad/KiCad.app/Contents/Frameworks"
    try:
        pcbnew_bare = __import__('pcbnew')  # If this works, we are probably in the pcbnew application, and we're done.
        if hasattr(pcbnew_bare, 'Refresh'):  # Check it is authentic
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
            pcbnew_bare = __import__('pcbnew')
        except ImportError as err:
            print('Warning: pcbnew.py was located but could not be imported.'
                  ' You will be able to use kigadgets within the pcbnew application,'
                  ' but not as a standalone. Error was:\n')
            print(err)
            print('\nContinuing with pcbnew = None')
            pcbnew_bare = None
    else:
        # failed to find pcbnew
        print(
            'pcbnew.py not found. pcbnew is required by kigadgets.'
            ' It gets installed when you install the KiCAD application, but not necessarily on your python path.'
            '\nSee instructions for how to link them at https://github.com/atait/kicad-python'
        )
        pcbnew_bare = None
    return pcbnew_bare


# --- Searching defaults

_paths = dict(kipython=None, pcbnew=None, user=None)

def latest(config_path, subpath=None):
    dirs = list(os.listdir(config_path))
    if len(dirs) == 0:
        # return None
        raise ValueError('No contents found in {}'.format(config_path))
    latest_V = sorted(dirs)[-1]
    out_path = os.path.join(config_path, latest_V)
    if subpath:
        out_path = os.path.join(out_path, subpath)
    return out_path

def populate_existing_default_paths():
    if sys.platform.startswith("linux"):
        _paths['kipython'] = None
        _paths['pcbnew'] = [
            "/usr/lib/python3/dist-packages/pcbnew.py",
            "/usr/lib/python3/site-packages/pcbnew.py",
        ]
        _paths['user'] = os.path.expanduser("~/.config/kicad")
    elif sys.platform == "darwin":
        application = "/Applications/KiCad/KiCad.app"
        framework = os.path.join(application, "Contents/Frameworks/Python.framework/Versions/Current")

        _paths['kipython'] = os.path.join(framework, "bin/python3")
        _paths['pcbnew'] = os.path.join(framework, "lib/python3.9/site-packages/pcbnew.py")
        _paths['user'] = os.path.expanduser("~/Library/Preferences/kicad")
    elif sys.platform == "win32":
        root = "C:/Program Files/KiCAD/"

        _paths['kipython'] = latest(root, "bin/python.exe")
        _paths['pcbnew'] = latest(root, "bin/Lib/site-packages/pcbnew.py")
        _paths['user'] = latest(os.path.expanduser("~/AppData/Roaming/kicad"))
        # PCM = latest(os.path.expanduser("~/OneDrive/Documents/KiCad"), "3rdparty")
    else:
        raise RuntimeError('Unrecognized operating system: {}'.format(sys.platform))

    # Expand to lists
    for k, v in _paths.items():
        if not isinstance(v, list):
            _paths[k] = [v]

    # Constrain to first existing
    for k, v in _paths.items():
        for path in v:
            if path and os.path.exists(path):
                _paths[k] = path
                break
        else:
            # raise ValueError('Nothing found for {}'.format(k))
            _paths[k] = None

def one_liner(script):
    import subprocess
    if _paths['kipython'] is None:
        raise ValueError('No kipython')
    cmd = [_paths['kipython'], '-c', script]
    ret = subprocess.run(cmd, capture_output=True)
    if ret.returncode:
        raise ValueError('One-liner failed\n' + cmd)
    return ret.stdout.decode().strip()

def get_ver():
    assert _paths['kipython'] is not None
    verstr = one_liner("import pcbnew; print(pcbnew.GetMajorMinorVersion())")
    ver = tuple(int(x) for x in verstr.split('.'))
    majver = ver[0]
    if ver[1] == 99:
        majver += 1
    return majver

def get_cfg_script():
    majver = get_ver()
    cfg_script = "import pcbnew; print(pcbnew.SETTINGS_MANAGER{}GetUserSettingsPath())"
    cfg_script = cfg_script.format('.' if majver >= 6 else '_')
    return cfg_script

def populate_optimal_paths():
    populate_existing_default_paths()
    if _paths['kipython']:
        # if _paths['pcbnew'] is None:
        _paths['pcbnew'] = one_liner("import pcbnew; print(pcbnew.__file__)")
        _paths['user'] = one_liner(get_cfg_script())
    elif _paths['pcbnew']:
        # This fallback won't work on Mac/Windows
        sys.path.insert(0, os.path.dirname(_paths['pcbnew']))
        import pcbnew
        if get_ver() >= 6:
            _paths['user'] = pcbnew.SETTINGS_MANAGER.GetUserSettingsPath()
        else:
            _paths['user'] = pcbnew.SETTINGS_MANAGER_GetUserSettingsPath()
    else:
            raise ValueError('Default installation of pcbnew.py and kicad:kipython not found. Must find paths manually')


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

if sys.platform.startswith('win'):
    _print_file = print
    _print_contents = print
else:
    def _print_file(arg):
        print('\033[4m\033[91m' + arg + '\033[0m')

    def _print_contents(arg):
        print('\033[92m' + arg + '\033[0m')


def create_link(pcbnew_module_path=None, kicad_config_path=None, dry_run=False):
    if pcbnew_module_path is None or kicad_config_path is None:
        populate_optimal_paths()
        if pcbnew_module_path is None:
            pcbnew_module_path = _paths['pcbnew']
        if kicad_config_path is None:
            kicad_config_path = _paths['user']
    writing = 'Would write' if dry_run else 'Writing'
    # Determine what to put in the startup script
    my_package_path = os.path.dirname(__file__)
    my_search_path = os.path.dirname(my_package_path)
    if sys.platform.startswith('win'):
        my_search_path = '\\\\'.join(my_search_path.split('\\'))
    startup_contents = startup_script.format(my_search_path)
    # Determine where to put the startup script
    startup_file = os.path.join(kicad_config_path.strip(), 'PyShell_pcbnew_startup.py')

    # Check that we are not overwriting something
    write_is_safe = True
    if os.path.isfile(startup_file):
        with open(startup_file) as fx:
            line = fx.readline()
        if line.startswith('### DEFAULT STARTUP FILE'):
            pass
        elif line.startswith('### Auto generated by kigadgets'):
            pass
        else:
            write_is_safe = False

    # Write the startup script
    print('\n1. {} console startup script: for GUI snippet scripting'.format(writing))
    _print_file(startup_file)
    if write_is_safe:
        if not dry_run:
            with open(startup_file, 'w') as fx:
                fx.write(startup_contents)
    else:
        print('Warning: Startup file is not empty:\n', startup_file)
        print('You can delete this file with')
        print('\n    rm {}'.format(startup_file))
        print('\n or manually write it with these contents')
    _print_contents(startup_contents)

    # Write the plugin importer
    plugin_dir = os.path.join(kicad_config_path.strip(), 'scripting', 'plugins')
    os.makedirs(plugin_dir, exist_ok=True)
    plugin_file = os.path.join(plugin_dir, 'expose_kigadgets_plugin.py')
    plugin_contents = plugin_script.format(my_search_path)
    print('2. {} plugin importer: for action plugin development'.format(writing))
    _print_file(plugin_file)
    if not dry_run:
        with open(plugin_file, 'w') as fx:
            fx.write(plugin_contents)
    _print_contents(plugin_contents)

    # Cleanup old script if it exists
    old_plugin_file = os.path.join(plugin_dir, 'initialize_kicad_python_plugin.py')
    if not dry_run and os.path.isfile(old_plugin_file):
        with open(old_plugin_file) as fx:
            line = fx.readline()
        if line.startswith('### Auto generated by kicad-python'):
            os.remove(old_plugin_file)
            if os.path.isfile(old_plugin_file + 'c'):
                os.remove(old_plugin_file + 'c')

    # Store the location of pcbnew module
    print('3. {} pcbnew path: for batch processing outside KiCAD'.format(writing))
    _print_file(pcbnew_path_store)
    if not dry_run:
        with open(pcbnew_path_store, 'w') as fx:
            fx.write(pcbnew_module_path.strip())
    _print_contents(pcbnew_module_path)

    # Try it
    if dry_run: return
    try:
        get_pcbnew_path()
    except ImportError as err:
        if err.args[0].startswith('dynamic module does not define'):
            print('You are likely using Mac or Windows,'
                  ' which means kicad does not yet support python 3 on your system.'
                  ' You will be able to use kigadgets in the pcbnew application,'
                  ' but not outside of it for batch processing.')
        else:
            raise
    else:
        print('Successfully linked kigadgets with pcbnew')


# --- CLI

help_msg = """
Create bidirectional link between kigadgets and pcbnew
To get the arguments correct, copy this and run it in pcbnew application console:

    import pcbnew; print(pcbnew.__file__, pcbnew.SETTINGS_MANAGER.GetUserSettingsPath())
    # which produces output like
    /usr/lib/python3/dist-packages/pcbnew.py /home/username/.config/kicad

    2. Copy the entire output.

    3. In an external terminal, with environment of choice activated::

        (myenv) $ link_kigadgets_to_pcbnew [paste here]

For kicad 5, replace that last command with `pcbnew.SETTINGS_MANAGER_GetUserSettingsPath()`
    - Note the last underscore
"""


parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=help_msg)
parser.add_argument('pcbnew_module_path', type=str, nargs='?', default=None)
parser.add_argument('kicad_config_path', type=str, nargs='?', default=None)
parser.add_argument('-n', '--dry-run', action='store_true')

def cl_main():
    from kigadgets import __version__, pcbnew_version
    vkga = 'kigadgets v{}'.format(__version__)
    vpcb = 'pcbnew    v{}'.format(pcbnew_version(asstr=True))
    verz = vkga + '\n' + vpcb
    parser.add_argument("-v", "--version", action="version", version=verz)
    args = parser.parse_args()
    create_link(args.pcbnew_module_path, args.kicad_config_path, dry_run=args.dry_run)
