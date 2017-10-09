#!/usr/bin/env python3

import math

from time import sleep

import cv2
import numpy

import sound_drivers
import hilbert_curve

from logger import logger

Synth, init_audio = sound_drivers.get_driver(sound_drivers.SUPER_COLLIDER)


def process_frame(frame, side_in, side_out):
    (height, width, *_) = frame.shape

    # Transformations
    downsample = lambda img: cv2.resize(img, (side_in, side_in))
    sharp = lambda img: cv2.filter2D(img, -1, numpy.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]))
    gaussian_blur = lambda img: cv2.GaussianBlur(img, (5, 5), 0)
    median_blur = lambda img: cv2.medianBlur(img, 5)
    denoising = lambda img: cv2.fastNlMeansDenoising(img, h=7, templateWindowSize=7, searchWindowSize=21)
    canny_edges = lambda img: cv2.Canny(img, 50, 100)
    laplasian = lambda img: cv2.Laplacian(img, cv2.CV_64F)
    grayscale = lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mirror = lambda img: cv2.flip(img, 1)
    upsample = lambda img: cv2.resize(img, (side_out, side_out))

    def square_crop(img):
        side = min((width, height))
        left = (width - side) // 2
        right = left + side
        top = (height - side) // 2
        bottom = top + side
        return img[top:bottom, left:right]

    def apply_chain(img, transform_chain):
        for transform in transform_chain:
            img = transform(img)
        return img

    # Create base image
    base_transformations = [
        grayscale,
        square_crop,
        mirror,
    ]
    base = apply_chain(frame, base_transformations)

    # Create sound input image
    sound_input = apply_chain(base, [
        gaussian_blur,
        downsample,
        denoising,
        # median_blur,
        # sharp,
        # laplasian,
        # canny_edges,
    ])

    # Sample up to [side_out x side_out] for better preview
    upsampled = upsample(sound_input)

    return sound_input, upsampled, base


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
                 octaves=3, tone_shift=-18,
                 sonify=True):
        self.side_in = side_in
        self.side_out = side_out
        self.fps = fps
        self.max_volume = max_volume
        self.volume_type = volume_type
        self.octaves = octaves
        self.tone_shift = tone_shift
        self.sonify = sonify

    def _init_sonificator(self):
        if self.sonify:
            self.sonificator = Sonificator(side_in=self.side_in, octaves=self.octaves, shift=self.tone_shift)

    def _sonify(self, arr):
        if self.sonify:
            self.sonificator.sonify(arr=arr, volume_type=self.volume_type, max_volume=self.max_volume)

    def run(self):
        logger.info('Starting Sight-via-Sound webcam application {}.'.format(self.__dict__))
        cap = cv2.VideoCapture(0)
        self._init_sonificator()
        logger.info('Sight-via-Sound webcam application started.')

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            sound_input, upsampled, cropped = process_frame(frame, self.side_in, self.side_out)

            self._sonify(sound_input)

            # Sleep until next frame
            sleep(1 / self.fps)

            # Display the resulting frame
            cv2.imshow('frame', cropped)
            cv2.imshow('Sound input', upsampled)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()


def main():
    app = WebcamApp(octaves=3, side_in=2**4, sonify=True)
    app.run()


if __name__ == "__main__":
    main()
