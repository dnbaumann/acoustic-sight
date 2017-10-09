import logging
import time

from logger import logger


def test_run(init_audio, Synth, levels=16, interval=.125, await=.5):
    logger.setLevel(logging.DEBUG)
    init_audio()

    synth = Synth(levels=levels)
    logger.info('Used frequencies: %s' % synth.frequencies)

    for i in range(len(synth)):
        synth.play(i)
        logger.debug('Turn on {} Hz frequency.'.format(synth.tones[i].frequency))
        time.sleep(interval)

    time.sleep(await)

    synth.stop()
    logger.info('Stop all.')
