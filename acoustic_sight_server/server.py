import logging

from aiohttp import web
from aiohttp_index import IndexMiddleware
import socketio

from acoustic_sight.tools import get_logger
from acoustic_sight import sound_drivers
from acoustic_sight_server.image_sonificator import ImageSonificator
from acoustic_sight_server.rpi_cam_client.image_retriever import RetrieverTypes


async def close_all_connections(sio):
    for sock in sio.eio.sockets.values():
        await sock.close()
        
        
class AcousticSightServer(object):
    def __init__(self, host=None, port=8090, remote_host='localhost',
                 remote_port=8000, frame_rate=24, side_in=2**3,
                 octaves=6, tone_shift=-18,
                 synth_type=sound_drivers.PY_GAME,
                 retriever_type=RetrieverTypes.PyGame,
                 log_level=logging.INFO,
                 profile=False,
                 save_images=False,
                 sigma=2, initial_mul=32, decrease=1.2,
                 **server_args):
        self.logger = get_logger('acoustic_sight_server.server', level=log_level)

        self.sio = socketio.AsyncServer()
        self.app = web.Application(middlewares=[IndexMiddleware()])
        self.sio.attach(self.app)

        self.clients = 0
        self.host = host
        self.port = port
        self.server_args = server_args

        self.remote_image_sonification = ImageSonificator(
            frame_rate=frame_rate, remote_host=remote_host,
            remote_port=remote_port, side_in=side_in,
            octaves=octaves, tone_shift=tone_shift,
            synth_type=synth_type,
            retriever_type=retriever_type,
            logger=self.logger,
            profile=profile,
            save_images=save_images,
            sigma=sigma, initial_mul=initial_mul, decrease=decrease,
        )

        self.setup_events()

    def run(self):
        self.logger.warning('Starting background tasks.')
        self.sio.start_background_task(self.sonify)

        self.logger.warning('Starting server.')
        web.run_app(self.app, host=self.host, port=self.port, **self.server_args)

        if self.remote_image_sonification.started:
            self.remote_image_sonification.stop()

    def setup_events(self):
        @self.sio.on('connect', namespace='/acoustic-sight')
        async def connect(sid, environ):
            self.logger.warning('Connection established: {sid} from {origin}.'.format(
                sid=sid, origin=environ.get('HTTP_ORIGIN', 'unknown origin')
            ))

            self.clients += 1

        @self.sio.on('disconnect', namespace='/acoustic-sight')
        def disconnect(sid):
            self.logger.warning('Disconnected: %s' % sid)

            self.clients -= 1

    async def sonify(self):
        """Perform frame by frame sonification."""
        self.remote_image_sonification.start()
        while True:
            self.remote_image_sonification.next()
            await self.sio.sleep(self.remote_image_sonification.get_sleep_timeout())


def run(*args, **kwargs):
    server = AcousticSightServer(*args, **kwargs)
    server.run()


if __name__ == '__main__':
    run()
