import numpy as np

from games import Game
from games.matrix_utils import direction_combinations


class UnionFind:
    def __init__(self, iterable):
        self.set_keys = {}
        self.sets_by_key = {}

        for element in iterable:
            self.set_keys[element] = element
            self.sets_by_key[element] = {element}

    def find_set_key(self, element):
        if self.set_keys[element] == element:
            return element
        else:
            set_key = self.find_set_key(self.set_keys[element])
            self.set_keys[element] = set_key
            return set_key

    def find(self, element):
        return self.sets_by_key[self.find_set_key(element)]

    def union(self, element1, element2):
        set_key1 = self.find_set_key(element1)
        set_key2 = self.find_set_key(element2)

        if set_key1 == set_key2:
            return

        self.sets_by_key[set_key1] = self.sets_by_key[set_key1] | self.sets_by_key[set_key2]
        del self.sets_by_key[set_key2]

        self.set_keys[set_key2] = set_key1

    def get_sets(self):
        return list(self.sets_by_key.values())


class Components:
    def __init__(self, game: Game):
        self.game = game
        self.num_dim = len(self.game.shape)

    def get_components(self, frames=None):
        frames_components = []

        if frames is None:
            frames = range(self.game.grid.shape[0])

        for frame_num in frames:
            frames_components.append(self.frame_components(frame_num))

        return frames_components

    def frame_components(self, frame_num):
        frame_grid = self.game.grid[frame_num, :, :, 0]

        alive_cells = np.stack(np.where(frame_grid == 1), axis=1)
        alive_cells = [tuple(c) for c in alive_cells]
        components = UnionFind(alive_cells)

        neighbor_directions = direction_combinations((-1, 0, 1), (-1, 0, 1))
        neighbor_directions.remove((0, 0))

        for alive_cell in alive_cells:
            for neighbor_direction in neighbor_directions:
                neighbor_address = tuple(np.add(alive_cell, neighbor_direction))
                if self.is_valid_coord(neighbor_address):
                    neighbor = frame_grid[neighbor_address]
                    if neighbor == 1:
                        components.union(alive_cell, neighbor_address)

        return components.get_sets()

    def recur_components(self, start_coord, comp_list, frame):
        frame_tup = (frame, )
        tail = (0,)
        neighbors = self.get_neighbor_coords(start_coord)
        for c in neighbors:
            full_c = frame_tup+c+tail
            if self.grid[full_c] == 1 and not self.visited[full_c]:
                self.visited[full_c] = True
                comp_list.append(full_c)
                self.recur_components(c, comp_list, frame)

        return comp_list

    def get_neighbor_coords(self, cell):
        neighs = [cell]
        for i in range(self.num_dim):
            new_neighs = neighs.copy()
            for neighbor in neighs:
                new_neighs.append((*neighbor[:i], neighbor[i] - 1, *neighbor[i + 1:]))
                new_neighs.append((*neighbor[:i], neighbor[i] + 1, *neighbor[i + 1:]))
            neighs = new_neighs

        neighs.remove(cell)
        final_list = [neigh for neigh in neighs if self.is_valid_coord(neigh)]

        return final_list

    def get_neighbor_vals(self, frame, cell):
        frame = (frame, )
        with_frame = []
        neigh_coords = self.get_neighbor_coords(cell)
        for c in neigh_coords:
            with_frame.append((frame+c))

        return [int(self.grid[cell]) for cell in with_frame]

    def is_valid_coord(self, cell):
        for i in range(self.num_dim):
            if cell[i] < 0 or cell[i] >= self.game.shape[i]:
                return False

        return True
