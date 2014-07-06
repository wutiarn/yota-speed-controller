import yaml
from os.path import dirname, join

base_dir = dirname(dirname(__file__))

config_path = join(base_dir, 'config.yaml')
with open(config_path) as file:
    config = yaml.load(open(config_path))