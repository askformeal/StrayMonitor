import tkinter as tk
from tkinter import messagebox, scrolledtext
import webbrowser

from src import main, __version__
from src.settings import Settings

from loguru import logger

class Window(tk.Tk):
    def __init__(self, root):
        super().__init__()
        self.root: main.Main = root
        self.settings = Settings()
        self.setup()
        logger.debug(f'Window module ({__name__}) initialized')

    def setup(self):
        def show_about():
            messagebox.showinfo('关于', 
                                f'Stray Monitor {__version__}\n'\
                                '作者: Demons1014\n'\
                                '许可证: GPL v3.0'
                                )
            
        def show_license():
            with open(self.settings.DATA_PATHS['license'], 'r', encoding='utf-8') as f:
                l = f.read()
            win = tk.Toplevel(self)
            win.title('许可证')
            
            win.iconbitmap(self.settings.DATA_PATHS['icon'])

            text = scrolledtext.ScrolledText(win)
            text.pack(fill='both', expand=True)
            text.insert('1.0', l)

        self.title(f'Stray Monitor {__version__}')
        height = int(self.winfo_screenheight() * self.settings.HEIGHT_RATE)
        width = int(self.settings.SIZE_RATIO * height)
        self.geometry(f'{width}x{height}+{self.settings.WIN_PADX}+{self.settings.WIN_PADY}')
        self.iconbitmap(self.settings.DATA_PATHS['icon'])
        self.config(background='white')

        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=lambda: self.root.exit(note='via menu'), 
                              underline=0)
        
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label='Github Repo', 
                              command=lambda: webbrowser.open(self.settings.GITHUB_REPO),
                              underline=0)
        help_menu.add_command(label='License', command=show_license, underline=0)
        help_menu.add_separator()
        help_menu.add_command(label='About', command=show_about, underline=0)

        menubar.add_cascade(label='File', menu=file_menu, underline=0)
        menubar.add_cascade(label='Help', menu=help_menu, underline=0)