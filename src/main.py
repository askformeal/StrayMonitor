from threading import Thread
from time import sleep
from tkinter import messagebox
from sys import argv
# kuchisake ornament
from src import __version__
from src.settings import Settings

from loguru import logger
from pystray import MenuItem, Icon
from PIL import Image, ImageDraw
import psutil

class Main:
    def __init__(self):
        self.settings = Settings()
        self.code = 0
        self.running = True
        logger.add(self.settings.PATHS['log'],
                   level=self.settings.LOG_LEVEL,
                   encoding='utf-8',
                   rotation=self.settings.LOG_MAX_BYTES,
                   colorize=False,
                   )
        # self.window = Window(self)
        if len(argv) > 1:
            monitor = argv[1].lower()
            if monitor not in ['cpu', 'mem', 'both']:
                self.exit(1, f'monitor must be \'cpu\', \'mem\' or \'both\', not \'{monitor}\'')
        else:
            monitor = 'both'
        logger.debug(f'Monitor: {monitor}')
        # monitor: 'cpu', 'mem', 'both'
        if monitor in ('cpu', 'both'):
            menu = (MenuItem('About', self.show_cpu, default=True, visible=False),
                    MenuItem('Exit', lambda: self.exit(note='via CPU stray')))
            self.cpu_icon = Icon('0%', self.gen_img(0), menu=menu)
            Thread(target=self.cpu_icon.run, daemon=True).start()
        if monitor in ('mem', 'both'):
            menu = (MenuItem('About', self.show_mem, default=True, visible=False),
                    MenuItem('Exit', lambda: self.exit(note='via Memory stray')))
            self.mem_icon = Icon('0%', self.gen_img(0), menu=menu)
            Thread(target=self.mem_icon.run, daemon=True).start()

        logger.debug(f'Main module ({__name__}) initialized')

    def show_cpu(self):
        sys_info = psutil.cpu_times()
        info = f'Usage: {psutil.cpu_percent()}%\n'\
               f'Cores: {psutil.cpu_count(logical=False)}\n'\
               f'Logical Cores: {psutil.cpu_count(logical=True)}\n'\
               f'CPU Time (System): {sys_info.system}\n'\
               f'CPU Time (User): {sys_info.user}'
        messagebox.showinfo('CPU Info', info)

    
    def show_mem(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        info = 'RAM:\n'\
               f'    Usage: {mem.percent}%\n'\
               f'    Total: {mem.total / (1024 ** 3):.3f} GB\n'\
               f'    Used: {mem.used / (1024 ** 3):.3f} GB\n'\
               f'    Free: {mem.free / (1024 ** 3):.3f} GB\n\n'\
               'Swap space:\n'\
               f'    Usage: {swap.percent}%\n'\
               f'    Total: {swap.total / (1024 ** 3):.3f} GB\n'\
               f'    Used: {swap.used / (1024 ** 3):.3f} GB\n'\
               f'    Free: {swap.free / (1024 ** 3):.3f} GB'
        messagebox.showinfo('Memory Info', info)

    def gen_img(self, rate: float) -> Image:
        size = self.settings.STRAY_SIZE
        image = Image.new('RGB', (size, size), color=self.settings.BACKGROUND)
        draw = ImageDraw.Draw(image)
        height = (size-1) - ((size-1) * rate)
        rect_pos = [(0, height), (size-1, size-1)]

        if rate < self.settings.MIDDLE_THRESHOLD:
            color = self.settings.LOW_COLOR
        elif rate >= self.settings.MIDDLE_THRESHOLD and rate < self.settings.HIGH_THRESHOLD:
            color = self.settings.MIDDLE_COLOR
        else:
            color = self.settings.HIGH_COLOR

        draw.rectangle(rect_pos, fill=color)

        tmp = height + self.settings.LINE_WIDTH
        if tmp > size-1:
            tmp = size-1
        rect_pos = [(0, height), (size-1, tmp)]
        draw.rectangle(rect_pos, fill=self.settings.LINE_COLOR)


        return image

    def start(self) -> int:
        logger.info(f'Start Stray Monitor {__version__}')
        # self.window.mainloop()
        while self.running:
            try:
                cpu_usage = psutil.cpu_percent()
                self.cpu_icon.icon = self.gen_img(cpu_usage/100)
                self.cpu_icon.title = f'CPU: {cpu_usage}%'

                mem = psutil.virtual_memory()
                mem.percent
                self.mem_icon.icon = self.gen_img(mem.percent/100)
                self.mem_icon.title = f'Memory: {mem.percent}% '\
                                      f'({mem.used / (1024 ** 3):.3f}/'\
                                      f'{mem.total / (1024 ** 3):.3f} GB)'

                sleep(self.settings.INTERVAL)
            except KeyboardInterrupt:
                self.exit(note='via keyboard interrupt')
        return self.code

    def exit(self, code = 0, note=''):
        self.code = code
        if self.code == 0:
            logger.info(f'Exit with code 0, {note}')
        else:
            
            logger.critical(f'Exit with code {self.code}, {note}')
        self.running = False