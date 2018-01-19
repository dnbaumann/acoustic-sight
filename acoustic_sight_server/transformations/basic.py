import abc

import numpy as np
import skimage.feature


class ImageTransformation(object):
    def __init__(self, sonificator):
        self.sonificator = sonificator

    def transform(self, image):
        result = self._process(image)
        self.show_image(result)
        return result

    def show_image(self, image, name=''):
        if self.sonificator.show_image:
            self.sonificator.cv2.imshow(self.__class__.__name__ + ' - %s' % name, image)

    @abc.abstractmethod
    def _process(self, image):
        return image


class HogTransformation(ImageTransformation):
    def _process(self, image):
        fd, hog_image = skimage.feature.hog(
            image, orientations=8, pixels_per_cell=(12, 12),
            cells_per_block=(1, 1), visualise=True,
            feature_vector=False,
        )

        # fd_image = fd.reshape(fd.shape[0], fd.shape[1], fd.shape[4])
        # self.sho_image(fd_image, 'fd')

        return hog_image


class CannyTransformation(ImageTransformation):
    def __init__(self, *args, sigma=1, initial_mul=32, decrease=1.2, **kwargs):
        super().__init__(*args, **kwargs)

        self.sigma = sigma
        self.initial_mul = initial_mul
        self.decrease = decrease

        self.previous = None

    def _process(self, image):
        canny_bools = skimage.feature.canny(image, sigma=self.sigma)
        canny_image = canny_bools.astype(np.uint8) * self.initial_mul

        if image.shape[0] == self.sonificator.rpi_cam_client.image_size[1]:
            if self.previous is not None:
                canny_image += self.previous

            self.previous = (canny_image / 1.2).astype(np.uint8)

        return canny_image
