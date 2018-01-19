import logging
import math

from acoustic_sight import sound_drivers
from acoustic_sight import hilbert_curve
from acoustic_sight.tools import TimeMeasurer, get_logger


class Sonificator:
    def __init__(self, side_in, octaves=3, shift=-18, synth_type=sound_drivers.SUPER_COLLIDER,
                 volume_type='linear', max_volume=.5, logger=None, log_level=logging.INFO,
                 profile=False,
                 ):
        self.volume_type = volume_type
        self.max_volume = max_volume

        if profile:
            if logger is None:
                self.logger = get_logger('Sonificator', level=log_level)
            else:
                self.logger = logger

            self.time_measurer = TimeMeasurer(self.logger)
            self.time_measurer.decorate_method(self, self.sonify, 'Sonified')

        Synth, init_audio = sound_drivers.get_driver(synth_type)

        init_audio()
        self.synth = Synth(levels=side_in*side_in, octaves=octaves, shift=shift)
        self.synth.play()

    def sonify(self, arr):
        vec = hilbert_curve.hilbert_expand(arr)
        for i in range(len(vec)):
            if self.volume_type == 'linear':
                self.synth[i] = vec[i] / 255 * self.max_volume
            elif self.volume_type == 'threshold':
                self.synth[i] = (vec[i] > 127) * 1.
            elif self.volume_type == 'exp':
                self.synth[i] = (math.exp(vec[i] / 255) - 1) / (math.exp(1) - 1) * self.max_volume
        self.synth.sync()

    def silence(self):
        self.synth.silence()
