import cv2
from PIL import Image

from acoustic_sight_server.rpi_cam_client.image_retriever import ImageRetriever


class OpenCVClient(ImageRetriever):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.camera = None
        self.image_size = (640, 480)

        self.convert_to_PIL_Image = True

    def start(self):
        if self.camera is not None:
            raise RuntimeError('Camera is already started: {}'.format(self.camera))

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.image_size[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.image_size[1])
        self.camera.set(cv2.CAP_PROP_FPS, 24)

    def stop(self):
        if self.camera is None:
            raise RuntimeError('Camera is already stopped')

        self.camera.release()
        cv2.destroyAllWindows()
        self.camera = None

    def get_image(self):
        if self.camera is None:
            raise RuntimeError('Trying to capture image for stopped camera.')

        _, frame = self.camera.read()

        if self.convert_to_PIL_Image:
            cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            image = Image.fromarray(cv2_image)

            return image
        else:
            return frame


def capture(filename):
    client = OpenCVClient()
    client.start()

    client.get_image().save(filename)
    print('Saved to: {}'.format(filename))

    client.stop()


if __name__ == '__main__':
    capture('/tmp/opencv_test_image.jpg')
