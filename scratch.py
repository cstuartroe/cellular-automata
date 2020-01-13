import random
import numpy as np

class ConwayGrid:
    def __init__(self, width, height, survive=[2, 3], spawn=[3], p_init_alive=0.5):
        self.width = width
        self.height = height
        self.survive = survive
        self.spawn = spawn
        self.grid = [[(True if random.randrange(2) == 1 else False) for x in range(width)] for y in range(height)]
        self.np_grid = np.random.choice([0,1], size=(height, width), p=[p_init_alive, (1-p_init_alive)])

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

    def print_np_grid(self):
        print(str(self.np_grid))

    def compute_neighbors(self):
        vert_pad = np.zeros((self.height, 1))
        hor_pad = np.zeros((1, self.width))
        right = np.delete(np.concatenate((self.np_grid, vert_pad), axis=1), 0, axis=1)
        left = np.delete(np.concatenate((vert_pad, self.np_grid), axis=1), self.width, axis=1)
        bottom = np.delete(np.concatenate((self.np_grid, hor_pad), axis=0), self.
        top = np.concatenate((hor_pad, self.np_grid), axis=0)
        de = np.concatenate((self.np_grid, vert_pad), axis=1)

        return top, bottom, left, right



if __name__ == '__main__':

    g = ConwayGrid(3,4)

    g.print_np_grid()
    print(g.compute_neighbors()[0])
    print(g.compute_neighbors()[1])
    print(g.compute_neighbors()[2])
    print(g.compute_neighbors()[3])
