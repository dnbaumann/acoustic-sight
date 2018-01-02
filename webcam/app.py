#!/usr/bin/env python3

from time import sleep

import cv2

from webcam.processors.cv2_frame_processor import CV2FrameProcessor
from sonification import sound_drivers
from sonification.sonificator import Sonificator
from sonification.tools import get_logger


logger = get_logger('webcam')


class WebcamApp:
    def __init__(self, side_in=16, side_out=640,
                 fps=24, max_volume=.5, volume_type='exp',
                 octaves=3, tone_shift=-18,
                 sonify=True, show_windows=True):
        self.side_in = side_in
        self.side_out = side_out
        self.fps = fps
        self.max_volume = max_volume
        self.volume_type = volume_type
        self.octaves = octaves
        self.tone_shift = tone_shift
        self.sonify = sonify
        self.show_windows = show_windows
        self.frame_processor = CV2FrameProcessor(self.side_in, self.side_out)

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
            _, sound_input, upsampled, cropped = self.frame_processor.process_frame(frame)

            self._sonify(sound_input)

            # Sleep until next frame
            sleep(1 / self.fps)

            # Display the resulting frame if required
            if self.show_windows:
                cv2.imshow('frame', cropped)
                cv2.imshow('Sound input', upsampled)

            # Break if exit requested
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--side_in', type=int, help='image side dimension for audio input', default=2**3)
    parser.add_argument('--side_out', type=int, help='side dimension for input image preview', default=640)
    parser.add_argument('--fps', type=int, help='maximum frames per second', default=24)
    parser.add_argument('--max_volume', type=float, help='frequency max volume (from .0 to 1.)', default=.125)
    parser.add_argument('--volume_type', type=str, help='volume scale type',
                        choices=['linear', 'threshold', 'exp'], default='exp')
    parser.add_argument('--octaves', type=int, help='frequency span in octaves', default=6)
    parser.add_argument('--tone_shift', type=int, help='first frequency shift from 440Hz in halftones', default=-18)
    parser.add_argument('--no_sound', action='store_true', help='turn sonification off')
    parser.add_argument('--no_preview', action='store_true', help='turn images preview off')
    parser.add_argument('--driver', type=str, default=sound_drivers.SUPER_COLLIDER, help='sound driver')
    args = parser.parse_args()

    app = WebcamApp(side_in=args.side_in, side_out=args.side_out, fps=args.fps, max_volume=args.max_volume,
                    volume_type=args.volume_type, octaves=args.octaves, tone_shift=args.tone_shift,
                    sonify=not args.no_sound, show_windows=not args.no_preview)
    app.run()


if __name__ == "__main__":
    main()
