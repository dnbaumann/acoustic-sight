import math

from sonification import sound_drivers

from sonification import hilbert_curve


class Sonificator:
    def __init__(self, side_in, octaves=3, shift=-18, synth_type=sound_drivers.SUPER_COLLIDER):
        Synth, init_audio = sound_drivers.get_driver(synth_type)

        init_audio()
        self.synth = Synth(levels=side_in*side_in, octaves=octaves, shift=shift)
        self.synth.play()

    def sonify(self, arr, volume_type='linear', max_volume=.5):
        vec = hilbert_curve.hilbert_expand(arr)
        for i in range(len(vec)):
            if volume_type == 'linear':
                self.synth[i] = vec[i] / 255 * max_volume
            elif volume_type == 'threshold':
                self.synth[i] = (vec[i] > 127) * 1.
            elif volume_type == 'exp':
                self.synth[i] = (math.exp(vec[i] / 255) - 1) / (math.exp(1) - 1) * max_volume
        self.synth.sync()
