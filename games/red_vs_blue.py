import numpy as np

from .game import Dimension, Spec, Game
from .matrix_utils import add_shifts, squashed_sigmoid


def conway_generator(init_alive_prob):
    return (lambda a: np.where(a > init_alive_prob, 0, 1))


class RedVsBlue(Game):
    RULE_SPEC = Spec(
        [Dimension("continuous", lambda x: x,   start=0, end=1)]*19 +
        [Dimension("continuous", lambda x: 4*x - 2, start=-2, end=2)]*3
    )

    def __init__(self, width, height, survive=[2, 3], spawn=[3], color_noise=.1,
                 auto_multiplier=1, lateral_multiplier=1, diagonal_multiplier=1,
                 init_alive_prob=.25):
        cell_spec = Spec([
            Dimension("categorical", conway_generator(init_alive_prob), categories={0, 1}),
            Dimension("continuous", lambda a: a*2 - 1, start=-1, end=1)
        ])
        super().__init__((height, width), cell_spec)
        self.survive = survive
        self.spawn = spawn
        self.color_noise = color_noise
        self.auto_multiplier = auto_multiplier,
        self.lateral_multiplier = lateral_multiplier
        self.diagonal_multiplier = diagonal_multiplier

    def advance(self):
        alive_cells = self.grid[-1, :, :, 0].astype(int)
        cell_colors = np.multiply(self.grid[-1, :, :, 1], alive_cells)

        num_neighbors = add_shifts(alive_cells, [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)])

        is_alive = np.zeros(self.shape, dtype=int)
        rand_grid = np.random.rand(*self.shape)

        survive_thresholds = self.survive[num_neighbors]
        spawn_thresholds = self.spawn[num_neighbors]

        np.place(is_alive, ((survive_thresholds > rand_grid) & (alive_cells == 1)), 1)
        np.place(is_alive, ((spawn_thresholds > rand_grid) & (alive_cells == 0)), 1)

        new_colors = cell_colors*self.auto_multiplier
        new_colors += add_shifts(cell_colors, [(0, 1), (0, -1), (1, 0), (-1, 0)])*self.lateral_multiplier/4
        new_colors += add_shifts(cell_colors, [(1, 1), (1, -1), (-1, 1), (-1, -1)])*self.diagonal_multiplier/4
        new_colors += np.random.randn(*new_colors.shape) * self.color_noise

        np.place(new_colors, new_colors > 1, 1)
        np.place(new_colors, new_colors < -1, -1)
        new_colors = np.multiply(new_colors, is_alive)

        new_frame = np.stack((is_alive, new_colors), axis=2)
        new_frame = np.reshape(new_frame, (1, *new_frame.shape))

        self.grid = np.concatenate((self.grid, new_frame), axis=0)

    @staticmethod
    def cartesian_distance(cell1, cell2):
        return ((cell1[1] - cell2[1])**2 + (cell1[2] - cell2[2])**2)**.5

    def cell_similarity(self, cell1, cell2):
        return 1 - abs(self.grid[cell1][0] - self.grid[cell2][0])

    @staticmethod
    def rulevector2args(rulevector):
        life_rules = squashed_sigmoid(rulevector[:18])
        survive = life_rules[:9]
        spawn = life_rules[9:]
        color_noise = rulevector[18]
        auto_multiplier = rulevector[19]
        lateral_multiplier = rulevector[20]
        diagonal_multiplier = rulevector[21]

        return [], {"survive": survive, "spawn": spawn, "color_noise": color_noise, "auto_multiplier": auto_multiplier,
                    "lateral_multiplier": lateral_multiplier, "diagonal_multiplier": diagonal_multiplier}
