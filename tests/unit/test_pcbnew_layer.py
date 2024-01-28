import unittest

from kigadgets.layer import LayerSet


TEST_LAYER_LIST = ['F.Cu', 'B.Cu', ]


class TestPcbnewLayerSet(unittest.TestCase):
    def test_layer_names(self):
        layer_set = LayerSet(TEST_LAYER_LIST)
        self.assertEqual(sorted(layer_set.layers),
                         sorted(TEST_LAYER_LIST))
