import time

import cv2
import httplib2
import io
import numpy as np
from PIL import Image
from skimage.transform import resize

from acoustic_sight.sonificator import Sonificator
from acoustic_sight_server.tools import square_crop


class RemoteImageSonificator(object):
    def __init__(self, host='localhost', port=8000, fps=24, side_in=2**3, **kwargs):
        self.host = host
        self.port = port
        self.fps = fps
        self.side_in = side_in

        self.sonificator = Sonificator(side_in=side_in, **kwargs)

    def get_latest_image(self):
        url = 'http://{host}:{port}/cam_data/previews/latest.jpg'.format(host=self.host, port=self.port)
        h = httplib2.Http()
        resp, content = h.request(url, "GET")

        temp_buff = io.BytesIO()
        temp_buff.write(content)
        temp_buff.seek(0)

        return Image.open(temp_buff)

    def get_data(self):
        img = self.get_latest_image()
        img_arr = np.array(img.convert('L'))
        cropped = square_crop(img_arr)
        downsampled = resize(cropped, (self.side_in, self.side_in))

        return downsampled

    def run(self):
        while True:
            try:
                data = self.get_data()
                self.sonificator.sonify(data)
                cv2.imshow('frame', data)
            except OSError:
                pass

            time.sleep(1 / self.fps)

            # Break if exit requested
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


def main():
    sonificator = RemoteImageSonificator(fps=12)
    sonificator.run()


if __name__ == "__main__":
    main()
