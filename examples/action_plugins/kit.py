import os, sys
import subprocess
import mousebite_kigadget

src_dir = os.path.join(os.path.dirname(__file__), 'tests', 'src_layouts')

script_file = os.path.join(mousebite_kigadget.__path__[0], 'mousebite_script.py')
src_file = os.path.join(src_dir, 'mousebite_api.kicad_pcb')
out_file = os.path.join(src_dir, 'mousebite_api-proc.kicad_pcb')
assert os.path.isfile(script_file)
assert os.path.isfile(src_file)

src_file = os.path.relpath(src_file)

script = ['python', script_file, src_file]
# script = ['touch', out_file]
# cmd = "python mousebite_kigadget/mousebite_script.py tests/src_layouts/mousebite_api.kicad_pcb"
cmd = f"python {script_file} {src_file}"
script = cmd.split(' ')
print(script)

completed_process = subprocess.run(script, capture_output=True)
if completed_process.returncode != 0:
    print(completed_process.stderr.decode())
    raise RuntimeError('Script failed')
# assert os.path.isfile(out_file)
# return out_file

# print(cmd)

# subprocess.run(cmd, capture_output=True)
