import abc
import os

from acoustic_sight.tools import TimeMeasurer, get_logger


DIR = os.path.dirname(os.path.realpath(__file__))


class RetrieverTypes:
    SocketIO = 'SocketIO'
    Http = 'Http'
    PyGame = 'PyGame'
    OpenCV = 'OpenCV'


def get_client(retriever_type):
    if retriever_type == RetrieverTypes.SocketIO:
        from acoustic_sight_server.rpi_cam_client.rpi_cam_socket_io_client import RPiCamSocketIOClient
        return RPiCamSocketIOClient
    elif retriever_type == RetrieverTypes.Http:
        from acoustic_sight_server.rpi_cam_client.rpi_cam_http_client import RPiCamHttpClient
        return RPiCamHttpClient
    elif retriever_type == RetrieverTypes.PyGame:
        from acoustic_sight_server.rpi_cam_client.pygame_client import PyGameClient
        return PyGameClient
    elif retriever_type == RetrieverTypes.OpenCV:
        from acoustic_sight_server.rpi_cam_client.opencv_client import OpenCVClient
        return OpenCVClient
    else:
        raise ValueError('Client is not supported: {client_type}.'.format(client_type=retriever_type))


class ImageRetriever(object):
    def __init__(self, host, port, logger=None, profile=False):
        self.host = host
        self.port = port

        if logger is None:
            self.logger = get_logger('ImageRetriever')
        else:
            self.logger = logger

        if profile:
            self.time_measurer = TimeMeasurer(logger=self.logger)
            self.time_measurer.decorate_method(self, self.get_image, 'Got image')

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def get_image(self):
        pass
