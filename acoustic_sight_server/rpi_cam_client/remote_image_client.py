import abc
import io

from PIL import Image
import requests

from acoustic_sight_server.rpi_cam_client.image_retriever import ImageRetriever


class RemoteImageClient(ImageRetriever):
    @abc.abstractmethod
    def get_latest_image_url(self):
        pass

    def get_image(self):
        url = self.get_latest_image_url()
        r = requests.get(url)

        temp_buff = io.BytesIO()
        temp_buff.write(r.content)

        temp_buff.seek(0)

        return Image.open(temp_buff)
