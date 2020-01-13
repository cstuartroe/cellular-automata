from games import conway as con
from metrics import component as comp
import sys


import numpy as np
from tqdm import tqdm

conway = con.Conway(100,100)
com = comp.Components(conway)

cl = []

print(sys.setrecursionlimit(100000))
print(conway.grid.squeeze())
print(len(com.get_components()))

