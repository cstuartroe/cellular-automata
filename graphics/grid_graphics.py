import tkinter as tk
import imageio
from PIL import Image, ImageDraw
import numpy as np

import time
from random import randrange

from metrics.component import Components


class GridGraphics:
    GIF_REPEAT_FRAMES = 2

    def __init__(self, game, components=False, as_gif=False, gif_name=None, cell_width=10):
        self.game = game
        self.components = Components(self.game) if components else None
        self.as_gif = as_gif
        self.gif_name = gif_name
        self.cell_width = cell_width

        if as_gif:
            self.images = []
            self.current_image_draw = None
        else:
            self.root = tk.Tk()
            self.root.resizable(True, True)
            self.canv = tk.Canvas(master=self.root, width=1000, height=1000 * game.shape[0] / game.shape[1])
            self.canv.pack()

    def draw(self):
        if self.as_gif:
            im = Image.new("RGB", (
                self.game.shape[1]*self.cell_width,
                self.game.shape[0]*self.cell_width
            ))
            self.current_image_draw = ImageDraw.Draw(im)
            self.images.append(im)
        else:
            self.canv.delete("all")

        self.make_shapes()

    def make_shapes(self):
        raise NotImplementedError("Making shapes not yet implemented!")

    def draw_cell(self, color, x, y):
        grid_height, grid_width = self.game.shape

        if self.as_gif:
            start_x = x * self.cell_width
            start_y = y * self.cell_width
            end_x = (x+1) * self.cell_width - 2
            end_y = (y+1) * self.cell_width - 2
            self.current_image_draw.rectangle([start_x, start_y, end_x, end_y], fill=color)
        else:
            start_x = x * self.canv.winfo_width() / grid_width
            start_y = y * self.canv.winfo_height() / grid_height,
            end_x = (x + 1) * self.canv.winfo_width() / grid_width,
            end_y = (y + 1) * self.canv.winfo_height() / grid_height
            self.canv.create_rectangle(start_x, start_y, end_x, end_y, fill=color)

    def run(self, limit=None):
        i = 0
        while limit is None or i < limit:
            if not self.as_gif:
                self.root.update_idletasks()
                self.root.update()
                time.sleep(.1)

            self.draw()
            self.game.advance()
            i += 1

        if self.as_gif:
            with imageio.get_writer(self.gif_name, mode='I') as writer:
                for im in self.images:
                    for i in range(GridGraphics.GIF_REPEAT_FRAMES):
                        writer.append_data(np.array(im))


class ConwayGraphics(GridGraphics):
    ALIVE_COLOR = "#ffff00"
    DEAD_COLOR = "#000044"
    HIGHLIGHTED_COLOR = "#00ff00"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def make_shapes(self):
        last_frame = self.game.grid[-1]

        components = self.components.frame_components(-1) if self.components else [[]]

        for x in range(self.game.shape[1]):
            for y in range(self.game.shape[0]):
                if last_frame[y][x]:
                    color = ConwayGraphics.ALIVE_COLOR
                else:
                    color = ConwayGraphics.DEAD_COLOR

                self.draw_cell(color, x, y)

        for component in components:
            color = "#" + hex(randrange(256**3))[2:].ljust(6, '0')
            for y, x in component:
                self.draw_cell(color, x, y)


def rgb2hex(r, g, b):
    h = "#"
    for color in r, g, b:
        h += hex(int(color*255))[2:].rjust(2, '0')
    return h


class RedVsBlueGraphics(GridGraphics):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, components=False, **kwargs)

    def make_shapes(self):
        alive_cells = self.game.grid[-1, :, :, 0]
        cell_colors = self.game.grid[-1, :, :, 1]

        for x in range(self.game.shape[1]):
            for y in range(self.game.shape[0]):
                if alive_cells[y][x]:
                    if cell_colors[y][x] < 0:
                        red = 1
                        green = cell_colors[y][x] + 1
                        blue = green
                    else:
                        red = 1 - cell_colors[y][x]
                        green = red
                        blue = 1
                    color = rgb2hex(red, green, blue)
                else:
                    color = "#000000"

                self.draw_cell(color, x, y)
