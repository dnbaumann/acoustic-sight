import time
from http.client import IncompleteRead

import numpy as np
from skimage.transform import resize

from acoustic_sight import sound_drivers
from acoustic_sight.sonificator import Sonificator
from acoustic_sight_server.tools import square_crop
from acoustic_sight_server.rpi_cam_client.rpi_cam_client import get_client, ClientTypes
from acoustic_sight.tools import TimeMeasurer


time_measurer = TimeMeasurer()


class RemoteImageSonificator(object):
    def __init__(self, remote_host='localhost', remote_port=8000,
                 frame_rate=24, side_in=2 ** 3,
                 sonify=True, show_image=False,
                 synth_type=sound_drivers.SUPER_COLLIDER,
                 rpi_cam_client_type=ClientTypes.Direct,
                 **kwargs):
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.frame_rate = frame_rate
        self.side_in = side_in

        self.sonify = sonify
        self.sonificator = None

        self.show_image = show_image
        self.cv2 = None

        self.rpi_cam_client = get_client(rpi_cam_client_type)(self.remote_host, self.remote_port)

        self.started = False

        self.last_time_checkpoint = time.time()

        if sonify:
            self.sonificator = Sonificator(side_in=side_in, octaves=6,
                                           synth_type=synth_type, **kwargs)

        if show_image:
            import cv2
            self.cv2 = cv2

    def get_data(self):
        img = self.rpi_cam_client.get_latest_image()
        img_arr = np.array(img.convert('L'))
        cropped = square_crop(img_arr)
        downsampled = resize(cropped, (self.side_in, self.side_in), mode='reflect')
        downsampled = (downsampled * 255).astype(np.uint8)

        return downsampled

    def start(self):
        self.rpi_cam_client.start()
        self.sonificator.silence()
        self.started = True

    def next(self):
        try:
            data = self.get_data()

            if self.sonify:
                time_measurer.measure_time('Sonified', self.sonificator.sonify, data)

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

    def run(self, sleep_fn=time.sleep):
        self.start()

        try:
            while self.started:
                self.next()

                time_measurer.measure_time('Awaited', sleep_fn, self.get_sleep_timeout())
        except KeyboardInterrupt:
            pass

        self.stop()


def main():
    sonificator = RemoteImageSonificator(frame_rate=12, sonify=True, show_image=False)
    sonificator.run()


if __name__ == "__main__":
    main()
