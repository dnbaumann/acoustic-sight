from logger import logger


def get_frequencies(base=440, octaves=3, levels=16, shift=-12):
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
        self.levels = levels
        self.tones = [None] * self.levels
        self.frequencies = get_frequencies(base, octaves, self.levels, shift)

        for i in range(self.levels):
            self.tones[i] = self.get_tone(self.frequencies[i])
        logger.info('All tones initialized.')

    def play(self, tone=None):
        if tone is not None:
            self.tones[tone].play(-1)
            logger.debug('Start to play {} Hz tone.'.format(self.tones[tone].frequency))
        else:
            for t in range(len(self.tones)):
                self.play(t)
            logger.info('All tones are ready and playing.')

    def stop(self, tone=None):
        if tone is not None:
            self.tones[tone].stop()
            logger.debug('Stop to play {} Hz tone.'.format(self.tones[tone].frequency))
        else:
            for t in range(len(self.tones)):
                self.stop(t)
            logger.info('All tones stopped.')

    def get_tone(self, frequency):
        raise NotImplemented

    def sync(self):
        pass

    def __getitem__(self, item):
        return self.tones[item].get_volume()

    def __setitem__(self, key, value):
        self.tones[key].set_volume(value)

    def __len__(self):
        return len(self.tones)

    def __del__(self):
        self.stop()
