from aiohttp import web
from aiohttp_index import IndexMiddleware
import socketio

from acoustic_sight.tools import get_logger
from acoustic_sight_server.remote_image_sonificator import RemoteImageSonificator


logger = get_logger('acoustic_sight_server.server')

sio = socketio.AsyncServer()
app = web.Application(middlewares=[IndexMiddleware()])
sio.attach(app)


async def close_all_connections():
    for sock in sio.eio.sockets.values():
        await sock.close()


@sio.on('connect', namespace='/acoustic-sight')
async def connect(sid, environ):
    logger.warning('Connection established: {sid} from {origin}.'.format(
        sid=sid, origin=environ.get('HTTP_ORIGIN', 'unknown origin')
    ))

    app['client'] += 1


@sio.on('disconnect', namespace='/acoustic-sight')
def disconnect(sid):
    logger.warning('Disconnected: %s' % sid)

    app['client'] -= 1


async def sonify():
    """Perform frame by frame sonification."""
    app['remote_image_sonification'].start()
    while True:
        app['remote_image_sonification'].next()
        await sio.sleep(app['remote_image_sonification'].get_sleep_timeout())


def run(host=None, port=8090, remote_host='localhost', remote_port=8000, frame_rate=24, side_in=2**3, **kwargs):
    app['remote_image_sonification'] = RemoteImageSonificator(frame_rate=frame_rate,
                                                              remote_host=remote_host, remote_port=remote_port,
                                                              side_in=side_in,
                                                              **kwargs)
    app['client'] = 0

    logger.warning('Starting background tasks.')
    sio.start_background_task(sonify)

    logger.warning('Starting server.')
    web.run_app(app, host=host, port=port, **kwargs)

    if app['remote_image_sonification'].started:
        app['frame_manager'].stop()


if __name__ == '__main__':
    run()
