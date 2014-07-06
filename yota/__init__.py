from yota import logging

logger = logging.get_logger('yota')
logger.info('Initializing')

from yota.config import config
from yota import pb
from yota import utils
from yota.web import web
from yota import parser
from yota import current_speed_provider
from yota.speed_control import speed_control

logger.info('Initialised')

def run():
    try:
        logger.info('Starting')
        current_speed_provider.run()
        speed_control.run()
    except BaseException as e:
        logging.get_logger('yota.main').exception(e)