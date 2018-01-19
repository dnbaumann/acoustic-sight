import multiprocessing
import os
import subprocess
import sys
import time

import requests

from acoustic_sight_server.tools import get_free_port
from acoustic_sight_server.rpi_cam_client.remote_image_client import RemoteImageClient


DIR = os.path.dirname(os.path.realpath(__file__))
NODE_JS_APP_DIR = os.path.join(DIR, 'rpi_cam_js_client')


def get_node_path():
    for node_path in ['node', '/usr/bin/node', '/usr/local/bin/node']:
        try:
            cmd = ['/usr/bin/env', 'which', node_path]
            return subprocess.check_output(cmd).decode().strip()
        except subprocess.CalledProcessError:
            pass


def run_client(*args):
    try:
        cmd = [get_node_path(), os.path.join(NODE_JS_APP_DIR, 'app.js')] + list(args)
        return subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        pass


class RPiCamSocketIOClient(RemoteImageClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client_port = get_free_port()

        self.process = multiprocessing.Process(
            target=run_client,
            args=[
                'http://{remote_host}:{remote_port}'.format(
                    remote_host=self.host,
                    remote_port=self.port,
                ),
                '/cam',
                '%s' % self.client_port
            ])

    def start(self):
        self.process.start()

        attempts = 10
        while not self.process.is_alive() and attempts > 0:
            time.sleep(.1)
            attempts -= 1

    def stop(self):
        self.process.terminate()
        self.process.join()

    def get_latest_image_url(self):
        r = requests.get('http://127.0.0.1:{port}/'.format(port=self.client_port))
        return r.json().get('src')


if __name__ == '__main__':
    run_client(*sys.argv[1:])
