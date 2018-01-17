import numpy as np
import numpy.fft as fft
import pyaudio
from collections import deque

from acoustic_sight.synth import Synth, get_frequencies
from acoustic_sight.tools import get_logger


logger = get_logger('pa_tools')


class PAState:
    def __init__(self, pa_instance: pyaudio.PyAudio, bitrate: int, channels: int):
        self.pa_instance = pa_instance
        self.bitrate = bitrate
        self.channels = channels


_pa_state: PAState = None


FFT = 'fft'
RFFT = 'rfft'


def init_audio(bitrate=96000, channels=1):
    logger.debug('Initializing PyGame mixer...')
    global _pa_state
    _pa_state = PAState(pyaudio.PyAudio(), bitrate, channels)
    logger.info('PyAudio initialized: {}'.format(_pa_state))


def stop_audio(*args, **kwargs):
    _pa_state.pa_instance.terminate()


def get_frequency_space(frame_size, sample_rate, fft_type=RFFT):
    if fft_type == RFFT:
        freq_function = fft.rfftfreq
    elif fft_type == FFT:
        freq_function = fft.fftfreq
    else:
        raise ValueError('Unsupported FFT type: %s.' % fft_type)

    return freq_function(frame_size, 1 / sample_rate)


def check_frequencies_order(frequencies):
    last_freq = frequencies[0]
    for f in frequencies:
        if f < last_freq:
            raise ValueError('Frequencies passed in non-ascendant order: {last_freq} id followed by {f}'
                             .format(last_freq=last_freq, f=f))
        else:
            last_freq = f


def get_frequency_map(frequencies, frequency_space):
    idx_map = dict()

    check_frequencies_order(frequencies)

    last_idx = 0
    for f in frequencies:
        idx_map[f] = last_idx
        for fs_i in range(last_idx, len(frequency_space)):
            if abs(frequency_space[fs_i] - f) <= abs(frequency_space[idx_map[f]] - f):
                idx_map[f] = fs_i
            else:
                last_idx = idx_map[f]
                break
            last_idx = idx_map[f]

    value_map = {f: frequency_space[idx] for f, idx in idx_map.items()}

    return idx_map, value_map


def get_top_frequencies(fs_signal, frequency_space, n=1):
    top_idx = np.abs(fs_signal).argsort()[-n:][::-1]
    top_frequencies = np.zeros(n, dtype=frequency_space.dtype)
    top_amplitudes = np.zeros(n, dtype=fs_signal.dtype)

    for i in range(n):
        top_frequencies[i] = frequency_space[top_idx[i]]
        top_amplitudes[i] = fs_signal[top_idx[i]]

    return top_idx, top_frequencies, top_amplitudes


class PATone:
    def __init__(self, frequency, amplitude, on=True):
        self.frequency = frequency
        self.amplitude = amplitude
        self.on = on


def get_freq_space_signal(tones: [PATone], frequency_space: [float], frequency_idx_map, scale=1.):
    freq_space_signal = np.zeros(len(frequency_space), dtype=np.complex128)
    for t in tones:
        if t.on:
            freq_idx = frequency_idx_map[t.frequency]
            freq_space_signal[freq_idx] = t.amplitude * scale

    return freq_space_signal


class PAMultiTone:
    def __init__(self, frequencies, volume=1., fft_type=RFFT):
        self.task_queue = deque()

        self.tones = [PATone(frequency=f, amplitude=volume, on=False) for f in frequencies]
        self.volume = volume

        self.bitrate = _pa_state.bitrate
        self.frame_size = int(self.bitrate)

        self.frequency_space = get_frequency_space(frame_size=self.frame_size, sample_rate=self.bitrate)
        self.frequency_idx_map, _ = get_frequency_map(frequencies, self.frequency_space)

        self.fft_type = fft_type

        self.stream = self._get_stream()

    def _flush_queue(self):
        while len(self.task_queue):
            task = self.task_queue.pop()
            fn_name = task[0]
            args = task[1:]
            func = getattr(self, fn_name)
            func(*args)

    def _get_stream(self):
        def stream_callback(in_data, frame_count, time_info, status):
            self._flush_queue()
            return self._get_samples(frame_count, time_info['output_buffer_dac_time']), pyaudio.paContinue

        return _pa_state.pa_instance.open(
            format=pyaudio.paFloat32,
            channels=_pa_state.channels,
            rate=_pa_state.bitrate,
            output=True,
            stream_callback=stream_callback,
        )

    def _get_samples(self, frame_count, time_base):
        freq_space_signal = get_freq_space_signal(tones=self.tones,
                                                  frequency_space=self.frequency_space,
                                                  frequency_idx_map=self.frequency_idx_map,
                                                  scale=self.frame_size / len(self.tones),
                                                  )

        if self.fft_type == RFFT:
            inverse_fft_function = fft.irfft
        elif self.fft_type == FFT:
            inverse_fft_function = fft.ifft
        else:
            raise ValueError('Unsupported FFT type: %s.' % self.fft_type)

        signal = inverse_fft_function(freq_space_signal, self.frame_size)

        start = int((time_base % (self.bitrate / self.frame_size)) * self.bitrate) % self.frame_size
        stop = start + frame_count

        if stop < len(signal):
            window = signal[start:stop]
        else:
            window = np.concatenate((signal[start:], signal[:stop - len(signal)]))

        scaled_window = window.real * self.volume * self.get_scale_factor()

        return scaled_window.astype(np.float32)

    def get_scale_factor(self):
        return 1 / (sum([abs(t.amplitude) for t in self.tones]) + 1) ** .5

    def play(self):
        for t in range(len(self.tones)):
            self.play_tone(t)

        self.stream.start_stream()

    def stop(self):
        self.stream.stop_stream()

    def _set_amplitude(self, key, value):
        self.tones[key].amplitude = value

    def set_amplitude(self, key, value):
        self.task_queue.append(('_set_amplitude', key, value))
        self._set_amplitude(key, value)

    def get_amplitude(self, key):
        return self.tones[key].amplitude

    def _play_tone(self, key):
        self.tones[key].on = True

    def play_tone(self, key):
        self.task_queue.append(('_play_tone', key))
        self._play_tone(key)

    def _stop_tone(self, key):
        self.tones[key].on = False

    def stop_tone(self, key):
        self.task_queue.append(('play_tone', key))
        self._stop_tone(key)

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
        return self.tones.get_amplitude(item)

    def __setitem__(self, key, value):
        self.tones.set_amplitude(key, value)

    def __len__(self):
        return len(self.tones)

    def __del__(self):
        self.stop()


def test():
    from acoustic_sight.sound_drivers.test_run import test_run
    test_run(init_audio, PASynth)


if __name__ == "__main__":
    test()
