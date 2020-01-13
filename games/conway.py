import numpy as np

from .game import Dimension, Spec, Game


def conway_generator(init_alive_prob):
    return (lambda a: np.where(a > init_alive_prob, 0, 1))


class Conway(Game):
    RULE_SPEC = Spec([Dimension("categorical", conway_generator(.5), categories={0, 1})]*18)

    def __init__(self, width, height, survive=[2, 3], spawn=[3], init_alive_prob=.25):
        cell_spec = Spec([Dimension("categorical", conway_generator(init_alive_prob), categories={0, 1})])
        super().__init__((width, height), cell_spec)
        self.survive = survive
        self.spawn = spawn

    def advance(self):
        old_grid = self.grid[-1, :, :, 0]
        neighbor_matrix = Conway.neighbors(old_grid)
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
    def neighbors(matrix):
        a = Conway.shift_right(matrix)
        b = Conway.shift_down(matrix)
        c = Conway.shift_up(matrix)
        d = Conway.shift_left(matrix)
        e = Conway.shift_up(Conway.shift_left(matrix))
        f = Conway.shift_up(Conway.shift_right(matrix))
        g = Conway.shift_down(Conway.shift_left(matrix))
        h = Conway.shift_down(Conway.shift_right(matrix))

        tup = (a, b, c, d, e, f, g, h)

        return Conway.collapse_and_sum(tup, 2)

    @staticmethod
    def cartesian_distance(cell1, cell2):
        return ((cell1[1] - cell2[1])**2 + (cell1[2] - cell2[2])**2)**.5

    def cell_similarity(self, cell1, cell2):
        return 1 if (self.grid[cell1][0] == self.grid[cell2][0]) else 0

    @staticmethod
    def rulevector2args(rulevector):
        survive = list(rulevector[:9])
        spawn = list(rulevector[9:])
        return [], {"survive": survive, "spawn": spawn}