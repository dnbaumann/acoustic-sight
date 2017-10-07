import logging
import time

from logger import logger


def test_run(init_audio, Synth, levels=16):
    logger.setLevel(logging.DEBUG)
    init_audio()

    synth = Synth(levels=levels)
    logger.info('Used frequencies: %s' % synth.frequencies)

    for i in range(len(synth)):
        synth.play(i)
        logger.debug('Turn on {} Hz frequency.'.format(synth.tones[i].frequency))
        time.sleep(.125)

    synth.stop()
    logger.info('Stop all.')
    time.sleep(.5)
