import json
import os

from src import main
from src.settings import Settings

from loguru import logger

class Option:
    def __init__(self, root):
        self.root: main.Main = root
        self.settings = Settings()
        
        self.stray_size: int
        self.bubble: bool
        self.plot_len: int
        self.load()

        logger.debug(f'Option module ({__name__}) initialized')

    def load_default(self) -> dict:
        with open(self.settings.DATA_PATHS['default_options'],
                    'r', encoding='utf-8') as f:
            return json.load(f)
    def load(self):        
        def decode(op: dict):
            try:
                if type(op['stray_icon_side_len']) == int:
                    self.stray_size = op['stray_icon_side_len']
                else:
                    raise TypeError('bubble must be a bool')
                
                if type(op['bubble']) == bool:
                    self.bubble = op['bubble']
                else:
                    raise TypeError('bubble must be a bool')
                
                if type(op['plot_width']) == int:
                    self.plot_len = op['plot_width']
                else:
                    raise TypeError('plot_width must be an int')
                
            except (KeyError, TypeError) as e:
                if type(e) == KeyError:
                    logger.error(f'Missing key: {e} in {filename}, load default options')
                else:
                    logger.error(f'Invalid {filename}, {e}')
                decode(self.load_default())

        filename = os.path.basename(self.settings.PATHS['options'])
        try:
            with open(self.settings.PATHS['options'],
                      'r', encoding='utf-8') as f:
                options = json.load(f)
        except FileNotFoundError:
            logger.info(f'{filename} not found, load default options')
            options = self.load_default()
        decode(options)
