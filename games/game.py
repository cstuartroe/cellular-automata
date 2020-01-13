import numpy


class CellSpec:
    def __init__(self, params):
        self.params = params


class Game:
    def __init__(self, shape, cellspec):
        self.shape = shape

        first_frame_layers = []
        for param in cellspec.params:
            if type(param) is set:
                first_frame_layers.append(numpy.random.choice(list(param), shape))
            elif type(param) is tuple:
                if type(param[0]) is float:
                    first_frame_layers.append(numpy.random.uniform(low=param[0], high=param[1], size=shape))
                elif type(param[0]) is int:
                    first_frame_layers.append(numpy.random.randint(low=param[0], high=param[1], size=shape))

        self.grid = numpy.stack(first_frame_layers, axis=-1)
        self.grid.resize((1, *self.grid.shape))

    def advance(self):
        raise NotImplementedError("advancing not yet implemented!")

    def advances(self, n):
        for i in range(n):
            self.advance()

    @staticmethod
    def cartesian_distance(cell1, cell2):
        raise NotImplementedError("cartesian distance not yet implemented!")

    def cell_similarity(self, cell1, cell2):
        raise NotImplementedError("advancing not yet implemented!")