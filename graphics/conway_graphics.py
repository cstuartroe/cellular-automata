import tkinter as tk
import time

from games import Conway

root = tk.Tk()
root.resizable(True, True)


class ConwayGraphics:
    ALIVE_COLOR = "#ffff00"
    DEAD_COLOR = "#000044"

    def __init__(self, game):
        self.game = game
        self.canv = tk.Canvas(master=root, width=600, height=600)
        self.canv.pack()

    def draw(self):
        self.canv.delete("all")

        last_frame = self.game.grid[-1]
        grid_width, grid_height = self.game.grid.shape[1:3]

        for x in range(grid_width):
            for y in range(grid_height):
                color = ConwayGraphics.ALIVE_COLOR if last_frame[y][x] else ConwayGraphics.DEAD_COLOR
                self.canv.create_rectangle(x*self.canv.winfo_width()/grid_width,
                                           y*self.canv.winfo_height()/grid_height,
                                           (x+1)*self.canv.winfo_width()/grid_width,
                                           (y+1)*self.canv.winfo_height()/grid_height,
                                           fill=color)

    def run(self):
        while True:
            self.draw()
            root.update()
            self.game.advance()