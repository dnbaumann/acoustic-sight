import pyaudio
import numpy

from logger import logger
from synth import Synth, get_frequencies


_state = dict()


def init_audio(bitrate=96000, channels=1):
    logger.debug('Initializing PyGame mixer...')
    _state['pyaudio'] = pyaudio.PyAudio()
    _state['bitrate'] = bitrate
    _state['channels'] = channels
    logger.info('PyAudio initialized: {}'.format(_state))


def stop_audio(*args, **kwargs):
    _state['pyaudio'].terminate()


class PATone:
    def __init__(self, frequency, amplitude, on=True):
        self.frequency = frequency
        self.amplitude = amplitude
        self.on = on


class PAMultiTone:
    def __init__(self, frequencies, volume=.1):
        self.tones = [PATone(frequency=f, amplitude=volume) for f in frequencies]
        self.volume = volume

        self.stream = self._get_stream()

    def _get_stream(self):
        def stream_callback(in_data, frame_count, time_info, status):
            return self._get_samples(frame_count, time_info['output_buffer_dac_time']), pyaudio.paContinue

        return _state['pyaudio'].open(
            format=pyaudio.paFloat32,
            channels=_state['channels'],
            rate=_state['bitrate'],
            output=True,
            stream_callback=stream_callback,
        )

    def _init_sine_components(self, frame_count, time_base):
        sample_rate = _state['bitrate']
        period = 1 / sample_rate * frame_count
        time_vector = numpy.linspace(start=time_base, stop=time_base+period, num=frame_count)

        components = dict()
        for t in self.tones:
            components[t.frequency] = (numpy.sin(time_vector * 2 * numpy.pi * t.frequency) + 1) / 2
            logger.debug('Generate {} Hz component'.format(t.frequency))

        return components

    def _get_samples(self, frame_count, time_base):
        components = self._init_sine_components(frame_count, time_base)

        signal = numpy.zeros(frame_count)
        for t in self.tones:
            if t.on is True:
                signal = signal + components[t.frequency] * t.amplitude
                logger.debug('Add amplified {} Hz component'.format(t.frequency))

        signal = signal / (len(self.tones) ** .5) * self.volume

        return signal.astype(numpy.float32)

    def play(self):
        for t in self.tones:
            t.on = True

        self.stream.start_stream()

    def stop(self):
        self.stream.stop_stream()

    def set_amplitude(self, key, value):
        self.tones[key].amplitude = value

    def get_amplitude(self, key):
        return self.tones[key].amplitude

    def play_tone(self, key):
        self.tones[key].on = True

    def stop_tone(self, key):
        self.tones[key].on = False

    def __getitem__(self, item):
        return self.tones[item]

    def __len__(self):
        return len(self.tones)

    def __del__(self):
        self.stream.close()


class PASynth(Synth):
    def __init__(self, base=440, octaves=3, levels=16, shift=-12):
        self.levels = levels
        self.tones = [None] * self.levels
        self.frequencies = get_frequencies(base, octaves, self.levels, shift)

        self.tones = PAMultiTone(self.frequencies)

    def play(self, key=None):
        if key is not None:
            self.tones.play_tone(key)
            logger.debug('Start to play {} tone.'.format(self.tones[key]))
        else:
            self.tones.play()
            logger.info('All tones are ready and playing.')

    def stop(self, key=None):
        if key is not None:
            self.tones.stop_tone(key)
            logger.debug('Stop to play {} tone.'.format(self.tones[key]))
        else:
            self.tones.stop()
            logger.info('All tones stopped.')

    def __getitem__(self, item):
        return self.tones.get_volume(item)

    def __setitem__(self, key, value):
        self.tones.set_volume(key, value)

    def __len__(self):
        return len(self.tones)

    def __del__(self):
        self.stop()


def __test():
    from test_run import test_run
    test_run(init_audio, PASynth)


if __name__ == "__main__":
    __test()
