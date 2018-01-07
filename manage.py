from manager import Manager

from acoustic_sight_server.remote_image_sonificator import RemoteImageSonificator

manager = Manager()


@manager.command
def remote_image_sonificator(host='localhost', port=8000, fps=24, side_in=2**3, sonify=True, show_image=False):
    """Runs remote image sonificator (cobbects to RPi Camera application)"""
    sonificator = RemoteImageSonificator(host=host, port=port, fps=fps, side_in=side_in,
                                         sonify=sonify, show_image=show_image)
    sonificator.run()


if __name__ == '__main__':
    manager.main()
