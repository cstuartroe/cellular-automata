import numpy as np

def percent_cells_changed(game):
    first_frame = game.grid[0]
    equals_first_frame = np.array([np.equal(frame, first_frame) for frame in game.grid])
    equals_first_frame = np.logical_and.reduce(equals_first_frame, axis=0)
    equals_first_frame = np.logical_and.reduce(equals_first_frame, axis=-1)
    # TODO: better variable names
    return 1 - np.sum(equals_first_frame)/equals_first_frame.size


def cell_change_frequency(game):
    is_changed = np.array([np.logical_not(np.equal(game.grid[t], game.grid[t+1])) for t in range(game.grid.shape[0]-1)])
    return np.sum(is_changed)/is_changed.size


