''' Do you hate the pcbnew console? Me too.
    This script can be run at the press of a button in the Pcbnew GUI. Great for semi-interactive coding
    It uses a plugin entry point, which can be hotkeyed.

    Usage:
    - write stuff below
    - in Pcbnew, press Cmd+Enter

    Use as a library:
    Run this in the pcbnew shell. Sometimes it is needed for every file change.

        import onepush_script; from onepush_script import reload; reload(onepush_script); from onepush_script import *

    Setup:
    1) register an entry point. I have already done this for you. It's called onepush_plugin.py
        - it is an external plugin and should show up in your Pcbnew menu
        - it just has to register the right name and find this file
    2) shortcut it in System Preferences (OSX)
        - keyboard > shortcuts
        - pick Application shortcuts from the menu
        - hit plus button, scroll to "Other..." at the bottom of the dropdown menu
        - find "kicad.app" within the KiCAD folder
        - enter the menu item name (One Push) and key combo (for me, Cmd+Enter)
        - repeat for the "pcbnew.app" in case you run that as standalone

    Notes:
    The python kernel persists while Pcbnew is open.
    - if you import another module, it will not run again.
    - attributes changed in that module will not reset.
    - if you had edited that module, stuff can get weird.
    - to reinit that module, use "reload(that_module)"
    The entry point will reload this script, thus reinitializing and running it every time
'''
from kigadgets import notify
import sys
import time
import pcbnew
from kigadgets.board import Board
# pcb = Board.from_editor()

def default():
    notify(
        'This is kigadgets, the one-push macro script. '
        'Edit the script directly at \n\n{}\n\n'
        'Use it to develop your own code without '
        'having to restart pcbnew every time.'.format(__file__)
    )
# default()  # Comment this line when ready to run your own code below


### the most basic test that paths and links and board loading are working correctly
def hello_world():
    # notify("One push hello world")
    from kigadgets.drawing import TextPCB
    pcb = Board.from_editor()
    full_text = 'One push hello world'
    pcb_text = TextPCB((0, 0), '')
    pcb.add(pcb_text)
    pcb_text.justification = 'left'
    for i in range(len(full_text)):
        pcb_text.text = full_text[:i]
        pcbnew.Refresh()
        time.sleep(0.1)
    pcb_text.x += (len(full_text) - 1) * pcb_text.size[0]
    pcb_text.justification = 'right'
    for i in range(1, len(full_text)+1):
        pcb_text.text = full_text[i:]
        pcb_text.thickness *= .9
        pcbnew.Refresh()
        time.sleep(0.1)
    time.sleep(1)
    pcb.remove(pcb_text)
    pcbnew.Refresh()
hello_world()

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

#### some tests of kigadgets

# Verify autoreloading
def test_autoreload():
    pcb = Board.from_editor()
    try:
        notify(pcb.temporary_attribute)
    except AttributeError:
        notify(
'''
Add the attribute to kigadgets.board:Board at this line,
then rerun this script to see if the library has been reloaded.
(It depends on your version of KiCAD):

class Board(object):
    temporary_attribute = 'hey there'
    def __init__(self, wrap=None):
'''
        )
# test_autoreload()

# get a module already present and move it
def move_footprint():
    pcb = Board.from_editor()
    mod = pcb.moduleByRef('D1')
    mod.position = (50, 30)
# move_footprint()

''' Other examples:
# add test track with via
track1 = [(30, 26), (30, 50), (60, 80)]
track2 = [(60, 80), (80, 80)]
pcb.add_track(track1, layer='F.Cu', width=0.25)
pcb.add_track(track2, layer='B.Cu')
from kicad.pcbnew.via import Via
pcb.add(Via(track1[-1], ['F.Cu', 'B.Cu'], 1, .5, board=pcb))

# add board edge
ul = (20, 20)
pcb_size = (100, 80)
edge = [ul,
        (ul[0], ul[1]+pcb_size[1]),
        (ul[0]+pcb_size[0], ul[1]+pcb_size[1]),
        (ul[0]+pcb_size[0], ul[1]),
        ul]
pcb.add_polyline(edge, layer='Edge.Cuts')

def probing():
    from kigadgets.drawing import ShapeType
    pcb = Board.from_editor()
    debug = ''
    sel = list(pcb.selected_items)
    if len(sel) != 1:
        notify('Needs one thing selected')
        return
    for item in sel:
        obj = item.native_obj

    item.fillet(1)
    # pcbnew.Refresh()
    return

    # obj.SetShape(ShapeType.Polygon)
    # poly = obj.GetPolyShape()
    # smoothed = poly.Fillet(int(radius_mm * units.DEFAULT_UNIT_IUS), int(tol_mm * units.DEFAULT_UNIT_IUS))
    # obj.SetPolyShape(smoothed)
    # debug_list = [d for d in dir(obj) if 'T' in d]
    # debug = '\n'.join(debug_list)
    notify(debug)
# probing()
'''

#### Reload main window
pcbnew.Refresh()

# time.sleep(2)

# for elem in removed:
#     pcb.add(elem)
# pcbnew.Refresh()


