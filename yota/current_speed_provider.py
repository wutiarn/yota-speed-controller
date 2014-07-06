import re
import sh
import datetime
from time import sleep
from collections import deque
import threading

from yota import config, logging

logger = logging.get_logger('yota.current_speed_provider')


def _parse_ifconfig(string):
    rx_re = re.compile('RX bytes:[\d]*')
    tx_re = re.compile('TX bytes:[\d]*')
    bytes_re = re.compile('[\d][0-9]+')

    rx = rx_re.findall(string)[0]
    tx = tx_re.findall(string)[0]

    rx = bytes_re.findall(rx)[0]
    tx = bytes_re.findall(tx)[0]

    rx = int(rx)
    tx = int(tx)

    return rx, tx

def _get_current_statistics(interface, cl):
    return _parse_ifconfig(str(cl.ifconfig(interface)))

def calculate_speed(state, last_state):
    time_delta = (state[1] - last_state[1]).seconds

    rx_delta = state[0][0] - last_state[0][0]
    tx_delta = state[0][1] - last_state[0][1]

    rx_speed = int(rx_delta / time_delta / 1024 * 8)
    tx_speed = int(tx_delta / time_delta / 1024 * 8)
    sum_speed = tx_speed + rx_speed

    return rx_speed, tx_speed, sum_speed, time_delta

def get_state_stamp():
    if config['use_ssh']:
        cl = sh.Command('ssh').bake(config['ssh_config']['host'], p=config['ssh_config']['port'], l=config['ssh_config']['login'])
    else:
        cl = sh

    interface = config['interface']

    return _get_current_statistics(interface, cl), datetime.datetime.now()


def _calculate_current_speed(current_speed, speed_update_events):

    state = get_state_stamp()
    sleep(config['speed_test_length'])

    while True:
        last_state = state
        sleep(config['speed_test_length'])

        state = get_state_stamp()

        calculated_speed = calculate_speed(state, last_state)
        rx_speed, tx_speed, sum_speed, time_delta = calculated_speed

        logger.debug('Current speed: RX: {} TX: {}. Summary: {}, Time: {}'.format(rx_speed, tx_speed, sum_speed, time_delta))

        current_speed.append(calculated_speed)
        for e in speed_update_events:
            e.set()

_current_speed = deque(maxlen=1)
_speed_update_events = []

def get_current_speed():
    return _current_speed[0]

def get_new_lister_event():
    event = threading.Event()
    _speed_update_events.append(event)
    return event

def remove_listener_event(event):
    index = _speed_update_events.index(event)
    del _speed_update_events[index]

def run():
    t = threading.Thread(target=_calculate_current_speed, args=(_current_speed, _speed_update_events))
    t.daemon = True
    t.start()