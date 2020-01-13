import random
import numpy as np
from .game import CellSpec, Game


class Conway(Game):
    GRID_DIMENSIONS = 2
    CELL_SPEC = CellSpec([
        {0, 1}
    ])

    def __init__(self, width, height, survive=[2, 3], spawn=[3]):
        super().__init__((width, height), Conway.CELL_SPEC)
        self.survive = survive
        self.spawn = spawn

    def advance(self):
        newgrid = []

        for y in range(self.height):
            newgrid.append([])

            for x in range(self.width):
                neighborcount = 0

                for xdiff in [-1, 0, 1]:
                    for ydiff in [-1, 0, 1]:
                        if xdiff != 0 or ydiff != 0:
                            if y + ydiff >= 0 and y + ydiff < self.height and x + xdiff >= 0 and x + xdiff < self.width:
                                if self.grid[y + ydiff][x + xdiff]:
                                    neighborcount += 1

                if self.grid[y][x]:
                    newgrid[-1].append(neighborcount in self.survive)
                else:
                    newgrid[-1].append(neighborcount in self.spawn)

        self.grid = newgrid

    def print_grid(self):
        for row in self.grid:
            print(''.join([('X' if c else '.') for c in row]))

    def compute_neighbors(self):
        vert_pad = np.zeros((self.height, 1))
        hor_pad = np.zeros((1, self.width))
        right = np.delete(np.concatenate((self.np_grid, vert_pad), axis=1), 0, axis=1)
        left = np.delete(np.concatenate((vert_pad, self.np_grid), axis=1), self.width, axis=1)
        bottom = np.delete(np.concatenate((self.np_grid, hor_pad), axis=0), 0, axis=0)
        top = np.delete(np.concatenate((hor_pad, self.np_grid), axis=0), self.height, axis=0)

        return top, bottom, left, right



if __name__ == "__main__":
    g = Conway(10, 10)
    print(g.grid)

    # for i in range(10):
    #     g.print_grid()
    #     print()
    #     g.advance()