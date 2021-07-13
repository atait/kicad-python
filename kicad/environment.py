''' Automatic linker to pcbnew GUI and pcbnew python package
    Use this one time to create the link.

    Copy-paste the argument from pcbnew terminal.

    1. Run this in pcbnew's terminal window::

    print('link_kicad_python_to_pcbnew', pcbnew.__file__, pcbnew.GetKicadConfigPath())

    Copy the output. It should look something like::

    link_kicad_python_to_pcbnew /usr/lib/python3/dist-packages/pcbnew.py /home/atait/.config/kicad

    2. Paste and run what you copied into command line from an environment where you have installed this package
'''
import os, sys
import argparse

# Tells pcbnew application where to find this package
plugin_script = """
''' Initialization plugin '''
import sys, pcbnew
sys.path.append("{}")
from kicad.pcbnew.board import Board
pcb = Board.from_editor()
"""

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
        if os.path.basename(pcbnew_swig_path) != 'pcbnew.py':
            raise EnvironmentError(
                'Incorrect location for \'PCBNEW_PATH\' ({}).'
                ' It should point to a file called pcbnew.py'.format(pcbnew_swig_path))
        if not os.path.isfile(pcbnew_swig_path):
            raise EnvironmentError(
                'Incorrect location for \'PCBNEW_PATH\' ({}).'
                ' File does not exist'.format(pcbnew_swig_path))
    return pcbnew_swig_path


def get_pcbnew_module():
    try:
        return __import__('pcbnew')  # If this works, we are probably in the pcbnew application, and we're done.
    except ImportError:
        pass

    pcbnew_swig_path = get_pcbnew_path()
    if pcbnew_swig_path:
        sys.path.insert(0, os.path.dirname(pcbnew_swig_path))
        pcbnew_bare = __import__('pcbnew')
    else:
        # special case for documentation without pcbnew at all
        spoofing_for_documentation = os.environ.get('KICAD_PYTHON_IN_SPHINX_GENERATION', '0')
        if spoofing_for_documentation == '1':
            class SphinxEnumPhony:
                def __getattr__(self, attr):
                    return 0
            pcbnew_bare = SphinxEnumPhony()
        else:
            # failed to find pcbnew
            raise EnvironmentError(
                'pcbnew is required by kicad-python.'
                ' It gets installed when you install the kicad application, but not necessarily on your python path.'
                '\nSee instructions for how to link them at https://github.com/atait/kicad-python'
            )
            pcbnew_bare = None
    return pcbnew_bare


def create_link(kicad_config_path, pcbnew_module_path):
    # Determine what to put in the plugin
    my_package_path = os.path.dirname(__file__)
    my_search_path = os.path.dirname(my_package_path)
    plugin_contents = plugin_script.format(my_search_path)
    # Determine where to put the plugin
    plugin_dir = os.path.join(kicad_config_path.strip(), 'scripting', 'plugins')
    os.makedirs(plugin_dir, exist_ok=True)
    plugin_file = os.path.join(plugin_dir, 'initialize_kicad_python_plugin.py')
    # Write the plugin
    print('Writing plugin to', plugin_file)
    with open(plugin_file, 'w') as fx:
        fx.write(plugin_contents)

    # Store the location of pcbnew module
    print('Writing pcbnew path to', pcbnew_path_store)
    with open(pcbnew_path_store, 'w') as fx:
        fx.write(pcbnew_module_path.strip())

    # Try it
    get_pcbnew_path()
    print('Successfully linked kicad-python with pcbnew')


parser = argparse.ArgumentParser()
parser.add_argument('kicad_config_path', type=str)
parser.add_argument('pcbnew_module_path', type=str)

def cl_main():
    args = parser.parse_args()
    create_link(args.kicad_config_path, args.pcbnew_module_path)
