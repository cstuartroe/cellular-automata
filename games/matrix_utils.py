import numpy as np


def shift(matrix, direction):
    for dim, distance in enumerate(direction):
        hor_pad = np.zeros(matrix.shape[:dim] + (abs(distance),) + matrix.shape[dim+1:], dtype=matrix.dtype)
        if distance > 0:
            matrix = np.delete(np.concatenate((hor_pad, matrix), axis=dim), np.s_[-distance:], axis=dim)
        elif distance < 0:
            matrix = np.delete(np.concatenate((matrix, hor_pad), axis=dim), np.s_[:-distance], axis=dim)

    return matrix


def add_shifts(matrix, shifts):
    # print("adding shifts")
    # print(matrix)
    arrays = [shift(matrix, direction) for direction in shifts]
    # for i in range(len(shifts)):
    #     print(list(shifts)[i])
    #     print(arrays[i])
    # print(np.sum(np.array(arrays), 0, dtype=matrix.dtype))
    # print()
    return np.sum(np.array(arrays), 0, dtype=matrix.dtype)


def direction_combinations(*tuples):
    combos = [()]
    for tup in tuples:
        new_combos = []
        for combo in combos:
            for direction in tup:
                new_combos.append(combo + (direction,))
        combos = new_combos
    return combos
