import supriya

from logger import logger
from synth import Synth


_pa_state = dict()


def init_audio(*args, **kwargs):
    logger.debug('Starting SuperCollider server...')
    _pa_state['default_server'] = supriya.servertools.Server()
    _pa_state['default_server'].boot()
    logger.info('SuperCollider server started: {}'.format(_pa_state['default_server']))


def stop_audio(*args, **kwargs):
    _pa_state['server'].quit()


def get_tone_synthdef(amplitude=1., frequency=440., gate=1.):
    builder = supriya.synthdeftools.SynthDefBuilder(
        amplitude=amplitude,
        frequency=frequency,
        gate=gate,
    )

    with builder:
        source = supriya.ugentools.SinOsc.ar(
            frequency=builder['frequency'],
        )
        envelope = supriya.ugentools.EnvGen.kr(
            done_action=supriya.synthdeftools.DoneAction.FREE_SYNTH,
            envelope=supriya.synthdeftools.Envelope.asr(),
            gate=builder['gate'],
        )
        source = source * builder['amplitude']
        source = source * envelope
        out = supriya.ugentools.Out.ar(
            bus=(0, 1),
            source=source,
        )

    return builder.build().allocate()


class SCTone:
    def __init__(self, frequency, amplitude=1., gate=1., group=None):
        self._started = False
        self.frequency = frequency

        # Allocate group if not specified
        if group is None:
            group = supriya.servertools.Group().allocate()
            logger.debug('Create dedicated SuperCollider tone group: {}'.format(group))
        self.group = group

        synthdef = get_tone_synthdef(amplitude=amplitude, frequency=frequency, gate=gate)
        self.synth = supriya.servertools.Synth(synthdef)

    def play(self, *args, **kwargs):
        if not self._started:
            self.group.append(self.synth)
            self._started = True
            logger.debug('Pushed tone synth for {frequency} Hz to SuperColider server'
                         .format(frequency=self.frequency))

    def stop(self):
        if self._started:
            self.synth.release()
            self._started = False
            logger.debug('Released tone synth for {frequency} Hz from SuperColider server'
                         .format(frequency=self.frequency))

    def get_volume(self):
        return self.synth['amplitude']

    def set_volume(self, volume):
        self.synth['amplitude'] = volume
        logger.debug('Set {frequency} Hz tone volume to {volume}'.format(frequency=self.frequency, volume=volume))


class SCSynth(Synth):
    def __init__(self, base=440, octaves=3, levels=16, shift=-12, server=None):
        # Allocate server if not specified
        if server is None:
            server = _pa_state['default_server']
            logger.debug('Use default SuperCollider server for SCSynth')
        self.server = server

        # Create group
        self.group = supriya.servertools.Group().allocate()
        logger.debug('Create SCSynth-level SuperCollider tone group: {}'.format(self.group))
        # Sync server
        self.server.sync()

        super().__init__(base=base, octaves=octaves, levels=levels, shift=shift)

    def get_tone(self, frequency):
        logger.debug('Create Tone synth for {} Hz'.format(frequency))
        return SCTone(frequency=frequency, group=self.group)


def __test():
    from test_run import test_run
    test_run(init_audio, SCSynth)


if __name__ == "__main__":
    __test()
