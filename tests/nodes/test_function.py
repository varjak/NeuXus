import sys

import unittest

sys.path.append('neuxus')
sys.path.append('tests/nodes')

from utils import (INDEX, COLUMN, simulate_loop_and_verify)
from chunks import Port
from nodes.function import ApplyFunction


class TestFunction(unittest.TestCase):

    def test_apply_function(self):
        # create a Port and a Node
        port = Port()
        port.set_parameters(
            data_type='signal',
            channels=COLUMN,
            sampling_frequency=250,
            meta={})
        node = ApplyFunction(port, lambda x: x**2)

        # simulate NeuXus loops
        simulate_loop_and_verify(port, node, self)
