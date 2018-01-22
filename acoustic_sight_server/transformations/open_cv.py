import cv2
import numpy as np

from acoustic_sight_server.transformations.basic import ImageTransformation


class OpenCVOpticalFlowTransformation(ImageTransformation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.previous = None
        self.hsv = None

    def _process(self, image):
        if image.shape[0] != self.sonificator.rpi_cam_client.image_size[1] or image.shape[0] != image.shape[1]:
            return np.zeros_like(image)

        if self.previous is None:
            self.previous = image
            self.hsv = np.zeros(image.shape + (3,), image.dtype)
            self.hsv[..., 1] = 255

            return np.zeros_like(image)

        flow = cv2.calcOpticalFlowFarneback(self.previous, image, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        self.hsv[..., 0] = ang * 180 / np.pi / 2
        self.hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        rgb = cv2.cvtColor(self.hsv, cv2.COLOR_HSV2BGR)

        self.previous = image

        return cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
