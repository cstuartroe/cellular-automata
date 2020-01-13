import numpy as np
from scipy.ndimage.measurements import label

class Components():
    def __init__(self, game):
        self.game = game
        self.frame_num = self.game.grid.shape[0]
        self.grid = self.game.grid
        self.world_shape = self.get_world_shape()
        self.visited = np.zeros(self.grid.shape, dtype=bool)
        self.num_dim = len(self.world_shape)

    def get_world_shape(self):
        shape = self.game.grid.shape
        dimension = []
        which = 1

        for dim in shape:
            if (which != 1) and (which != len(shape)):
                dimension.append(dim)
            which += 1

        return tuple(dimension)

    def get_components(self):
        components = []

        for f in range(self.frame_num):

            ones = np.where(self.grid[f] == 1)
            w = len(ones[0])
            indices = []
            s = np.stack(ones)

            for i in range(w):
                inter = tuple(s[:, i])
                indices.append(inter[:len(inter)-1])

            for i in indices:
                comp_list = []
                comp = self.recur_components(i, comp_list, f)
                if comp:
                    components.append(comp)

        return components


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
            if cell[i] < 0 or cell[i] >= self.world_shape[i]:
                return False

        return True
