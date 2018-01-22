import pygame.image
import pygame.camera
from PIL import Image

from acoustic_sight_server.rpi_cam_client.image_retriever import ImageRetriever


class PyGameClient(ImageRetriever):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.camera = None
        self.image_size = (640, 480)

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

    def get_image(self):
        if self.camera is None:
            raise RuntimeError('Trying to capture image for stopped camera.')

        surface = self.camera.get_image()
        imgstr = pygame.image.tostring(surface, 'RGB')
        return Image.frombytes('RGB', surface.get_size(), imgstr)


def capture(filename):
    client = PyGameClient()
    client.start()

    client.get_image().save(filename)
    print('Saved to: {}'.format(filename))

    client.stop()


if __name__ == '__main__':
    capture('/tmp/pygame_test_image.jpg')
