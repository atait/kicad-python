import os
if os.getenv('PYTHONHASHSEED') != '0':
    iprepeat = False
    print('Strings will not hash repeatably')
else:
    iprepeat = True

if iprepeat:
    def test_repeatable_str():
        from kigadgets.via import Via
        via = Via((20, 20))
        assert via.geohash() == 1551763526998012866

# Tell lytest about out layouts
import lytest
# lytest.kdb_xor.run_xor = lytest.kdb_xor.run_xor_pcbnew
lytest.utest_buds.default_file_ext = '.kicad_pcb'
lytest.utest_buds.test_root = os.path.dirname(__file__)
