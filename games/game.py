import numpy as np
import random
from typing import Callable


class Dimension:
    TYPES = {"categorical", "integer", "continuous"}

    def __init__(self, dtype: str,
                 generator: Callable[[float], float],
                 categories: set = None,
                 start: float = None,
                 end: float = None):
        """A dimension represents a single piece of state for a cell or a ruleset, which has a type,
           a domain, and a probability distribution which is specified by its generator function
        generator: maps a number or np vector uniformly distributed over [0, 1) to the desired probability distribution
                   generators are responsible for initialization of cells, are less important for rulesets
        start, end: define an integer or continuous range. end is exclusive.
        """
        if categories is None:
            categories = set()
        assert(dtype in Dimension.TYPES)
        self.dtype = dtype
        self.generator = generator

        # used to check that at least a few randomly generated values fall within the specified domain
        # obviously not a good way to check for edge cases
        samples = generator(np.random.rand(10))

        if dtype == "categorical":
            assert(type(categories) is set)
            self.categories = categories
            assert(all(s in categories for s in samples))

        elif dtype == "integer":
            assert(type(start) is int and type(end) is int)
            self.start = start
            self.end = end
            assert(all(s in list(range(self.start, self.end)) for s in samples))

        elif dtype == "continuous":
            assert(type(start) in [float, int] and type(end) in [float, int])
            self.start = start
            self.end = end
            assert(all((start <= s < end) for s in samples))

    def generate(self):
        return self.generator(random.random())


class Spec:
    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.num_dimensions = len(dimensions)

    def generate(self):
        return np.array([dimension.generate() for dimension in self.dimensions])


class Game:
    def __init__(self, shape, cell_spec):
        self.shape = shape

        first_frame_layers = []
        for dimension in cell_spec.dimensions:
            first_frame_layers.append(dimension.generator(np.random.rand(*shape)))

        self.grid = np.stack(first_frame_layers, axis=-1)
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

    @staticmethod
    def rulevector2args(rulevector):
        """Maps a numpy vector within a ruleset space to an actual args and kwargs to pass to game_class.__init__"""
        raise NotImplementedError("rulevector2args not yet implemented!")
