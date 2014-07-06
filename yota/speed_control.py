from datetime import datetime, timedelta

from yota import utils, config, web, current_speed_provider, exceptions, logging

__author__ = 'rdvlip'

class SpeedControl:

    def __init__(self):
        self.logger = logging.get_logger('yota.speed_control')
        self.current_mode = utils.mode_from_tariff(web.get_last_tariff())
        self.speed_downgrade_time = None
        self.speed_downgrade_start_state = None

    def run(self):
        self._speed_update_listener()

    def _start_downgrade(self):
        self.speed_downgrade_time = datetime.now() + timedelta(minutes=config['hold_high_speed_time'])
        self.speed_downgrade_start_state = current_speed_provider.get_state_stamp()

        self.logger.info('Downgrade started: {}'.format(self.speed_downgrade_time))

    def _process_downgrade(self):
        if self.speed_downgrade_start_state:
            self.speed_downgrade_time = None
            middle_speed = current_speed_provider.calculate_speed(current_speed_provider.get_state_stamp(), self.speed_downgrade_start_state)[2]
            new_mode = utils.nearest_num(middle_speed, config['modes'])
            self.logger.info('Downgrade processing. Middle speed: {}'.format(middle_speed))
            self._switch(new_mode)
            self.speed_downgrade_start_state = None
        else:
            raise exceptions.DowngradeIsNotInitialized

    def _cancel_downgrade(self):
        if self.speed_downgrade_start_state or self.speed_downgrade_time:
            self.logger.info('Downgrade cancelled')
            self.speed_downgrade_time = None
            self.speed_downgrade_start_state = None

    def _speed_update_listener(self):
        speed_update_event = current_speed_provider.get_new_lister_event()
        while True:
            speed_update_event.wait()
            speed_update_event.clear()
            speed = current_speed_provider.get_current_speed()
            summary_speed = speed[2]
            self._process_new_speed(summary_speed)

    def _process_new_speed(self, speed):
        new_mode = utils.nearest_num(speed, config['modes'])

        if new_mode < self.current_mode and not self.speed_downgrade_time:
            self._start_downgrade()
        elif new_mode > self.current_mode:
            self.logger.info('INCREASE')
            self._cancel_downgrade()
            self._switch(utils.calculate_mode_for_increase_speed(new_mode))
        elif self.speed_downgrade_time and new_mode >= self.current_mode:
            self._cancel_downgrade()
        elif self.speed_downgrade_time and self.speed_downgrade_time < datetime.now():
            self._process_downgrade()

    def _switch(self, mode):
        if mode != self.current_mode:
            new_yota_tariff = config['modes'][mode]
            self.logger.info('SWITCHING FROM: {} TO: {}'.format(config['modes'][self.current_mode], new_yota_tariff))
            web.change_tariff(new_yota_tariff)
            self.current_mode = mode
        else:
            self.logger.info('SWITCHING CANCEL. Already on requested mode')

speed_control = SpeedControl()