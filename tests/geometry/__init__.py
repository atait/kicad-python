import os
# Tell lytest about out layouts
import lytest
# lytest.kdb_xor.run_xor = lytest.kdb_xor.run_xor_pcbnew
lytest.utest_buds.default_file_ext = '.kicad_pcb'
from kigadgets import SWIG_version
lytest.utest_buds.test_root = os.path.join(os.path.dirname(__file__), f'{SWIG_version}.0')


if os.getenv('PYTHONHASHSEED') != '0':
    iprepeat = False
    print('Strings will not hash repeatably')
else:
    iprepeat = True


