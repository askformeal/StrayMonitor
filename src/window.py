import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import webbrowser
import json
import os

from src import main, __version__
from src.settings import Settings

from loguru import logger
from PIL import Image, ImageTk

class Window(tk.Tk):
    def __init__(self, root):
        super().__init__()
        self.root: main.Main = root
        self.settings = Settings()
        self.setup()
        logger.debug(f'Window module ({__name__}) initialized')

    def show_info(self, info: str):
        def save():
            types = [("Text Files", "*.txt"), ("All Files", "*.*")]
            path = filedialog.asksaveasfilename(parent=self, title='Save',
                                                initialfile='system-info.txt',
                                                filetypes=types)
            if path != '':
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(info.strip())
        def copy():
            self.clipboard_append(info)

        win = tk.Toplevel(self)
        win.title('System Info')
        win.iconbitmap(self.settings.DATA_PATHS['icon'])
        win.bind('<Control-s>', lambda event: save())

        text = scrolledtext.ScrolledText(win)

        text.config(state='normal')

        text.delete('1.0', 'end')
        text.insert('1.0', info)

        text.config(state='disabled')

        text.pack()

        fr = tk.Frame(win)
        fr.pack()

        btn = tk.Button(fr, text='Save', command=save)
        btn.pack(side='right')
        
        btn = tk.Button(fr, text='Copy', command=copy)
        btn.pack(side='right', padx=(0,10))

    def update_plot(self, images: tuple, cpu: int, mem: int):
        self.cpu_img = ImageTk.PhotoImage(images[0])
        self.cpu_plot.config(image=self.cpu_img)
        
        self.mem_img = ImageTk.PhotoImage(images[1])
        self.mem_plot.config(image=self.mem_img)
        
        self.cpu_lbl.config(text=f'CPU: {cpu}%')
        self.mem_lbl.config(text=f'Memory: {mem}%')

    def setup(self):
        def show_about():
            messagebox.showinfo('About', 
                                f'Stray Monitor {__version__}\n'\
                                'By Demons1014\n'\
                                'License: GPL v3.0'
                                )
            
        def show_license():
            with open(self.settings.DATA_PATHS['license'], 'r', encoding='utf-8') as f:
                l = f.read()
            win = tk.Toplevel(self)
            win.title('License')
            
            win.iconbitmap(self.settings.DATA_PATHS['icon'])

            text = scrolledtext.ScrolledText(win)
            text.pack(fill='both', expand=True)
            text.insert('1.0', l)

        def toggle_pin():
            self.pin = not self.pin
            self.attributes('-topmost', self.pin)

        def open_options():
            path = self.settings.PATHS['options']
            if os.path.exists(path):
                os.startfile(path)
            else:
                logger.error('option.json not found')
                if messagebox.askyesno('Error',
                                       'option.json not found'\
                                       'Create default option.json?'):
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(self.root.options.load_default(), f,
                                  indent=4)
                        
        def on_click(e: tk.Event):
            x_rate = self.settings.PLOT_SIZE_RATE[0]
            y_rate = self.settings.PLOT_SIZE_RATE[1]

            width = self.root.options.plot_len * x_rate
            height = 100 * y_rate

            x = round((width - e.x) / x_rate)
            y = round((height - e.y) / y_rate)

            self.pos_lbl.config(text=f'({x},{y})')

        def update_interval(n: int):
            self.root.interval = float(n)

        self.title(f'Stray Monitor {__version__} ({self.root.env})')
        # self.title('abc')

        self.iconbitmap(self.settings.DATA_PATHS['icon'])
        self.resizable(self.settings.RESIZABLE, self.settings.RESIZABLE)
        self.config(background='white')
        self.protocol('WM_DELETE_WINDOW', self.withdraw)
        self.pin = False
        toggle_pin()

        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label='Open options.json', command=open_options,
                              underline=0)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=lambda: self.root.exit(note='via menu',
                                                                             confirm=True), 
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

        fr = tk.Frame(self)
        fr.pack(fill='x')

        tmp = self.settings.CPU_LINE_COLOR
        tmp = f'#{tmp[0]:02X}{tmp[1]:02X}{tmp[2]:02X}'
        self.cpu_lbl = tk.Label(fr, text='CPU: 0%', fg=tmp,
                       relief='raised')
        self.cpu_lbl.pack(side='right', padx=(0,self.settings.LABEL_PAD))

        self.pin_image = Image.open(self.settings.DATA_PATHS['pin_img'])
        self.pin_image = ImageTk.PhotoImage(self.pin_image)

        btn = tk.Button(fr, image=self.pin_image, command=toggle_pin)
        btn.pack(side='left')

        self.actual_interval = tk.Label(fr, relief='raised')
        self.actual_interval.pack(side='left', padx=(5,0))

        scale = tk.Scale(fr, from_=0.0, to=3.0, orient='horizontal',
                         resolution=0.1, command=update_interval)
        scale.set(self.root.interval)
        scale.pack(side='left', pady=(0,13))


        self.pos_lbl = tk.Label(fr, text='(-,-)', relief='raised')
        self.pos_lbl.pack(side='left', padx=(10,10))

        self.cpu_plot = tk.Label(self)
        self.cpu_plot.pack(fill='both', expand=True,
                           pady=(0,5))
        self.cpu_plot.bind('<Button-1>', on_click)

        fr = tk.Frame(self)
        fr.pack(fill='x')

        tmp = self.settings.MEM_LINE_COLOR
        tmp = f'#{tmp[0]:02X}{tmp[1]:02X}{tmp[2]:02X}'
        self.mem_lbl = tk.Label(fr, text='Memory: 0%', fg=tmp,
                       relief='raised')
        self.mem_lbl.pack(side='right', padx=(0,self.settings.LABEL_PAD))
        
        self.mem_plot = tk.Label(self)
        self.mem_plot.pack(fill='both', expand=True,
                           pady=(0,5))
        self.mem_plot.bind('<Button-1>', on_click)

        self.withdraw()