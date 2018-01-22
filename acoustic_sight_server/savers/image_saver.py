import abc
import os
import multiprocessing
import time
import uuid


class ImageSaver(object):
    def __init__(self, ext='jpg', save_path='/tmp', prefix='img-', create_session=True, in_parallel=False):
        if create_session:
            save_path = os.path.join(save_path, str(uuid.uuid4()))
            os.makedirs(save_path)

        self.save_path = save_path
        self.ext = ext
        self.file_name_template = os.path.join(save_path, '%s{millis:014d}.%s' % (prefix, ext))
        self.in_parallel = in_parallel

        if in_parallel:
            self.queue = multiprocessing.Queue()
            self.process = multiprocessing.Process(target=self.parallel_saver, args=(self.queue, self._save_image))
            self.process.start()

    def get_next_filename(self):
        unix_millis = int(time.time() * 1000)
        return self.file_name_template.format(millis=unix_millis)

    def save_image(self, img):
        filename = self.get_next_filename()

        if self.in_parallel:
            self.queue.put((img, filename))
        else:
            self._save_image(img, self.get_next_filename())

    @staticmethod
    def parallel_saver(queue, save_fn):
        while True:
            image, filename = queue.get()
            save_fn(image, filename)

    @staticmethod
    @abc.abstractstaticmethod
    def _save_image(img, filename):
        pass


class PILImageSaver(ImageSaver):
    @staticmethod
    def _save_image(img, filename):
        img.save(filename)
