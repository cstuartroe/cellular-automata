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


def sparse_change(game):
    return percent_cells_changed(game)*(1 - cell_change_frequency(game))


def random_position(game):
    return tuple([np.random.randint(width) for width in game.shape])


def local_similarity(game):
    local_similarities = []
    global_similarities = []

    num_frames = game.grid.shape[0]

    for frame in range(num_frames):
        random_position1 = (frame,) + random_position(game)
        random_position2 = (frame,) + random_position(game)

        global_similarities.append(game.cell_similarity(random_position1, random_position2))

    for frame in range(num_frames):
        random_position1 = (frame,) + random_position(game)
        random_position2 = None

        while random_position2 is None:
            rand_dim = np.random.randint(len(game.shape))
            if random_position1[rand_dim+1] + 1 < game.shape[rand_dim]:
                random_position2 = random_position1[:rand_dim+1] +\
                                   (random_position1[rand_dim+1] + 1,) +\
                                   random_position1[rand_dim+2:]

        local_similarities.append(game.cell_similarity(random_position1, random_position2))

    return sum(local_similarities)/(sum(global_similarities) + 1)
