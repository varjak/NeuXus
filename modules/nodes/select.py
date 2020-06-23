import sys

import pandas as pd

sys.path.append('.')
sys.path.append('../..')

from modules.core.node import Node


class ChannelSelector(Node):
    """Select a subset of signal channels
    Attributes:
     - output (port): output port
    Args:
     - mode ('index' or 'name'): indicate the way to select data
     - selected (list): column to be selected

    example: ChannelSelector(port1, port2, 'index', [2, 4, 5])
          or ChannelSelector(port1, port2, 'name', ['Channel 2', 'Channel 4'])

    """

    def __init__(self, input_port, mode, selected):
        Node.__init__(self, input_port)

        assert mode in ['index', 'name']

        # get channels
        if mode == 'index':
            self._channels = [self.input.channels[i - 1] for i in selected]
        elif mode == 'name':
            self._channels = selected

        self.output.set_parameters(
            channels=self._channels,
            frequency=self.input.frequency,
            meta=self.input.meta)

    def update(self):
        for chunk in self.input:
            self.output.set_from_df(chunk[self._channels])


class SpatialFilter(Node):
    """Maps M inputs to N outputs by multiplying the each input vector with a matrix
    usually used after a ChannelSelector
    Attributes:
     - output (port): output GroupOfPorts
    Args:
     - input (port): input port
     - matrix (dict): dictionnary with new channel name as keys and list of coefficients as values,
       list must be of the same length as input.channels

    example: SpatialFilter(input_port, matrix)
    where matrix = {
        'OC2': [4, 0, -1, 0],
        'OC3': [0, -1, 2, 4]
    }

    """

    def __init__(self, input_port, matrix):
        Node.__init__(self, input_port)

        # protected
        self._matrix = matrix
        self._channels = [*self._matrix.keys()]

        # verify that the size of _matrix is correct
        for chan in self._channels:
            assert len(self._matrix[chan]) == len(self.input.channels)

        self.output.set_parameters(
            channels=self._channels,
            frequency=self.input.frequency,
            meta=self.input.meta)

    def update(self):
        for chunk in self.input:
            df = pd.DataFrame([])
            for chan in self._channels:
                flag = True  # use to first create the serie
                for index, coef in enumerate(self._matrix[chan]):
                    # print(f'{index} columns with coef {coef}')
                    if flag:
                        serie = chunk.iloc[:, index] * coef
                        flag = False
                    else:
                        serie += chunk.iloc[:, index] * coef
                df[chan] = serie
            self.output.set_from_df(df)


class ReferenceChannel(Node):
    """Subtracts the value of the reference channel from all other channels
    Attributes:
     - output (port): output GroupOfPorts
    Args:
     - mode ('index' or 'name'): indicate the way to select data
     - reference channel (str or int): column to be substracted

    example: ReferenceChannel(input_port, 'index', 4)
          or ReferenceChannel(input_port, 'name', 'Cz')

    """

    def __init__(self, input_port, mode, ref):
        Node.__init__(self, input_port)

        assert mode in ['index', 'name']

        # get reference channel name
        if mode == 'index':
            self._ref = self.input.channels[ref - 1]
        elif mode == 'name':
            self._ref = ref

        self._channels = self.input.channels.copy()
        self._channels.remove(self._ref)

        self.output.set_parameters(
            channels=self._channels,
            frequency=self.input.frequency,
            meta=self.input.meta)

    def update(self):
        for chunk in self.input:
            df = pd.DataFrame([])
            to_substract = chunk.loc[:, self._ref]
            for chan in self._channels:
                df[chan] = chunk.loc[:, chan] - to_substract
            self.output.set_from_df(df)


class CommonAverageReference(Node):
    """Re-referencing the signal to common average reference consists in
    subtracting from each sample the average value of the samples of all
    electrodes at this time
    Attributes:
     - output (port): output GroupOfPorts

    example: CommonReferenceChannel(input_port)

    """

    def __init__(self, input_port):
        Node.__init__(self, input_port)

        self.output.set_parameters(
            channels=self.input.channels,
            frequency=self.input.frequency,
            meta=self.input.meta)

    def update(self):
        for chunk in self.input:
            to_substract = chunk.mean(axis=1)
            df = pd.DataFrame([])
            for chan in self.input.channels:
                df[chan] = chunk.loc[:, chan] - to_substract
            self.output.set_from_df(df)