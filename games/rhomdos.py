import numpy as np

from .game import Dimension, Spec, Game
from .matrix_utils import add_shifts, direction_combinations
from .conway import conway_generator


    # def determine_life(self):
    #     if self.alive:
    #         self.scheduled_alive = self.survival_rules[self.adjacent_alive()]
    #     else:
    #         self.scheduled_alive = self.birth_rules[self.adjacent_alive()]
    #
    # def enact_life(self):
    #     if self.scheduled_alive and not self.alive:
    #         self.be_born()
    #     elif not self.scheduled_alive and self.alive:
    #         self.die()
    #
    # def adjacent_alive(self):
    #     if self.odd:
    #         adjacents = [(1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, -1, 0),
    #                      (0, 0, 1), (1, 0, 1), (0, 1, 1), (1, 1, 1),
    #                      (0, 0, -1), (1, 0, -1), (0, 1, -1), (1, 1, -1)]
    #     else:
    #         adjacents = [(1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, -1, 0),
    #                      (0, 0, 1), (-1, 0, 1), (0, -1, 1), (-1, -1, 1),
    #                      (0, 0, -1), (-1, 0, -1), (0, -1, -1), (-1, -1, -1)]
    #
    #     result = 0
    #     for adjacent in adjacents:
    #         adjX, adjY, adjZ = (self.x + adjacent[0]), (self.y + adjacent[1]), (self.z + adjacent[2])
    #         if not (-1 in (adjX, adjY, adjZ)) and not (self.num_rows in (adjX, adjY, adjZ)):
    #             result += (1 if self.array[adjX][adjY][adjZ].alive else 0)
    #     return result


class Rhomdos(Game):
    def __init__(self, width, height, depth, survive, spawn, init_alive_prob):
        cell_spec = Spec([Dimension("categorical", conway_generator(init_alive_prob), categories={0, 1})])
        super().__init__((depth, height, width), cell_spec)

        self.survive = survive
        self.spawn = spawn

    def advance(self):
        old_grid = self.grid[-1, :, :, :, 0]
        neighbor_matrix = Rhomdos.neighbors(old_grid)
        new_grid = np.zeros(self.shape, dtype=int)

        np.place(new_grid, (np.isin(neighbor_matrix, self.survive) & (old_grid == 1)), 1)
        np.place(new_grid, (np.isin(neighbor_matrix, self.spawn) & (old_grid == 0)), 1)

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
