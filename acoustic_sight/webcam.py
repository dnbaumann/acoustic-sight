#!/usr/bin/env python3

from time import sleep

import numpy as np
import cv2

import synth
import hilbert_curve


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
    def __init__(self, side_in):
        synth.init()
        self.synth = synth.Synth(levels=side_in*side_in, octaves=3, shift=-18)

    def sonify(self, arr, volume_type='linear', max_volume=.5):
        vec = hilbert_curve.hilbert_expand(arr)
        for i in range(len(vec)):
            if volume_type == 'linear':
                self.synth[i] = vec[i] / 255 * max_volume
            elif volume_type == 'threshold':
                self.synth[i] = (vec[i] > 127) * 1.


def main():
    side_in = 1
    side_out = 640
    fps = 6
    max_volume = .5
    volume_type = 'linear'

    cap = cv2.VideoCapture(0)
    sonificator = Sonificator(side_in)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        out, sound_input = process_frame(frame, side_in, side_out)

        sonificator.sonify(arr=sound_input, volume_type=volume_type, max_volume=max_volume)

        # Sleep until next frame
        sleep(1 / fps)

        # Display the resulting frame
        cv2.imshow('frame', out)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
