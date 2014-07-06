__author__ = 'rdvlip'

import requests
from yota import config

def send_notification(title, body):
    if config['pb_enabled']:
        auth = (config['pb_api'], '')
        for device_id in config['pb_devices']:
            data = {
                'device_iden': device_id,
                'type': 'note',
                'title': title,
                'body': body
            }
            requests.post('https://api.pushbullet.com/v2/pushes', data=data, auth=auth)

def notify_tariff_changed(old, new):
    send_notification(
        'Изменение тарифа Yota',
        'Тариф был изменен с {} на {}'.format(old, new)
    )