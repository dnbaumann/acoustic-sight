import math

import numpy
import pygame

from sonification.synth import Synth
from sonification.tools import get_logger


logger = get_logger('pg_tools')


def init_audio(frequency=22050*4, channels=1):
    logger.debug('Initializing PyGame mixer...')
    pygame.mixer.pre_init(frequency, -16, channels, 1024)
    pygame.init()
    logger.info('PyGame mixer initialized: {}'.format(pygame.mixer.get_init()))


def get_max_amplitude():
    bits_per_sample = abs(pygame.mixer.get_init()[1])
    return 2 ** (bits_per_sample - 1) - 1


def get_tone_samples_array(frequency, repeat=10, time_shift=0.):
    period = 1. / frequency
    sample_rate = pygame.mixer.get_init()[0]
    frame_size = math.floor(sample_rate * repeat * period)
    frame_period = repeat * period
    time_vector = numpy.linspace(start=time_shift, stop=time_shift+frame_period, num=frame_size)

    max_amplitude = get_max_amplitude()

    signal = numpy.sin(time_vector * 2 * numpy.pi * frequency) * max_amplitude

    return signal.astype(numpy.int16)


class PGTone(pygame.mixer.Sound):
    def __init__(self, frequency, volume=.1):
        self.frequency = frequency
        super().__init__(buffer=self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        return get_tone_samples_array(self.frequency)


class PGSynth(Synth):
    def __init__(self, base=440, octaves=3, levels=16, shift=-12):
        pygame.mixer.set_num_channels(levels)
        super().__init__(base=base, octaves=octaves, levels=levels, shift=shift)

    def get_tone(self, frequency):
        return PGTone(frequency=frequency, volume=1/self.levels)


def __test():
    from test_run import test_run
    test_run(init_audio, PGSynth)


if __name__ == "__main__":
    __test()
