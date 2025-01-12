''' Are you tired of the pcbnew GUI terminal? Me too.
    This script can be run at the press of a button (or hotkey) in the Pcbnew GUI.
    Great for semi-interactive coding.

    Do not edit this example file. Edit onepush_script.py instead.

    Setup:
    1) copy the parent directory "onepush" to your KiCad user config folder
        Mac: usually ~/Documents/KiCad/V.V/scripting/plugins
        Linux: usually ~/.config/kicad/V.V/scripting/plugins
        Windows: usually ~/Documents/KiCad/V.V/scripting/plugins
    2*) register an entry point
        - *I have already done this for you in action_onepush.py
        - You only need to reload the action plugin menu, or restart Pcbnew.app
    3) shortcut menu item in System Preferences (OSX instructions)
        - Keyboard > Shortcuts > Application Shortcuts
        - pick Application shortcuts from the menu
        - hit plus button, scroll to "Other..." at the bottom of the dropdown menu
        - find "kicad.app" within the KiCad folder
        - enter the menu item name (One Push) and key combo (for me, Shift+Cmd+R)
            - It must match the menu item name exactly (One Push)!
        - repeat hotkeying for the "pcbnew.app" in case you run that as standalone

    Notes:
    The python kernel persists while Pcbnew is open.
    - module attributes will not reset.
    The action plugin entry point (action_onepush.py) will reload this script,
    thus reinitializing and running it every time
    - if you import another module, it will not reload any code changes
    - to reinit that module, use "kireload(that_module)"
'''
import kigadgets
from kigadgets import notify, kireload
import time
import os
import pcbnew
from kigadgets.board import Board

def default():
    home = os.path.expanduser("~")
    file_path = __file__.replace(home, "~")
    notify(
        'This is kigadgets, the one-push macro script. '
        'Edit the script directly at \n\n{}\n\n'
        'Use it to develop your own code without '
        'having to restart pcbnew every time.'
        'See that file for premade examples'.format(file_path)
    )
# default()  # Comment this line when ready to run your own code below

def hello_world():
    full_text = 'kigadgets hola world'

    from kigadgets.drawing import TextPCB
    pcb = Board.from_editor()
    pcb_text = TextPCB((0, 0), '', justification='left')
    pcb.add(pcb_text)
    for i in range(len(full_text)):
        pcb_text.text = full_text[:i]
        pcbnew.Refresh()
        time.sleep(0.1)
    pcb_text.x += (len(full_text) - 1) * pcb_text.size[0]*.85
    pcb_text.justification = 'right'
    for i in range(1, len(full_text)+1):
        pcb_text.text = full_text[i:]

        # pcb_text.thickness *= .9
        pcb_text.size = (
            pcb_text.size[0] * 1.02,
            pcb_text.size[1] * .96
        )

        pcbnew.Refresh()
        time.sleep(0.1)
    time.sleep(1)
    pcb.remove(pcb_text)
    pcbnew.Refresh()
# hello_world()


# --- Simple editing examples

def move_footprint():
    # get a module already present and move it
    pcb = Board.from_editor()
    mod = pcb.moduleByRef('D1')
    mod.position = (50, 30)
    pcbnew.Refresh()
# move_footprint()

def some_tracks():
    # add test track with via
    pcb = Board.from_editor()
    track1 = [(30, 26), (30, 50), (60, 80)]
    track2 = [(60, 80), (80, 80)]
    pcb.add_track(track1, layer='F.Cu', width=0.25)
    pcb.add_track(track2, layer='B.Cu')
    from kigadgets.via import Via

    my_via = Via(track1[-1], ['F.Cu', 'B.Cu'], 1, .5)
    pcb.add(my_via)

    # add board edge
    ul = (20, 20)
    pcb_size = (100, 80)
    edge = [ul,
            (ul[0], ul[1]+pcb_size[1]),
            (ul[0]+pcb_size[0], ul[1]+pcb_size[1]),
            (ul[0]+pcb_size[0], ul[1]),
            ul]
    pcb.add_polyline(edge, layer='Edge.Cuts')
    pcbnew.Refresh()
