import numpy as np
from .game import CellSpec, Game


class Conway(Game):

    CELL_SPEC = CellSpec([{0, 1}])

    def __init__(self, width, height, survive=[2, 3], spawn=[3]):
        super().__init__((width, height), Conway.CELL_SPEC)
        self.survive = survive
        self.spawn = spawn

    def advance(self):
        old_grid = self.grid[-1, :, :, 0]
        neighbor_matrix = Conway.static_neighbors(old_grid)
        new_grid = np.zeros((self.shape[0], self.shape[1]))

        np.place(new_grid, (np.isin(neighbor_matrix, self.survive) & (old_grid == 1)), 1)
        np.place(new_grid, (np.isin(neighbor_matrix, self.spawn) & (old_grid == 0)), 1)

        new_grid = np.reshape(new_grid, (1, *new_grid.shape, 1))

        self.grid = np.concatenate((self.grid, new_grid), axis=0)

    def print_grid(self):
        for row in self.grid:
            print(''.join([('X' if c else '.') for c in row]))

    @staticmethod
    def shift_down(matrix):
        hor_pad = np.zeros((1, matrix.shape[1]))
        return np.delete(np.concatenate((hor_pad, matrix), axis=0), matrix.shape[0], axis=0)

    @staticmethod
    def shift_up(matrix):
        hor_pad = np.zeros((1, matrix.shape[1]))
        return np.delete(np.concatenate((matrix, hor_pad), axis=0), 0, axis=0)

    @staticmethod
    def shift_left(matrix):
        vert_pad = np.zeros((matrix.shape[0], 1))
        return np.delete(np.concatenate((matrix, vert_pad), axis=1), 0, axis=1)

    @staticmethod
    def shift_right(matrix):
        vert_pad = np.zeros((matrix.shape[0], 1))
        return np.delete(np.concatenate((vert_pad, matrix), axis=1), matrix.shape[1], axis=1)

    @staticmethod
    def collapse_and_sum(arrays, axis):
        return np.sum(np.dstack(arrays), axis)

    @staticmethod
    def static_neighbors(matrix):
        a = Conway.shift_right(matrix)
        b = Conway.shift_down(matrix)
        c = Conway.shift_up(matrix)
        d = Conway.shift_left(matrix)
        e = Conway.shift_up(Conway.shift_left(matrix))
        f = Conway.shift_up(Conway.shift_right(matrix))
        g = Conway.shift_down(Conway.shift_left(matrix))
        h = Conway.shift_down(Conway.shift_right(matrix))

        tup = (a,b,c,d,e,f,g,h)

        return Conway.collapse_and_sum(tup, 2)

    def get_grid(self):
        return self.grid
