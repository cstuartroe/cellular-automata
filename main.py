import numpy

from games.conway import Conway
from metrics import percent_cells_changed, cell_change_frequency

g = Conway(10, 10)

g.grid = numpy.repeat(g.grid, 5, axis=0)

print(cell_change_frequency(g))