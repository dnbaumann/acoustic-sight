import logging
import time


logger = logging.getLogger('test_run')
logger.setLevel(logging.DEBUG)


def test_run(init_audio, Synth):
    init_audio()

    synth = Synth(levels=16)
    logger.info('Used frequencies: %s' % synth.frequencies)

    for i in range(len(synth)):
        synth.play(i)
        time.sleep(.125)

    synth.stop()
    logger.info('Stop all.')
    time.sleep(.5)
