import numpy as np

from .game import Dimension, Spec, Game
from .matrix_utils import add_shifts, direction_combinations, squashed_sigmoid
from .conway import conway_generator


class Rhomdos(Game):
    RULE_SPEC = Spec([Dimension("continuous", lambda x: x, start=0.0, end=1.0)]*26)

    def __init__(self, width, height, depth, survive, spawn, init_alive_prob):
        cell_spec = Spec([Dimension("categorical", conway_generator(init_alive_prob), categories={0, 1})])
        super().__init__((depth, height, width), cell_spec)

        self.survive = survive
        self.spawn = spawn

    def advance(self):
        old_grid = self.grid[-1, :, :, :, 0]
        neighbor_matrix = Rhomdos.neighbors(old_grid)

        new_grid = np.zeros(self.shape, dtype=int)
        rand_grid = np.random.rand(*self.shape)

        survive_thresholds = self.survive[neighbor_matrix]
        spawn_thresholds = self.spawn[neighbor_matrix]

        np.place(new_grid, ((survive_thresholds > rand_grid) & (old_grid == 1)), 1)
        np.place(new_grid, ((spawn_thresholds > rand_grid) & (old_grid == 0)), 1)

        new_grid = np.reshape(new_grid, (1, *new_grid.shape, 1))

        self.grid = np.concatenate((self.grid, new_grid), axis=0)

    @staticmethod
    def neighbors(matrix):
        lateral_neighbor_directions = [(0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0)]
        odd_vertical_neighbor_directions = direction_combinations((1, -1), (0, -1), (0, -1))
        even_vertical_neighbor_directions = direction_combinations((1, -1), (0, 1), (0, 1))

        odd_neighbors = add_shifts(matrix, lateral_neighbor_directions + odd_vertical_neighbor_directions)
        even_neighbors = add_shifts(matrix, lateral_neighbor_directions + even_vertical_neighbor_directions)

        return np.where(np.mgrid[0:matrix.shape[0], 0:matrix.shape[1], 0:matrix.shape[2]][0] % 2 == 0,
                        even_neighbors, odd_neighbors)

    @staticmethod
    def rulevector2args(rulevector):
        life_rules = squashed_sigmoid(rulevector)
        return [], {"survive": life_rules[:13], "spawn": life_rules[13:]}
