import sys
import os

class Settings:
    def __init__(self):
        self.GITHUB_REPO = 'https://github.com/askformeal/'

        self.SIZE_RATIO = 5/6 # Width/Height
        self.HEIGHT_RATE = 0.4 # Actual height = screen_height * HEIGHT_RATE
        self.RESIZABLE = False
        self.WIN_PADX = 70
        self.WIN_PADY = 70
        self.FONT =  'TkDefaultFont'

        self.INITIAL_INTERVAL = 0.3

        self.BG = (255, 255, 255)

        self.ICON_BG = (255, 255, 255)
        self.LINE_COLOR = (0, 0, 0)
        self.LOW_COLOR = (0, 255, 0)
        self.MIDDLE_COLOR = (255, 165, 0)
        self.HIGH_COLOR = (255, 0, 0)
        self.MIDDLE_THRESHOLD = 0.4
        self.HIGH_THRESHOLD = 0.7

        self.LINE_WIDTH = 12

        self.BUBBLE_COLOR_LOW = (0, 200, 0)
        self.BUBBLE_COLOR_MIDDLE = (200, 130, 0)
        self.BUBBLE_COLOR_HIGH = (200, 0, 0)
        self.BUBBLE_NUM = 10
        self.BUBBLE_SIZE = 40
        self.PLOT_SIZE_RATE = (3, 1.5)

        self.PLOT_BG = self.BG
        
        self.CPU_LINE_COLOR = (0, 255, 0)
        self.CPU_FILL_COLOR = (0, 150, 0)
        
        self.MEM_LINE_COLOR = (0, 0, 255)
        self.MEM_FILL_COLOR = (0, 0, 150)

        self.DRAW_RANGE_COLOR = False

        self.PLOT_LINE_WIDTH = 3

        self.LABEL_PAD = 5

        self.X_GRID = True
        self.X_GRID_STEP = 20
        self.Y_GRID = True
        self.Y_GRID_STEP = 10

        self.GRIDE_WIDTH = 1
        self.GRIDE_COLOR = (100, 100, 100)

        self.SCALE_WIDTH = 25
        self.SCALE_HEIGHT_EXCESS = 10
        self.SCALE_PAD = 3
        self.SCALE_COLOR = (0, 0, 0)

        self.LOG_LEVEL = 'DEBUG'
        self.LOG_MAX_BYTES = '10 MB'

        self.PATHS = {
            'log': './StrayMonitor.log',
            'options': './options.json'
        }
        # work_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        # for k,v in self.PATHS.items():
        #     self.PATHS[k] = os.path.join(work_dir, v)

        self.DATA_PATHS = {
            'default_options': './data/default_options.json',
            'icon': './data/app.ico',
            'license': './data/LICENSE',
            'pin_img': './data/pin.png'
        }
        # for k,v in self.DATA_PATHS.items():
        #     self.DATA_PATHS[k] = self.resource_path(v)

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            print(1)
            base_path = sys._MEIPASS
        else:
            print(2)
            base_path = os.path.abspath(".")
        path = os.path.join(base_path, relative_path)
        return path