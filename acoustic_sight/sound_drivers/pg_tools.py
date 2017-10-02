import logging

import pygame
import numpy

from synth import Synth


logger = logging.getLogger('pg_tools')
logger.setLevel(logging.INFO)


def init_audio(frequency=22050*4, channels=1):
    logger.debug('Initializing PyGame mixer...')
    pygame.mixer.pre_init(frequency, -16, channels, 1024)
    pygame.init()
    logger.info('PyGame mixer initialized: {}'.format(pygame.mixer.get_init()))


def get_samples_array(frequency, oscilations=10):
    sample_rate = pygame.mixer.get_init()[0]
    period = int(round(sample_rate / frequency)) * oscilations
    amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1

    def frame_value(i):
        return amplitude * numpy.sin(2.0 * numpy.pi * frequency * i / sample_rate)

    return numpy.array([frame_value(x) for x in range(0, period)]).astype(numpy.int16)


class PGTone(pygame.mixer.Sound):
    def __init__(self, frequency, volume=.1):
        self.frequency = frequency
        super().__init__(buffer=self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        return get_samples_array(self.frequency)


class PGSynth(Synth):
    def __init__(self, base=440, octaves=3, levels=16, shift=-12):
        pygame.mixer.set_num_channels(levels)
        super().__init__(base=base, octaves=octaves, levels=levels, shift=shift)

    def get_tone(self, frequency):
        return PGTone(frequency)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if value > 0:
            self.tones[key].play(-1)
        else:
            self.tones[key].stop()


def __test():
    from test_run import test_run
    logger.setLevel(logging.DEBUG)
    test_run(init_audio, PGSynth)


if __name__ == "__main__":
    __test()
