from random import randint

from src import main
from src.settings import Settings

from loguru import logger
from PIL import Image, ImageDraw, ImageFont

class GenImg:
    def __init__(self, root):
        self.root: main.Main = root
        self.settings = Settings()
        logger.debug(f'Image Generator module ({__name__}) initialized')

    def gen_img(self, rate: float) -> Image:
        size = self.root.options.stray_size
        image = Image.new('RGB', (size, size), color=self.settings.ICON_BG)
        draw = ImageDraw.Draw(image)
        height = (size-1) - ((size-1) * rate)
        rect_pos = [(0, height), (size-1, size-1)]

        if rate < self.settings.MIDDLE_THRESHOLD:
            color = self.settings.LOW_COLOR
            bubble_color = self.settings.BUBBLE_COLOR_LOW
        elif rate >= self.settings.MIDDLE_THRESHOLD and rate < self.settings.HIGH_THRESHOLD:
            color = self.settings.MIDDLE_COLOR
            bubble_color = self.settings.BUBBLE_COLOR_MIDDLE
        else:
            color = self.settings.HIGH_COLOR
            bubble_color = self.settings.BUBBLE_COLOR_HIGH

        draw.rectangle(rect_pos, fill=color)

        tmp = height + self.settings.LINE_WIDTH
        if tmp > size-1:
            tmp = size-1
        rect_pos = [(0, height), (size-1, tmp)]

        if self.root.options.bubble:
            for i in range(self.settings.BUBBLE_NUM):
                x = randint(0, size-1)
                y = randint(int(height), size-1)
                tmp = self.settings.BUBBLE_SIZE
                draw.rectangle([(x, y), (x+tmp, y+tmp)],
                            fill=bubble_color,
                            outline=bubble_color)

        draw.rectangle(rect_pos, fill=self.settings.LINE_COLOR)

        return image

    def gen_plot_img(self, cpu: list[int], mem: list[int]) -> tuple:
        def gen_img(l: list, line_color, fill_color):
            plot_len = self.root.options.plot_len
            x_rate = self.settings.PLOT_SIZE_RATE[0]
            y_rate = self.settings.PLOT_SIZE_RATE[1]

            width = int(plot_len * x_rate)
            height = int(100 * y_rate)

            plot_image = Image.new('RGB', (width, height), color=self.settings.PLOT_BG)
            draw = ImageDraw.Draw(plot_image)


            # ------------------ Range Colors ------------------
            if self.settings.DRAW_RANGE_COLOR:
                tmp1 = self.settings.MIDDLE_THRESHOLD * 100 * y_rate
                draw.rectangle([(0, 0), (width, tmp1)], 
                               fill=self.settings.LOW_COLOR)
                

                tmp2 = self.settings.HIGH_THRESHOLD * 100 * y_rate
                draw.rectangle([(0, tmp1), (width, tmp2)], 
                               fill=self.settings.MIDDLE_COLOR)
                
                draw.rectangle([(0, tmp2), (width, height)], 
                               fill=self.settings.HIGH_COLOR)

            # ------------------ Grid ------------------
            if self.settings.X_GRID:
                for i in range(0, plot_len+1, self.settings.X_GRID_STEP):
                    x = i * x_rate
                    draw.line([(x, 0), (x, height)], 
                              fill=self.settings.GRIDE_COLOR,
                              width=self.settings.GRIDE_WIDTH)

            if self.settings.Y_GRID:
                for i in range(0, 101, self.settings.Y_GRID_STEP):
                    y = i * y_rate
                    draw.line([(0, y), (width, y)],
                              fill=self.settings.GRIDE_COLOR,
                              width=self.settings.GRIDE_WIDTH)
            
            draw.rectangle([(0,0), (width-1, height-1)], width=1, 
                           outline=self.settings.GRIDE_COLOR)

            # image = image.transpose(Image.FLIP_TOP_BOTTOM)
            
            # ------------------ Plot ------------------

            for i in range(plot_len-1):
                points = [(i*x_rate, l[i]*y_rate), ((i+1)*x_rate+1, l[i+1]*y_rate)]

                draw.line(points,
                        fill=line_color,
                        width=self.settings.PLOT_LINE_WIDTH)
                points = points + [((i+1)*x_rate+1, 0), (i*x_rate, 0)]
                draw.polygon(points, fill=fill_color)
            
            plot_image = plot_image.transpose(Image.FLIP_TOP_BOTTOM)

            # ------------------ Scale ------------------

            font = ImageFont.load_default()
            scale_height = height+self.settings.SCALE_HEIGHT_EXCESS
            scale_image = Image.new('RGB', 
                                    (self.settings.SCALE_WIDTH, scale_height), 
                                    color=self.settings.PLOT_BG)
            
            draw_scale = ImageDraw.Draw(scale_image)
            if self.settings.Y_GRID:
                for i in range(0, 101, self.settings.Y_GRID_STEP):
                    y = height-(i * y_rate)
                    # print(i, y)
                    draw_scale.text((self.settings.SCALE_PAD, y), 
                                    str(i), font=font,
                                    fill=self.settings.SCALE_COLOR)
            # sys.exit()

            image = Image.new('RGB', 
                              (width+self.settings.SCALE_WIDTH, scale_height),
                              color=self.settings.PLOT_BG)
            image.paste(plot_image, (0, 0))
            image.paste(scale_image, (width, 0))
            return image

        plot_len = self.root.options.plot_len
        cpu = (([0] * plot_len) + cpu)[-plot_len:]
        mem = (([0] * plot_len) + mem)[-plot_len:]
        # [0,0,0,0,0,0,0,0,0,0] + [1,2,3] -> [0,0,0,0,0,0,0,1,2,3]

        cpu_image = gen_img(cpu, self.settings.CPU_LINE_COLOR,
                            self.settings.CPU_FILL_COLOR)
        mem_image = gen_img(mem, self.settings.MEM_LINE_COLOR,
                            self.settings.MEM_FILL_COLOR)
        
        return (cpu_image, mem_image)