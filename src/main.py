from threading import Thread
from time import sleep
import platform as pf
from datetime import datetime
from tkinter import messagebox

from sys import argv
from src import __version__
from src.settings import Settings
from src.window import Window

from loguru import logger
from pystray import MenuItem, Menu, Icon
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
        
        self.window = Window(self)
        
        if len(argv) > 1:
            monitor = argv[1].lower()
            if monitor not in ['cpu', 'mem', 'both']:
                self.exit(1, f'monitor must be \'cpu\', \'mem\' or \'both\', not \'{monitor}\'')
        else:
            monitor = 'both'
        
        logger.debug(f'Monitor: {monitor}')
        # monitor: 'cpu', 'mem', 'both'

        if monitor in ('mem', 'both'):
            menu = (MenuItem('Plot', self.window.deiconify, default=True),
                    MenuItem('System Info', self.show_info),
                    Menu.SEPARATOR,
                    MenuItem('Exit', lambda: self.exit(note='via Memory stray',
                                                       confirm=True)))
            self.mem_icon = Icon('0%', self.gen_img(0), menu=menu)
            Thread(target=self.mem_icon.run, daemon=True).start()

        if monitor in ('cpu', 'both'):
            menu = (MenuItem('Plot', self.window.deiconify, default=True),
                    MenuItem('System Info', self.show_info),
                    Menu.SEPARATOR,
                    MenuItem('Exit', lambda: self.exit(note='via CPU stray',
                                                       confirm=True)))
            self.cpu_icon = Icon('0%', self.gen_img(0), menu=menu)
            Thread(target=self.cpu_icon.run, daemon=True).start()
        

        self.cpu_plot = []
        self.mem_plot = []
        
        logger.debug(f'Main module ({__name__}) initialized')

    def show_info(self):
        sys_info = psutil.cpu_times()
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        freq = psutil.cpu_freq()
        users = ', '.join(list(map(lambda user: user.name, psutil.users())))
        info = f'System Info {str(datetime.now())}\n\n\n'\
               'General:\n'\
               f'    Name: {pf.node()}\n'\
               f'    Users: {users}\n'\
               f'    Operating System: {pf.platform()}\n'\
               f'    Architecture: {pf.architecture()[0]}\n\n'\
               f'    Process: {len(psutil.pids())}\n'\
               'CPU:\n'\
               f'    Model: {pf.processor()}\n'\
               f'    Usage: {psutil.cpu_percent()}%\n'\
               f'    Cores: {psutil.cpu_count(logical=False)}\n'\
               f'    Logical Cores: {psutil.cpu_count(logical=True)}\n'\
                '    Frequency:\n'\
               f'        Current: {freq.current}\n'\
               f'        Min: {freq.min}\n'\
               f'        Max: {freq.max}\n'\
               f'    CPU Time (System): {sys_info.system}\n'\
               f'    CPU Time (User): {sys_info.user}\n\n'\
               'RAM:\n'\
               f'    Usage: {mem.percent}%\n'\
               f'    Total: {mem.total / (1024 ** 3):.3f} GB\n'\
               f'    Used: {mem.used / (1024 ** 3):.3f} GB\n'\
               f'    Free: {mem.free / (1024 ** 3):.3f} GB\n\n'\
               'Swap space:\n'\
               f'    Usage: {swap.percent}%\n'\
               f'    Total: {swap.total / (1024 ** 3):.3f} GB\n'\
               f'    Used: {swap.used / (1024 ** 3):.3f} GB\n'\
               f'    Free: {swap.free / (1024 ** 3):.3f} GB\n\n'\
               'Disks:\n'
        
        for partition in psutil.disk_partitions():
            disk = psutil.disk_usage(partition.device)
            info += f'    {partition.device}\n'\
                    f'        Usage: {disk.percent}%\n'\
                    f'        Total: {disk.total / (1024 ** 3):.2f} GB\n'\
                    f'        Used: {disk.used / (1024 ** 3):.2f} GB\n'\
                    f'        Free: {disk.free / (1024 ** 3):.2f} GB\n'
        
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        
        info += '    IO:\n'\
                f'       Read: {disk_io.read_bytes / (1024 ** 2):.2f} MB\n'\
                f'       Write: {disk_io.write_bytes / (1024 ** 2):.2f} MB\n\n'\
                f'Network:\n'\
                f'    IO:\n'\
                f'        Send: {net_io.bytes_sent / (1024 ** 2):.2f} MB\n'\
                f'        Receive: {net_io.bytes_recv / (1024 ** 2):.2f} MB\n\n'\
                f'    Interfaces:\n'
        
        for interface, addrs in psutil.net_if_addrs().items():
            info += f'        {interface}:\n'
            for addr in addrs:
                info += f'            {addr.family.name}: {addr.address}\n'
            info += '\n'

        info = f'{info.strip()}\n'

        self.window.show_info(info)

    def gen_plot_img(self, cpu: list[int], mem: list[int]) -> tuple:
        def gen_img(l: list, line_color, fill_color):
            plot_len = self.settings.PLOT_LEN
            x_rate = self.settings.PLOT_SIZE_RATE[0]
            y_rate = self.settings.PLOT_SIZE_RATE[1]

            width = int(plot_len * x_rate)
            height = int(100 * y_rate)

            image = Image.new('RGB', (width, height), color=self.settings.PLOT_BG)
            draw = ImageDraw.Draw(image)
            
            spacing = width // self.settings.X_GRID_NUM-1
            if self.settings.X_GRID:
                for i in range(1, self.settings.X_GRID_NUM+1):
                    x = i * spacing
                    draw.line([(x, 0), (x, height)], 
                              fill=self.settings.GRIDE_COLOR,
                              width=self.settings.GRIDE_WIDTH)

            spacing = height // self.settings.Y_GRID_NUM-1
            if self.settings.Y_GRID:
                for i in range(1, self.settings.Y_GRID_NUM+1):
                    y = i * spacing
                    draw.line([(0, y), (width, y)],
                              fill=self.settings.GRIDE_COLOR,
                              width=self.settings.GRIDE_WIDTH)
            
            draw.rectangle([(0,0), (width-1, height-1)], width=1, 
                           outline=self.settings.GRIDE_COLOR)

            # image = image.transpose(Image.FLIP_TOP_BOTTOM)
            
            for i in range(plot_len-1):
                draw.line([(i*x_rate, l[i]*y_rate), ((i+1)*x_rate, l[i+1]*y_rate)],
                        fill=line_color,
                        width=self.settings.PLOT_LINE_WIDTH)
                points = [(i*x_rate, l[i]*y_rate), ((i+1)*x_rate, l[i+1]*y_rate),
                        ((i+1)*x_rate, 0), (i*x_rate, 0)]
                draw.polygon(points, fill=fill_color)
            
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            return image

        plot_len = self.settings.PLOT_LEN
        cpu = (([0] * plot_len) + cpu)[-plot_len:]
        mem = (([0] * plot_len) + mem)[-plot_len:]
        # [0,0,0,0,0,0,0,0,0,0] + [1,2,3] -> [0,0,0,0,0,0,0,1,2,3]

        cpu_image = gen_img(cpu, self.settings.CPU_LINE_COLOR,
                            self.settings.CPU_FILL_COLOR)
        mem_image = gen_img(mem, self.settings.MEM_LINE_COLOR,
                            self.settings.MEM_FILL_COLOR)
        
        return (cpu_image, mem_image)

    def gen_img(self, rate: float) -> Image:
        size = self.settings.STRAY_SIZE
        image = Image.new('RGB', (size, size), color=self.settings.ICON_BG)
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

    def update(self):
        while self.running:
            try:
                cpu_usage = psutil.cpu_percent()
                self.cpu_icon.icon = self.gen_img(cpu_usage/100)
                self.cpu_icon.title = f'CPU: {cpu_usage}%'

                self.cpu_plot.append(cpu_usage)
                if len(self.cpu_plot) > self.settings.PLOT_LEN:
                    self.cpu_plot = self.cpu_plot[1:]

                mem = psutil.virtual_memory()
                mem.percent
                self.mem_icon.icon = self.gen_img(mem.percent/100)
                self.mem_icon.title = f'Memory: {mem.percent}% '\
                                    f'({mem.used / (1024 ** 3):.3f}/'\
                                    f'{mem.total / (1024 ** 3):.3f} GB)'
                
                self.mem_plot.append(mem.percent)
                if len(self.mem_plot) > self.settings.PLOT_LEN:
                    self.mem_plot = self.mem_plot[1:]

                try:
                    self.window.update_plot(self.gen_plot_img(self.cpu_plot, self.mem_plot),
                                            self.cpu_plot[-1], self.mem_plot[-1])
                except RuntimeError:
                    ...
                sleep(self.settings.INTERVAL)
            except KeyboardInterrupt:
                self.exit(note='via keyboard interrupt')

    def start(self) -> int:
        logger.info(f'Start Stray Monitor {__version__}')
        Thread(target=self.update, daemon=True).start()
        try:
            self.window.mainloop()
        except KeyboardInterrupt:
            self.exit(note='via keyboard interrupt')
        return self.code

    def exit(self, code = 0, note='', confirm=False):
        flag = True
        if confirm:
            flag = messagebox.askyesno('Exit', 'Exit StrayMonitor?')
        if flag:
            self.code = code
            if self.code == 0:
                logger.info(f'Exit with code 0, {note}')
            else:

                logger.critical(f'Exit with code {self.code}, {note}')
            self.window.destroy()
            self.window.quit()
            self.running = False