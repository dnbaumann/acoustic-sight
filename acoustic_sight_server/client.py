import time
from http.client import IncompleteRead
from multiprocessing import Process

import io
import numpy as np
from PIL import Image
import requests
from skimage.transform import resize

from acoustic_sight.sonificator import Sonificator
from acoustic_sight_server.tools import square_crop, get_free_port
from acoustic_sight_server.rpi_cam_client.rpi_cam_client import run_client


class RemoteImageSonificator(object):
    def __init__(self, host='localhost', port=8000, fps=24, side_in=2**3, sonify=True, show_image=False, **kwargs):
        self.host = host
        self.port = port
        self.fps = fps
        self.side_in = side_in

        self.sonify = sonify
        self.sonificator = None

        self.show_image = show_image
        self.cv2 = None

        self.rpi_cam_client_port = get_free_port()
        self.rpi_cam_client = Process(target=run_client,
                                      args=['http://127.0.0.1:8000', '/cam', '%s' % self.rpi_cam_client_port])

        if sonify:
            self.sonificator = Sonificator(side_in=side_in, octaves=6, **kwargs)

        if show_image:
            import cv2
            self.cv2 = cv2

    def get_latest_image_url(self):
        r = requests.get('http://127.0.0.1:{port}/'.format(port=self.rpi_cam_client_port))
        return r.json()['src']

    def get_latest_image(self):
        url = self.get_latest_image_url()
        r = requests.get(url)

        temp_buff = io.BytesIO()
        temp_buff.write(r.content)

        temp_buff.seek(0)

        return Image.open(temp_buff)

    def get_data(self):
        img = self.get_latest_image()
        img_arr = np.array(img.convert('L'))
        cropped = square_crop(img_arr)
        downsampled = resize(cropped, (self.side_in, self.side_in), mode='reflect')
        downsampled = (downsampled * 255).astype(np.uint8)

        return downsampled

    def run(self):
        self.rpi_cam_client.start()

        try:
            while True:
                if not self.rpi_cam_client.is_alive():
                    raise ChildProcessError('RPi Camera client is offline.')
                try:
                    data = self.get_data()

                    if self.sonify:
                        self.sonificator.sonify(data)

                    if self.show_image:
                        self.cv2.imshow('frame', data)
                        if self.cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                except (OSError, IncompleteRead):
                    pass

                time.sleep(1 / self.fps)
        except KeyboardInterrupt:
            pass

        self.rpi_cam_client.terminate()


def main():
    sonificator = RemoteImageSonificator(fps=12, sonify=True, show_image=False)
    sonificator.run()


if __name__ == "__main__":
    main()