# some_tracks()

def probe_item():
    ''' Get a single item selected in the PCB and experiment with it
    '''
    # Some very basic object exposure
    pcb = Board.from_editor()
    if len(pcb.selected_items) != 1:
        notify('Needs one thing selected')
        return
    this_item = pcb.selected_items[0]
    this_swig_obj = this_item.native_obj

    # Then do your experiments here

    attributes = [attr for attr in dir(this_swig_obj) if not attr.startswith('__')]
    attr_grouped = []
    for i in range(0, len(attributes), 4):
        attr_grouped.append(' , '.join(attributes[i:i+4]))
    attr_grouped.extend(attributes[i:])
    attr_str = '\n'.join(attr_grouped)
    message = f'''
This {this_swig_obj.__class__}
(wrapped by {this_item.__class__}) has attributes:
{attr_str}
'''
    notify(message)
    try:
        this_item.fillet(5)
    except AttributeError:
        notify('This item does not have a fillet method')
    pcbnew.Refresh()
# probe_item()


# --- Low-level tests of kigadgets

# Verify autoreloading
def test_autoreload():
    ''' Say you are developing a library dependency somewhere else.
        It does not get auto-reloaded along with onepush. This example uses kigadgets to demonstrate this.
    '''
    kireload(kigadgets)  # This is the key line. Should work on
    pcb = Board.from_editor()
    try:
        notify('Success with pcb.temporary_attribute =', pcb.temporary_attribute)
    except AttributeError:
        notify(
'''
Add the attribute to kigadgets.board:Board at this line,
then rerun this script to see if the library has been reloaded.
(It depends on your version of KiCad):

class Board(object):
    temporary_attribute = 'hey there'
    def __init__(self, wrap=None):
'''
        )
# test_autoreload()

n_errors = 10
def crawl_API(base=None, regex='Get', levels=2):
    global n_errors
    import re
    if levels == 0:
        return []
    if base is None:
        base = pcbnew
    regex = regex.lower()
    # notify('Crawling', str(base))
    meth_arr_str = dir(base)
    # filtered = [m for m in meth_arr_str if re.match(regex, m) is not None]
    filtered = [m for m in meth_arr_str if regex in m.lower() and not m.startswith('__')]
    methods = []
    variables = []
    error_attr = []
    for meth_str in meth_arr_str:
        if meth_str.startswith('__'):
            continue
        try:
            member = getattr(base, meth_str)
        except AttributeError:
            error_attr.append(meth_str)
            continue
        # if isinstance(member, type):
        #     pass
        # elif callable(member):
        #     methods.append((meth_str, member))
        # else:
        #     variables.append((meth_str, member))
        if hasattr(member, '__dict__'):
            methods.append(member)
    # return filtered
    print(len(methods), flush=True)
    error_call = []
    modules = {}
    more_methods = []
    more_variables = []
    for meth in methods:
        for k, v in meth.__dict__.items():
            if hasattr(v, '__dict__'):
                modules[k] = v
            else:
                variables.append(k)
        if callable(meth) and False:
            try:
                ret = meth()
            except TypeError:  # method needs arguments
                continue
            except Exception:
                error_call.append((meth))
                print('Error in call', meth, type(meth))
                if n_errors == 0:
                    raise
                n_errors -= 1
                continue
            if callable(ret):
                more_methods.append(ret)
            elif hasattr(ret, '__dict__'):
                modules.append(ret)
            else:
                more_variables.append((meth, ret))
    print('mods', len(modules), 'var', len(variables))
    # sub_filtered = []
    # for name, mod in modules.items():
    #     submembers = crawl_API(mod, regex, levels-1)
    #     subrename = [name + '.' + memstr for memstr in filtered + sub_filtered]
    #     filtered.extend(subrename)
    return filtered
# notify('\n'.join(crawl_pcbnew_API(regex='SHAPE')))


