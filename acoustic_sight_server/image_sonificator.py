import logging
import time
from http.client import IncompleteRead

import numpy as np
from skimage.transform import resize

from acoustic_sight import sound_drivers
from acoustic_sight.sonificator import Sonificator
from acoustic_sight.tools import DATA_DIR
from acoustic_sight_server.tools import square_crop
from acoustic_sight_server.rpi_cam_client.image_retriever import get_client, RetrieverTypes
from acoustic_sight_server.savers.image_saver import PILImageSaver
from acoustic_sight.tools import TimeMeasurer, get_logger
from acoustic_sight_server.transformations.basic import CannyTransformation


class ImageSonificator(object):
    def __init__(self, remote_host='localhost', remote_port=8000,
                 frame_rate=24, side_in=2**3,
                 sonify=True, show_image=False,
                 synth_type=sound_drivers.SUPER_COLLIDER,
                 retriever_type=RetrieverTypes.PyGame,
                 logger=None,
                 log_level=logging.INFO,
                 profile=False,
                 save_images=False,
                 sigma=2, initial_mul=32, decrease=1.2,
                 **kwargs):
        if logger is None:
            self.logger = get_logger('ImageSonificator', level=log_level)
        else:
            self.logger = logger

        if profile:
            self.time_measurer = TimeMeasurer(logger=self.logger)

            self.time_measurer.decorate_method(self, self.next, 'Full cycle')
            self.time_measurer.decorate_method(self, self.get_data, 'Data retrieved')
            self.time_measurer.decorate_method(self, self.process_full_size_image, 'Full size process')
            self.time_measurer.decorate_method(self, self.await, 'Awaited')
            self.time_measurer.decorate_method(self, self.save_image, 'Saved original')

        self.remote_host = remote_host
        self.remote_port = remote_port
        self.frame_rate = frame_rate
        self.side_in = side_in

        self.sonify = sonify
        self.sonificator = None

        self.save_images = save_images
        self.image_saver = None

        self.show_image = show_image
        self.cv2 = None

        self.rpi_cam_client = get_client(retriever_type)(self.remote_host, self.remote_port, profile=profile)

        self.started = False

        self.last_time_checkpoint = time.time()

        if sonify:
            self.sonificator = Sonificator(side_in=side_in, octaves=6,
                                           synth_type=synth_type, profile=profile,
                                           **kwargs,
                                           )
        if save_images:
            self.image_saver = PILImageSaver(save_path=DATA_DIR, in_parallel=True)

        if show_image:
            import cv2
            self.cv2 = cv2

        self.transforamtion = CannyTransformation(self, sigma=sigma, initial_mul=initial_mul, decrease=decrease)

    def process_full_size_image(self, image):
        return self.transforamtion.transform(image)

    def process_downsampled_image(self, image):
        return image

    def save_image(self, img):
        if self.save_images:
            self.image_saver.save_image(img)

    def get_data(self):
        img = self.rpi_cam_client.get_image()
        self.save_image(img)

        # Prepare square array:
        img_arr = np.array(img.convert('L'))
        cropped = square_crop(img_arr)

        full_size_processed = self.process_full_size_image(cropped)

        # Downsample image
        downsampled = resize(full_size_processed, (self.side_in, self.side_in), mode='reflect')
        downsampled = (downsampled * 255).astype(np.uint8)

        downsampled_processed = self.process_downsampled_image(downsampled)

        return downsampled_processed

    def start(self):
        self.rpi_cam_client.start()
        self.sonificator.silence()
        self.started = True

    def next(self):
        try:
            data = self.get_data()

            if self.sonify:
                self.sonificator.sonify(data)

            if self.show_image:
                self.cv2.imshow('frame', data)
                if self.cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop()

        except (OSError, IncompleteRead):
            self.sonificator.silence()

        return self.started

    def stop(self):
        if self.started:
            self.started = False
            self.rpi_cam_client.stop()

    def get_sleep_timeout(self):
        base_period = 1 / self.frame_rate
        new_checkpoint = time.time()
        time_passed = new_checkpoint - self.last_time_checkpoint

        if time_passed < base_period:
            return base_period - time_passed
        else:
            return 0

    def await(self, sleep_fn):
        sleep_fn(self.get_sleep_timeout())

    def run(self, sleep_fn=time.sleep):
        self.start()

        try:
            while self.started:
                self.next()
                self.await(sleep_fn)
        except KeyboardInterrupt:
            pass

        self.stop()


def main():
    sonificator = ImageSonificator(frame_rate=12, sonify=True, show_image=False)
    sonificator.run()


if __name__ == "__main__":
    main()
