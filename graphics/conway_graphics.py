import tkinter as tk
import time

from metrics.component import Components

root = tk.Tk()
root.resizable(True, True)


class ConwayGraphics:
    ALIVE_COLOR = "#ffff00"
    DEAD_COLOR = "#000044"
    HIGHLIGHTED_COLOR = "#00ff00"

    def __init__(self, game, components=True):
        self.game = game
        self.canv = tk.Canvas(master=root, width=1000, height=1000*game.shape[0]/game.shape[1])
        self.canv.pack()
        self.components = Components(self.game) if components else None

    def draw(self):
        self.canv.delete("all")

        last_frame = self.game.grid[-1]
        grid_height, grid_width = self.game.shape

        components = self.components.get_components() if self.components else [[]]
        print(components)

        for x in range(grid_width):
            for y in range(grid_height):
                if last_frame[y][x]:
                    if (y, x) in components[0]:
                        color = ConwayGraphics.HIGHLIGHTED_COLOR
                    else:
                        color = ConwayGraphics.ALIVE_COLOR
                else:
                    color = ConwayGraphics.DEAD_COLOR

                self.canv.create_rectangle(x*self.canv.winfo_width()/grid_width,
                                           y*self.canv.winfo_height()/grid_height,
                                           (x+1)*self.canv.winfo_width()/grid_width,
                                           (y+1)*self.canv.winfo_height()/grid_height,
                                           fill=color)

    def run(self):
        while True:
            root.update_idletasks()
            self.draw()
            root.update()
            time.sleep(.1)
            self.game.advance()