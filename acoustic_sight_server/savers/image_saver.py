import abc
import datetime
import multiprocessing
import os
import subprocess
import time
import uuid


class ImageSaver(object):
    def __init__(self, ext='jpg', data_dir='/tmp', prefix='img-', in_parallel=False):
        session_name = '{datetime}-{uuid}'.format(
            datetime=datetime.datetime.now().isoformat(),
            uuid=str(uuid.uuid4()),
        )

        tarball_path = os.path.join(data_dir, '{}.tar'.format(session_name))
        save_path = os.path.join(data_dir, session_name)

        os.makedirs(save_path, exist_ok=True)
        subprocess.run(('tar', '-cf', tarball_path, '-T', '/dev/null'))

        self.data_dir = data_dir
        self.save_path = save_path
        self.tarball_path = tarball_path
        self.ext = ext
        self.file_name_template = os.path.join(save_path, '%s{millis:014d}.%s' % (prefix, ext))
        self.in_parallel = in_parallel

        if in_parallel:
            self.queue = multiprocessing.Queue()
            self.process = multiprocessing.Process(
                target=self.parallel_saver,
                args=(self,),
            )
            self.process.start()

    def get_next_filename(self):
        unix_millis = int(time.time() * 1000)
        return self.file_name_template.format(millis=unix_millis)

    def save(self, img):
        filename = self.get_next_filename()

        if self.in_parallel:
            self.queue.put((img, filename))
        else:
            self.save_image(img, filename)
            self.pack_image(filename)

    @staticmethod
    def parallel_saver(saver):
        while True:
            image, filename = saver.queue.get()
            saver.save_image(image, filename)
            saver.pack_image(filename)

    def pack_image(self, filename):
        if filename.startswith(self.data_dir):
            filename = filename[len(self.data_dir):]
        filename = filename.lstrip('/')

        subprocess.run(('tar', '-rf', self.tarball_path, '-C', self.data_dir, filename))

    @staticmethod
    @abc.abstractstaticmethod
    def save_image(img, filename):
        pass


class PILImageSaver(ImageSaver):
    @staticmethod
    def save_image(img, filename):
        img.save(filename)
