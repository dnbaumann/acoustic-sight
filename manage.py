from manager import Manager

from acoustic_sight import sound_drivers
from acoustic_sight_server.remote_image_sonificator import RemoteImageSonificator
from acoustic_sight_server.rpi_cam_client.rpi_cam_client import ClientTypes
import acoustic_sight_server.server

manager = Manager()


@manager.command
def remote_image_sonificator(remote_host='localhost', remote_port=8000, frame_rate=24,
                             side_in=2**3, sonify=True, show_image=False,
                             synth_type=sound_drivers.SUPER_COLLIDER,
                             rpi_cam_client_type=ClientTypes.Direct,
                             ):
    """Runs remote image sonificator (cobbects to RPi Camera application)"""
    sonificator = RemoteImageSonificator(remote_host=remote_host, remote_port=remote_port,
                                         frame_rate=frame_rate, side_in=side_in,
                                         sonify=sonify, show_image=show_image,
                                         synth_type=synth_type,
                                         rpi_cam_client_type=rpi_cam_client_type,
                                         )
    sonificator.run()


@manager.command
def runserver(host=None, port=8090, remote_host='localhost',
              remote_port=8000, frame_rate=24, side_in=2**3,
              synth_type=sound_drivers.SUPER_COLLIDER,
              rpi_cam_client_type=ClientTypes.Direct,
              ):
    acoustic_sight_server.server.run(host=host, port=port,
                                     remote_host=remote_host, remote_port=remote_port,
                                     frame_rate=frame_rate, side_in=side_in,
                                     synth_type=synth_type,
                                     rpi_cam_client_type=rpi_cam_client_type,
                                     )


if __name__ == '__main__':
    manager.main()
