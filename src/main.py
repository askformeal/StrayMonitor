from threading import Thread
from time import sleep
import platform as pf
from datetime import datetime
from tkinter import TclError
from tkinter import messagebox

from sys import argv
from src import __version__, is_release
from src.settings import Settings
from src.option import Option
from src.window import Window
from src.gen_img import GenImg

from loguru import logger
from pystray import MenuItem, Menu, Icon
import psutil

class Main:
    def __init__(self):
        self.settings = Settings()
        self.code = 0
        self.running = True
        if is_release:
            self.env = 'Release'
        else:
            self.env = 'Develop'
        self.interval = self.settings.INITIAL_INTERVAL

        logger.add(self.settings.PATHS['log'],
                   level=self.settings.LOG_LEVEL,
                   encoding='utf-8',
                   rotation=self.settings.LOG_MAX_BYTES,
                   colorize=False,
                   )
    
        self.options = Option(self)
        self.window = Window(self)


        self.generator = GenImg(self)
        print(self is self.generator.root)
        
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
            self.mem_icon = Icon('0%', self.generator.gen_img(0), menu=menu)
            Thread(target=self.mem_icon.run, daemon=True).start()

        if monitor in ('cpu', 'both'):
            menu = (MenuItem('Plot', self.window.deiconify, default=True),
                    MenuItem('System Info', self.show_info),
                    Menu.SEPARATOR,
                    MenuItem('Exit', lambda: self.exit(note='via CPU stray',
                                                       confirm=True)))
            self.cpu_icon = Icon('0%', self.generator.gen_img(0), menu=menu)    
            Thread(target=self.cpu_icon.run, daemon=True).start()

        self.cpu_plot = []
        self.mem_plot = []
        self.pre_stamp = datetime.now().timestamp()

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

    def update(self):
        while self.running:
            try:
                if self.env == 'Develop':
                    tmp = ' (Develop)'
                else:
                    tmp = ''

                cpu_usage = psutil.cpu_percent()
                self.cpu_icon.icon = self.generator.gen_img(cpu_usage/100)
                self.cpu_icon.title = f'CPU: {cpu_usage}%{tmp}'

                self.cpu_plot.append(cpu_usage)
                if len(self.cpu_plot) > self.options.plot_len:
                    self.cpu_plot = self.cpu_plot[1:]

                mem = psutil.virtual_memory()
                self.mem_icon.icon = self.generator.gen_img(mem.percent/100)
                self.mem_icon.title = f'Memory: {mem.percent}% '\
                                    f'({mem.used / (1024 ** 3):.3f}/'\
                                    f'{mem.total / (1024 ** 3):.3f} GB){tmp}'
                self.mem_plot.append(mem.percent)
                if len(self.mem_plot) > self.options.plot_len:
                    self.mem_plot = self.mem_plot[1:]
                try:
                    self.window.update_plot(self.generator.gen_plot_img(self.cpu_plot, self.mem_plot),
                                            self.cpu_plot[-1], self.mem_plot[-1])
                
                except RuntimeError:
                    ...
                sleep(self.interval)
                now_stamp = datetime.now().timestamp()
                actual_interval = round(now_stamp - self.pre_stamp, 3)
                self.pre_stamp = now_stamp
                self.window.actual_interval.config(text='Interval: '\
                                                        f'{str(actual_interval):.4}')

            except KeyboardInterrupt:
                self.exit(note='via keyboard interrupt')
            except TclError as e:
                logger.error(f'TclError: {e}')

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