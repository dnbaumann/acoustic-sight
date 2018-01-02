from typing import Tuple

import cv2
import numpy as np

from webcam.processors.frame_processor import FrameProcessor


class CV2FrameProcessor(FrameProcessor):
    def __init__(self, side_in: int, side_out: int, buffer_size: int=2):
        super().__init__(side_in, side_out, buffer_size)

    @staticmethod
    def sharp(img):
        return cv2.filter2D(img, -1, np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]))

    @staticmethod
    def gaussian_blur(img):
        return cv2.GaussianBlur(img, (5, 5), 0)

    @staticmethod
    def median_blur(img):
        return cv2.medianBlur(img, 5)

    @staticmethod
    def denoising(img):
        return cv2.fastNlMeansDenoising(img, h=7, templateWindowSize=7, searchWindowSize=21)

    @staticmethod
    def canny_edges(img):
        return cv2.Canny(img, 50, 100)

    @staticmethod
    def laplasian(img):
        return cv2.Laplacian(img, cv2.CV_64F)

    @staticmethod
    def grayscale(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def mirror(img):
        return cv2.flip(img, 1)

    def downsample(self, img):
        return cv2.resize(img, (self.side_in, self.side_in))

    def upsample(self, img):
        return cv2.resize(img, (self.side_out, self.side_out))

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, ...]:
        frame = super().process_frame(frame)[0]

        # Create base image
        base_transformations = [
            self.grayscale,
            self.square_crop,
            self.mirror,
        ]
        base = self.apply_chain(frame, base_transformations)

        # Create sound input image
        sound_input = self.apply_chain(base, [
            self.gaussian_blur,
            self.downsample,
            self.denoising,
            # self.median_blur,
            # self.sharp,
            # self.laplasian,
            # self.canny_edges,
        ])

        # Sample up to [side_out x side_out] for better preview
        upsampled = self.upsample(sound_input)

        return frame, sound_input, upsampled, base