#!/usr/bin/env python3

import logging
import math

from time import sleep

import cv2

from sound_drivers.sc_tools import SCSynth as Synth, init_audio
import hilbert_curve


logger = logging.getLogger('WebcamApp')
logger.setLevel(logging.INFO)


def process_frame(frame, side_in, side_out):
    (height, width, *_) = frame.shape

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Crop image to square size
    side = min((width, height))
    left = (width - side) // 2
    right = left + side
    top = (height - side) // 2
    bottom = top + side
    cropped = gray[top:bottom, left:right]

    # Sample down to [side x side] for sonification
    sound_input = cv2.resize(cropped, (side_in, side_in))

    # Sample up to [side_out x side_out] for better preview
    upsampled = cv2.resize(sound_input, (side_out, side_out))

    # Set output frame
    out = upsampled

    return out, sound_input


class Sonificator:
    def __init__(self, side_in, octaves=3, shift=-18):
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


class WebcamApp:
    def __init__(self, side_in=16, side_out=640,
                 fps=24, max_volume=.5, volume_type='exp',
                 octaves=3, tone_shift=-18):
        self.side_in = side_in
        self.side_out = side_out
        self.fps = fps
        self.max_volume = max_volume
        self.volume_type = volume_type
        self.octaves = octaves
        self.tone_shift = tone_shift

    def run(self):
        logger.info('Starting Sight-via-Sound webcam application {}.'.format(self.__dict__))
        cap = cv2.VideoCapture(0)
        sonificator = Sonificator(side_in=self.side_in, octaves=self.octaves, shift=self.tone_shift)
        logger.info('Sight-via-Sound webcam application started.')

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            out, sound_input = process_frame(frame, self.side_in, self.side_out)

            sonificator.sonify(arr=sound_input, volume_type=self.volume_type, max_volume=self.max_volume)

            # Sleep until next frame
            sleep(1 / self.fps)

            # Display the resulting frame
            cv2.imshow('frame', out)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()


def main():
    app = WebcamApp(octaves=3, max_volume=.1)
    app.run()


if __name__ == "__main__":
    main()
