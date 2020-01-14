from math import log2
import random

from direct.task import Task

HALFLIFE = 100


class Rhomdo:
    def __init__(self, x, y, z, array, num_rows, start_density, survival_rules, birth_rules):
        self.x, self.y, self.z = x, y, z
        self.odd = self.z % 2 == 1
        self.id = x * (num_rows ** 2) + y * num_rows + z
        self.array = array
        self.lifespan = -HALFLIFE * log2(1 - random.random())
        self.scheduled_alive = True

        self.num_rows = num_rows
        self.start_density = start_density
        self.survival_rules = survival_rules
        self.birth_rules = birth_rules

        self.rr = None

    def add_rr(self, rr):
        self.rr = rr
        if random.random() < self.start_density:
            self.be_born()
        else:
            self.die()

    def determine_life(self):
        if self.alive:
            self.scheduled_alive = self.survival_rules[self.adjacent_alive()]
        else:
            self.scheduled_alive = self.birth_rules[self.adjacent_alive()]

    def enact_life(self):
        if self.scheduled_alive and not self.alive:
            self.be_born()
        elif not self.scheduled_alive and self.alive:
            self.die()

    def die(self):
        if self.rr:
            self.rr.hide()
        self.alive = False

    def be_born(self):
        if self.rr:
            self.rr.show()
        self.alive = True

    def adjacent_alive(self):
        if self.odd:
            adjacents = [(1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, -1, 0), (0, 0, 1), (1, 0, 1), (0, 1, 1), (1, 1, 1),
                         (0, 0, -1), (1, 0, -1), (0, 1, -1), (1, 1, -1)]
        else:
            adjacents = [(1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, -1, 0), (0, 0, 1), (-1, 0, 1), (0, -1, 1), (-1, -1, 1),
                         (0, 0, -1), (-1, 0, -1), (0, -1, -1), (-1, -1, -1)]

        result = 0
        for adjacent in adjacents:
            adjX, adjY, adjZ = (self.x + adjacent[0]), (self.y + adjacent[1]), (self.z + adjacent[2])
            if not (-1 in (adjX, adjY, adjZ)) and not (self.num_rows in (adjX, adjY, adjZ)):
                result += (1 if self.array[adjX][adjY][adjZ].alive else 0)
        return result


class RhomdoGame:
    def __init__(self, _survival_rules, _birth_rules, _start_density, num_rows):
        self.SURVIVAL_RULES = _survival_rules
        self.BIRTH_RULES = _birth_rules
        self.START_DENSITY = _start_density
        self.num_rows = num_rows

        self.rhomdos = []

        for x in range(self.num_rows):
            rhomdosY = []
            for y in range(self.num_rows):
                rhomdosZ = []
                for z in range(self.num_rows):
                    rhomdo = Rhomdo(x, y, z, self.rhomdos, self.num_rows, self.START_DENSITY, self.SURVIVAL_RULES, self.BIRTH_RULES)
                    rhomdosZ.append(rhomdo)
                rhomdosY.append(rhomdosZ)
            self.rhomdos.append(rhomdosY)

    def updateRhomdos(self):
        for x in range(self.num_rows):
            for y in range(self.num_rows):
                for z in range(self.num_rows):
                    self.rhomdos[x][y][z].determine_life()
        for x in range(self.num_rows):
            for y in range(self.num_rows):
                for z in range(self.num_rows):
                    self.rhomdos[x][y][z].enact_life()
        return Task.cont
