import unittest

from kicad.pcbnew.layer import *


TEST_LAYER_LIST = ['F.Cu', 'B.Cu', ]


class TestPcbnewLayerSet(unittest.TestCase):
    def test_layer_names(self):
        layer_set = LayerSet(TEST_LAYER_LIST)
        self.assertEqual(sorted(layer_set.layer_names),
                         sorted(TEST_LAYER_LIST))

    def test_layer_ids(self):
        layer_set = LayerSet(TEST_LAYER_LIST)
        self.assertEqual(len(layer_set.layers), len(TEST_LAYER_LIST))
