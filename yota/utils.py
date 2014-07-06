__author__ = 'rdvlip'
from yota import config

def nearest_num(n, nums_dict):
    nums_dict = sorted(nums_dict)
    for i, j in enumerate(nums_dict):
        if n < j:
            return nums_dict[i-1]
    return nums_dict[-1]

def string_to_speed(string):
    if string == 'max':
        return 20.0
    elif '.' in string:
        speed = float(string)
    else:
        speed = int(string)
    return speed

def mode_from_tariff(tariff):
    modes = config['modes']
    for mode in modes:
        if modes[mode] == tariff:
            return mode

def calculate_mode_for_increase_speed(standart_mode):
    modes_list = list(config['modes'].keys())
    modes_list.sort()
    current_index = modes_list.index(standart_mode)
    last_index = len(modes_list) - 1
    for n in reversed(range(config['speed_increase_step'])):
        if last_index >= current_index + n:
            return modes_list[current_index + n]