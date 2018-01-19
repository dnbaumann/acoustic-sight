#!/usr/bin/env python3

import os
import shutil

from jinja2 import Template
from manager import Manager

from acoustic_sight.tools import PROJECT_DIR, SERVICES_DIR
from acoustic_sight import sound_drivers
from acoustic_sight_server.image_sonificator import ImageSonificator
from acoustic_sight_server.rpi_cam_client.image_retriever import RetrieverTypes
import acoustic_sight_server.server

manager = Manager()


ASS_SERVICE_SETTINGS = {
    'conf_template': os.path.join(SERVICES_DIR, 'supervisor.conf.tmpl'),
    'default_conf_file': os.path.join(SERVICES_DIR, 'acoustic_sight_server-supervisor.conf'),
    'command': os.path.join(PROJECT_DIR, 'manage.py') + ' runserver',
    'args': ''.join([]),
    'autostart': 'false',
}

SONIFICATOR_SETTINGS = {
    'conf_template': os.path.join(SERVICES_DIR, 'supervisor.conf.tmpl'),
    'default_conf_file': os.path.join(SERVICES_DIR, 'sonificator-supervisor.conf'),
    'command': os.path.join(PROJECT_DIR, 'manage.py') + ' remote_image_sonificator',
    'args': ''.join([
        '--sigma=2',
        '--initial_mul=32',
        '--decrease=1.2',
    ]),
    'autostart': 'true',
}

JUPYTER_SERVICE_SETTINGS = {
    'conf_template': os.path.join(SERVICES_DIR, 'supervisor.conf.tmpl'),
    'default_conf_file': os.path.join(SERVICES_DIR, 'jupyter-supervisor.conf'),
    'command': '/usr/bin/env jupyter-notebook',
    'args': ''.join([
        '--no-browser',
    ]),
    'autostart': 'false',
}

SUPERVISOR_CONF_DIR = '/etc/supervisor/conf.d'


@manager.command
def remote_image_sonificator(remote_host='localhost', remote_port=80, frame_rate=6,
                             side_in=2**3, sonify=True, show_image=False,
                             synth_type=sound_drivers.PY_GAME,
                             retriever_type=RetrieverTypes.PyGame,
                             log_level='INFO',
                             profile=False,
                             sigma=2, initial_mul=32, decrease=1.2,
                             ):
    """Runs image sonificator"""
    sonificator = ImageSonificator(remote_host=remote_host, remote_port=remote_port,
                                   frame_rate=frame_rate, side_in=side_in,
                                   sonify=sonify, show_image=show_image,
                                   synth_type=synth_type,
                                   retriever_type=retriever_type,
                                   log_level=log_level,
                                   profile=profile,
                                   sigma=sigma, initial_mul=initial_mul, decrease=decrease,
                                   )
    sonificator.run()


@manager.command
def runserver(host=None, port=8090, remote_host='localhost',
              remote_port=80, frame_rate=6, side_in=2**3,
              synth_type=sound_drivers.PY_GAME,
              retriever_type=RetrieverTypes.PyGame,
              log_level='INFO',
              profile=False,
              sigma=2, initial_mul=32, decrease=1.2,
              ):
    acoustic_sight_server.server.run(host=host, port=port,
                                     remote_host=remote_host, remote_port=remote_port,
                                     frame_rate=frame_rate, side_in=side_in,
                                     synth_type=synth_type,
                                     retriever_type=retriever_type,
                                     log_level=log_level,
                                     profile=profile,
                                     sigma=sigma, initial_mul=initial_mul, decrease=decrease,
                                     )


def crete_config(path, command, args, log_dir, program_name, autostart):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    with open(JUPYTER_SERVICE_SETTINGS['conf_template']) as tmpl:
        template = Template(tmpl.read())
        config = template.render(
            command=command, args=args,
            project_dir=PROJECT_DIR, log_dir=log_dir,
            program_name=program_name,
            autostart=autostart,
        )

        with open(path, 'w') as conf:
            conf.write(config)


@manager.command
def server_supervisor_conf(
        path=ASS_SERVICE_SETTINGS['default_conf_file'],
        command=ASS_SERVICE_SETTINGS['command'],
        args=ASS_SERVICE_SETTINGS['args'],
        log_dir=SERVICES_DIR,
        autostart=ASS_SERVICE_SETTINGS['autostart'],
):
    """Generates Supervisor config for Jupyter"""
    crete_config(path, command, args, log_dir, 'asoustic_sight_server', autostart)


@manager.command
def sonificator_conf(
        path=SONIFICATOR_SETTINGS['default_conf_file'],
        command=SONIFICATOR_SETTINGS['command'],
        args=SONIFICATOR_SETTINGS['args'],
        log_dir=SERVICES_DIR,
        autostart=SONIFICATOR_SETTINGS['autostart'],
):
    """Generates Supervisor config for remote sonificator"""
    crete_config(path, command, args, log_dir, 'sonificator', autostart)


@manager.command
def jupyter_supervisor_conf(
        path=JUPYTER_SERVICE_SETTINGS['default_conf_file'],
        command=JUPYTER_SERVICE_SETTINGS['command'],
        args=JUPYTER_SERVICE_SETTINGS['args'],
        log_dir=SERVICES_DIR,
        autostart=JUPYTER_SERVICE_SETTINGS['autostart'],
):
    """Generates Supervisor config for Jupyter"""
    crete_config(path, command, args, log_dir, 'jupyter', autostart)


@manager.command
def make_configs():
    server_supervisor_conf()
    sonificator_conf()
    jupyter_supervisor_conf()


@manager.command
def copy_configs(dst=SUPERVISOR_CONF_DIR, sudo=False):
    for conf in [SONIFICATOR_SETTINGS, JUPYTER_SERVICE_SETTINGS, ASS_SERVICE_SETTINGS]:
        src_path = conf['default_conf_file']
        dst_path = os.path.join(dst, os.path.basename(src_path))

        try:
            shutil.copy2(src_path, dst_path)
        except PermissionError as e:
            if sudo:
                shutil.os.system('sudo cp "{src_path}" "{dst_path}"'.format(src_path=src_path, dst_path=dst_path))
            else:
                raise e


@manager.command
def pg_tools_test():
    from acoustic_sight.sound_drivers.pg_tools import test
    test()


@manager.command
def sc_tools_test():
    from acoustic_sight.sound_drivers.sc_tools import test
    test()


@manager.command
def pa_tools_test():
    from acoustic_sight.sound_drivers.pa_tools import test
    test()


if __name__ == '__main__':
    manager.main()
