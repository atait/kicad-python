import os
import sys
from lytest.utest_buds import get_src_dir
from lytest import contained_pcbnewBoard, contained_script, difftest_it
import subprocess

import mousebite_kigadget
import mousebite_kigadget.mousebite_script as mbcore


@contained_pcbnewBoard#(infile='mousebite_source.kicad_pcb')
def mousebite_api(pcb):
    mbcore.main(pcb, dialog_opts=None)

def test_mousebite_api(): difftest_it(mousebite_api)()


@contained_script
def mousebite_cli():
    script_file = os.path.join(mousebite_kigadget.__path__[0], 'mousebite_script.py')
    slayarg = '-s User.Eco2' if False else None
    src_file = os.path.join(get_src_dir(), 'mousebite_api.kicad_pcb')
    out_file = os.path.join(get_src_dir(), 'mousebite_api-proc.kicad_pcb')
    assert os.path.isfile(script_file)
    assert os.path.isfile(src_file)

    script = [sys.executable, script_file, src_file]
    print(script)
    # if False:
    #     script.insert(2, '--slay=User.Eco2')
    completed_process = subprocess.run(script, capture_output=True)
    if completed_process.returncode != 0:
        print(completed_process.stderr.decode())
        raise RuntimeError('Script failed')
    assert os.path.isfile(out_file)
    return out_file

def test_mousebite_cli(): difftest_it(mousebite_cli)()
