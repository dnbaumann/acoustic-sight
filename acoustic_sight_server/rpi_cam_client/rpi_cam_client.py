import abc
import io
import os

from PIL import Image
import requests


DIR = os.path.dirname(os.path.realpath(__file__))


class ClientTypes:
    SocketIO = 'SocketIO'
    Direct = 'Direct'


def get_client(client_type):
    if client_type == ClientTypes.SocketIO:
        from acoustic_sight_server.rpi_cam_client.rpi_cam_socket_io_client import RPiCamSocketIOClient
        return RPiCamSocketIOClient
    elif client_type == ClientTypes.Direct:
        from acoustic_sight_server.rpi_cam_client.rpi_cam_direct_client import RPiCamDirectClient
        return RPiCamDirectClient


class RPiCamClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def get_latest_image_url(self):
        pass

    def get_latest_image(self):
        url = self.get_latest_image_url()
        r = requests.get(url)

        temp_buff = io.BytesIO()
        temp_buff.write(r.content)

        temp_buff.seek(0)

        return Image.open(temp_buff)
