import requests
from yota import exceptions, config, parser, logging, pb

__author__ = 'rdvlip'

class Web:
    def __init__(self):
        self.logger = logging.get_logger('yota.web')
        self.cookies = None
        self._auth()
        self.tariffs = self._get_tariffs()
        self.last_tariff = self.get_current_tariff()

    def _auth(self):
        if self.cookies and self._check_cookie():
            return True

        login_data = {
           'IDToken1': config['yota_credentials']['login'],
           'IDToken2': config['yota_credentials']['password'],
           'goto': 'https://my.yota.ru:443/selfcare/loginSuccess',
           'old-token': '',
           'org': 'customer'
        }
        r = requests.post('https://login.yota.ru/UI/Login', data=login_data, allow_redirects=False)
        self.cookies = dict(r.cookies)

        if not self._check_cookie():
            raise exceptions.LoginFailed

        return True

    def _check_cookie(self):
        r = requests.get('https://my.yota.ru/selfcare/devices', cookies=self.cookies)
        return r.url == 'https://my.yota.ru/selfcare/devices' and r.status_code == 200

    def _get(self, url):
        r = requests.get(url, cookies=self.cookies)
        if not r.url == url and r.status_code == 200:
            self._auth()
            r = requests.get(url, cookies=self.cookies)
        return r

    def _post(self, url, data):
        self._auth()
        r = requests.post(url, data=data, cookies=self.cookies)
        return r


    def _get_main_page(self):
        r = self._get('https://my.yota.ru/selfcare/devices')
        return r

    def _get_main_page_content(self):
        return self._get_main_page().text

    def _get_tariffs(self):
        return parser.parse_html_for_tariffs(self._get_main_page_content())

    def get_tariffs(self):
        return self.tariffs

    def get_current_tariff(self):
        result = self.last_tariff = parser.parse_html_for_current_tariff(self._get_main_page_content())
        self.logger.info('CURRENT TARIFF: {}'.format(result))
        return result

    def get_last_tariff(self):
        return self.last_tariff

    def _get_product_id(self):
        return parser.parse_html_for_product_id(self._get_main_page_content())

    def change_tariff(self, tariff):
        if tariff != self.last_tariff:
            self._change_tariff(tariff)

    def _change_tariff(self, new_tariff):
        yota_tariff_code = self.tariffs[new_tariff]
        self.logger.info('Switch: {} ({})'.format(yota_tariff_code, new_tariff))
        post_data = {
            'product': self._get_product_id(),
            'offerCode': yota_tariff_code,
            'areOffersAvailable': 'false',
            'status': 'custom',
            'autoprolong': 1,
            'isSlot': 'false',
            'currentDevice': 1,
            'isDisablingAutoprolong': 'false'
        }
        r = self._post('https://my.yota.ru/selfcare/devices/changeOffer', post_data)
        self.logger.info('Switching done')

        old_tariff = self.last_tariff

        if not new_tariff == self.get_current_tariff():
            raise exceptions.TariffChangeError
        else:
            self.logger.info('Tariff switched successfully')
            pb.notify_tariff_changed(old_tariff, new_tariff)

        return r
web = Web()