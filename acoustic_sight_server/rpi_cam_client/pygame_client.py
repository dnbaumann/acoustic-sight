import pygame.image
import pygame.camera
from PIL import Image

from acoustic_sight_server.rpi_cam_client.rpi_cam_client import RPiCamClient


class PyGameClient(RPiCamClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.camera = None
        self.image_size = (160, 120)

        pygame.camera.init()

    def start(self):
        if self.camera is not None:
            raise RuntimeError('Camera is already started: {}'.format(self.camera))

        self.camera = pygame.camera.Camera(pygame.camera.list_cameras()[0], self.image_size)
        self.camera.start()

    def stop(self):
        if self.camera is None:
            raise RuntimeError('Camera is already stopped')

        self.camera.stop()
        self.camera = None

    def get_latest_image_url(self):
        return None

    def get_latest_image(self):
        if self.camera is None:
            raise RuntimeError('Trying to capture image for stopped camera.')

        while self.camera.query_image():
            surface = self.camera.get_image()

        imgstr = pygame.image.tostring(surface, 'RGB')
        image = Image.frombytes('RGB', surface.get_size(), imgstr)

        return image


def capture(filename):
    client = PyGameClient()
    client.start()

    client.get_latest_image().save(filename)
    print('Saved to: {}'.format(filename))

    client.stop()


if __name__ == '__main__':
    capture('/tmp/pygame_test_image.jpg')
