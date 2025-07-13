import sys
import os

class Settings:
    def __init__(self):
        self.GITHUB_REPO = 'https://github.com/askformeal/'

        self.SIZE_RATIO = 5/6 # Width/Height
        self.HEIGHT_RATE = 0.4 # Actual height = screen_height * HEIGHT_RATE
        self.RESIZABLE = True
        self.WIN_PADX = 70
        self.WIN_PADY = 70
        self.FONT = 'TkDefaultFont'

        self.BACKGROUND = (255, 255, 255)
        self.LINE_COLOR = (0, 0, 0)
        self.LOW_COLOR = (0, 255, 0)
        self.MIDDLE_COLOR = (255, 165, 0)
        self.HIGH_COLOR = (255, 0, 0)
        self.MIDDLE_THRESHOLD = 0.4
        self.HIGH_THRESHOLD = 0.7

        self.STRAY_SIZE = 64
        self.LINE_WIDTH = 3

        self.INTERVAL = 0.4

        self.LOG_LEVEL = 'DEBUG'
        self.LOG_MAX_BYTES = '10 MB'

        self.PATHS = {
            'log': './StrayMonitor.log',
            'options': './options.json'
        }
        
        work_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        for k,v in self.PATHS.items():
            self.PATHS[k] = os.path.join(work_dir, v)

        self.DATA_PATHS = {
            'icon': './data/app.ico',
            'license': './data/LICENSE',
        }
        for k,v in self.DATA_PATHS.items():
            self.DATA_PATHS[k] = self.resource_path(v)

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        path = os.path.join(base_path, relative_path)
        return path