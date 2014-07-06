import re
from yota import utils
__author__ = 'rdvlip'

def _clear_slider_data(string):
    return re.findall('var sliderData.*};', string)[0]

def parse_html_for_tariffs(string):
    string =_clear_slider_data(string)
    string = re.findall('"steps":\[.+?\]', string)[0]

    codes = re.findall('POS-MA[\d]+-[\d]{4}', string)[1:]
    speeds = re.findall('"speedNumber":".+?",', string)[1:]

    for i, speed in enumerate(speeds):
        speed = re.findall('[\d\.]+|max', speed)[0]
        speed = utils.string_to_speed(speed)
        speeds[i] = speed

    return dict(zip(speeds, codes))

def parse_html_for_current_tariff(string):
    string =_clear_slider_data(string)
    string = re.findall('"currentProduct":{.+?}', string)[0]
    speed = re.findall('"speedNumber":".+?",', string)[0]
    speed = re.findall('[\d\.]+|max', speed)[0]
    speed = utils.string_to_speed(speed)
    return speed

def parse_html_for_product_id(string):
    string = re.findall('"productId":[\d]+', string)[0]
    string = re.findall('[\d]+', string)[0]
    return string
