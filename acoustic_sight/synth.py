from time import sleep

import pygame
import numpy


def init(frequency=22050*4, channels=1):
    pygame.mixer.pre_init(frequency, -16, channels, 1024)
    pygame.init()


def get_samples_array(frequency, oscilations=10):
    sample_rate = pygame.mixer.get_init()[0]
    period = int(round(sample_rate / frequency)) * oscilations
    amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1

    def frame_value(i):
        return amplitude * numpy.sin(2.0 * numpy.pi * frequency * i / sample_rate)

    return numpy.array([frame_value(x) for x in range(0, period)]).astype(numpy.int16)


class Note(pygame.mixer.Sound):
    def __init__(self, frequency, volume=.1):
        self.frequency = frequency
        super().__init__(buffer=self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        return get_samples_array(self.frequency)


def get_frequencies(base, octaves, levels, shift=-12):
    a = 2 ** (1/12)

    def freq(n):
        return base * a ** n

    step = octaves * 12 / levels
    frequences = [None] * levels

    for l in range(levels):
        frequences[l] = freq(step * l + shift)

    return frequences


class Synth:
    def __init__(self, base=440, octaves=3, levels=16, shift=-12):
        pygame.mixer.set_num_channels(levels)

        self.notes = [None]*levels
        self.frequencies = get_frequencies(base, octaves, levels, shift)

        for i in range(levels):
            self.notes[i] = Note(self.frequencies[i])

    def play(self, note=None):
        if note is not None:
            self.notes[note].play(-1)
        else:
            for note in self.notes:
                note.play(-1)

    def stop(self, note=None):
        if note is not None:
            self.notes[note].stop()
        else:
            for note in self.notes:
                note.stop()

    def __getitem__(self, item):
        return self.notes[item].get_volume()

    def __setitem__(self, key, value):
        self.notes[key].set_volume(value)
        if value > 0:
            self.notes[key].play(-1)
        else:
            self.notes[key].stop()

    def __len__(self):
        return len(self.notes)


def __test():
    init()

    synth = Synth(levels=16)
    print(synth.frequencies)

    for i in range(len(synth)):
        synth.play(i)
        print('Play %s Hz.' % synth.frequencies[i])
        sleep(.125)

    synth.stop()
    print('Stop all.')
    sleep(.5)


if __name__ == "__main__":
    __test()
