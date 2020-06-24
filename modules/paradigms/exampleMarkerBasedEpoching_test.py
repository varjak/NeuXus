import sys
import numpy as np

sys.path.append('.')
sys.path.append('../..')

from modules.core.pipeline import run
from modules.nodes import *


if __name__ == '__main__':

    # initialize the pipeline
    #lsl_marker_reception = io.LslReceive('type', 'Markers')
    #lsl_reception = io.LslReceive('name', 'LiveAmpSN-054207-0168')
    #lsl_reception = io.LslReceive('name', 'LiveAmpSN-054207-0168', sync='network')
    lsl_reception = io.LslReceive('type', 'EEG')
    #lsl_reception = io.LslReceive('name', 'openvibeSignal')
    lsl_marker_reception = io.LslReceive('name', 'openvibeMarkers')
    #lsl_reception = io.LslReceive('name', 'openvibeSignalLSL')

    #reref = select.ReferenceChannel(lsl_reception.output, 'index', 1)
    reref = select.CommonAverageReference(lsl_reception.output)

    chans = select.ChannelSelector(reref.output, 'index', [1, 2, 3, 4])

    matrix = {
            'OC2': [4, 0, -1, 0],
            'OC3': [0, -1, 2, 4]}
    laplacian_filter =  select.SpatialFilter(chans.output, matrix)

    butter_filter = filter.ButterFilter(chans.output, 8, 12)

    time_epoch = epoching.TimeBasedEpoching(butter_filter.output, 0.5, 1)
    square_epoch = function.ApplyFunction(time_epoch.output, lambda x: x**2)
    average_epoch = epoch_function.Average(square_epoch.output)

    log_epoch = function.ApplyFunction(time_epoch.output, lambda x: np.log1p(x))

    baseline = epoching.StimulationBasedEpoching(average_epoch.output, lsl_marker_reception.output, 800, 0.025, 3)


    baseline_average = epoch_function.Average(baseline.output)

    def relative_alpha(x):
        return (x - baseline_average.value) / baseline_average.value * 100

    relative_band = function.ApplyFunction(average_epoch.output, relative_alpha)


    lsl_send0 = io.LslSend(time_epoch.output, 'time_epoch')
    lsl_send1 = io.LslSend(square_epoch.output, 'square_epoch')
    lsl_send2 = io.LslSend(average_epoch.output, 'average_epoch_n')
    lsl_send3 = io.LslSend(log_epoch.output, 'log_epoch')
    lsl_send4 = io.LslSend(relative_band.output, 'relative_band')
    lsl_send5 = io.LslSend(laplacian_filter.output, 'laplacian_filter')


    # run the pipeline
    run()
