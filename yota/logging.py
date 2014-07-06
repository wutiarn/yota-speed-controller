__author__ = 'rdvlip'
import logging

root_logger = logging.getLogger('yota')
root_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s | %(message)s")


stderr_handler = logging.StreamHandler()
stderr_handler.setFormatter(formatter)

root_logger.addHandler(stderr_handler)

def get_logger(name):
    return logging.getLogger(name)