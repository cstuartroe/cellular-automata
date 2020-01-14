import numpy as np

from .game import Dimension, Spec, Game, shift


def conway_generator(init_alive_prob):
    return (lambda a: np.where(a > init_alive_prob, 0, 1))


class Conway(Game):
    RULE_SPEC = Spec([Dimension("categorical", conway_generator(.5), categories={0, 1})]*18)

    def __init__(self, width, height, survive=[2, 3], spawn=[3], init_alive_prob=.25):
        cell_spec = Spec([Dimension("categorical", conway_generator(init_alive_prob), categories={0, 1})])
        super().__init__((height, width), cell_spec)
        self.survive = survive
        self.spawn = spawn

    def advance(self):
        old_grid = self.grid[-1, :, :, 0]
        neighbor_matrix = Conway.neighbors(old_grid)
        new_grid = np.zeros(self.shape, dtype=int)

        np.place(new_grid, (np.isin(neighbor_matrix, self.survive) & (old_grid == 1)), 1)
        np.place(new_grid, (np.isin(neighbor_matrix, self.spawn) & (old_grid == 0)), 1)

        new_grid = np.reshape(new_grid, (1, *new_grid.shape, 1))

        self.grid = np.concatenate((self.grid, new_grid), axis=0)

    def print_grid(self):
        grid = np.reshape(self.grid[-1], self.shape)
        for row in grid:
            for cell in row:
                print("X" if cell else ".", end="")
            print()

    @staticmethod
    def collapse_and_sum(arrays, axis):
        return np.sum(np.dstack(arrays), axis, dtype=int)

    @staticmethod
    def neighbors(matrix):
        up = shift(matrix, (1, 0))
        down = shift(matrix, (-1, 0))
        left = shift(matrix, (0, -1))
        right = shift(matrix, (0, 1))
        up_left = shift(matrix, (1, -1))
        up_right = shift(matrix, (1, 1))
        down_left = shift(matrix, (-1, -1))
        down_right = shift(matrix, (-1, 1))

        tup = (up, down, left, right, up_left, up_right, down_left, down_right)

        return Conway.collapse_and_sum(tup, 2)

    @staticmethod
    def cartesian_distance(cell1, cell2):
        return ((cell1[1] - cell2[1])**2 + (cell1[2] - cell2[2])**2)**.5

    def cell_similarity(self, cell1, cell2):
        return 1 - abs(self.grid[cell1][0] - self.grid[cell2][0])

    @staticmethod
    def rulevector2args(rulevector):
        survive = [i for i in range(9) if rulevector[i] == 1]
        spawn = [i for i in range(9, 18) if rulevector[i] == 1]
        return [], {"survive": survive, "spawn": spawn}


class ProbabilisticConway(Conway):
    RULE_SPEC = Spec([Dimension("continuous", lambda x: x, start=0.0, end=1.0)] * 18)

    def __init__(self, *args, survive=np.array([.5]*9), spawn=np.array([.5]*9), **kwargs):
        super().__init__(*args, survive=survive, spawn=spawn, **kwargs)

    def advance(self):
        old_grid = self.grid[-1, :, :, 0]
        neighbor_matrix = Conway.neighbors(old_grid)

        new_grid = np.zeros(self.shape, dtype=int)
        rand_grid = np.random.rand(*self.shape)

        survive_thresholds = self.survive[neighbor_matrix]
        spawn_thresholds = self.spawn[neighbor_matrix]

        np.place(new_grid, ((survive_thresholds > rand_grid) & (old_grid == 1)), 1)
        np.place(new_grid, ((spawn_thresholds > rand_grid) & (old_grid == 0)), 1)

        new_grid = np.reshape(new_grid, (1, *new_grid.shape, 1))

        self.grid = np.concatenate((self.grid, new_grid), axis=0)

    @staticmethod
    def rulevector2args(rulevector):
        survive = rulevector[:9]
        spawn = rulevector[9:]
        return [], {"survive": survive, "spawn": spawn}
