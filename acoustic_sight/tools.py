import logging
import os


ACOUSTIC_SIGHT_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = os.path.dirname(ACOUSTIC_SIGHT_DIR)
ACOUSTIC_SIGHT_SERVER_DIR = os.path.join(PROJECT_DIR, 'acoustic_sight_server')


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    return logger
