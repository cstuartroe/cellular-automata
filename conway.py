import random


class ConwayGrid:
    def __init__(self, width, height, survive=[2, 3], spawn=[3]):
        self.width = width
        self.height = height
        self.survive = survive
        self.spawn = spawn
        self.grid = [[(True if random.randrange(2) == 1 else False) for x in range(width)] for y in range(height)]

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


if __name__ == "__main__":
    g = ConwayGrid(10, 10)

    for i in range(10):
        g.print_grid()
        print()
        g.advance()