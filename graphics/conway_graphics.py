import tkinter as tk
import imageio
from PIL import Image, ImageDraw

import time
from random import randrange

from metrics.component import Components


class GridGraphics:
    GIF_CELL_WIDTH = 10
    GIF_REPEAT_FRAMES = 2

    def __init__(self, game, components=False, as_gif=False, gif_name=None):
        self.game = game
        self.components = Components(self.game) if components else None
        self.as_gif = as_gif
        self.gif_name = gif_name

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
                self.game.shape[1]*GridGraphics.GIF_CELL_WIDTH,
                self.game.shape[0]*GridGraphics.GIF_CELL_WIDTH
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
            start_x = x * GridGraphics.GIF_CELL_WIDTH
            start_y = y * GridGraphics.GIF_CELL_WIDTH
            end_x = (x+1) * GridGraphics.GIF_CELL_WIDTH - 2
            end_y = (y+1) * GridGraphics.GIF_CELL_WIDTH - 2
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
                    im.save("test.png")
                    for i in range(GridGraphics.GIF_REPEAT_FRAMES):
                        writer.append_data(imageio.imread("test.png"))


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