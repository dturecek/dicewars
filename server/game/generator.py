import hexutil
from random import randint, choice as rand_choice, shuffle


class BoardGenerator(object):
    def __init__(self):
        self.min_x = -32
        self.max_x = 30
        self.min_y = -14
        self.max_y = 13
        self.coordinates = [(x, y) for x in range(self.min_x + 2, self.max_x, 2)
                            for y in range(self.min_y + 1, self.max_y)]
        for i in range(len(self.coordinates)):
            if self.coordinates[i][1] % 2 == 1:
                self.coordinates[i] = (self.coordinates[i][0] + 1, self.coordinates[i][1])

    def random_hex(self):
        y = randint(self.min_y, self.max_y)
        while True:
            if y % 2 == 0:
                x = randint(self.min_x, self.max_x)
            else:
                x = randint(self.min_x + 1, self.max_x + 1)
            if (x + y) % 2 == 0:
                break
        return hexutil.Hex(x, y)

    def generate_board(self):
        self.a = {}
        self.areas = {}
        for i in range(self.min_y, self.max_y + 1):
            self.a[i] = {}
            if i % 2 == 0:
                for j in range(self.min_x, self.max_x + 1, 2):
                    self.a[i][j] = 0
            else:
                for j in range(self.min_x + 1, self.max_x + 2, 2):
                    self.a[i][j] = 0

        for i in range(1, 30 + randint(0, 2)):
            self.create_area(i)
        self.add_neighbours()

        return self.areas

    def create_area(self, area):
        self.possible_hexes = []
        i = 0
        size = randint(12, 18)
        while i < size:
            ret = self.add_hex_to_area(area)
            i += 1
            if not ret:
                i = 0
        self.fill_area(area)

    def fill_area(self, area):
        for h in self.areas[area]['hexes']:
            for n in h.neighbours():
                counter = 0
                if n.y not in self.a or n.x not in self.a[n.y] or self.a[n.y][n.x] != 1:
                    break
                for nn in n.neighbours():
                    if (nn.y not in self.a or nn.x not in self.a[nn.y]):
                        counter += 1
                    elif nn not in self.areas[area]['hexes']:
                        counter += 1
                    if counter > 2:
                        break
                if counter <= 2:
                    self.retag_neighbouring_hexes(n)
                    self.a[n.y][n.x] = 2
                    self.areas[area]['hexes'].append(n)
                    break

    def add_hex_to_area(self, area):
        if not self.areas:
            return self.start_first_area()
        elif area not in self.areas:
            return self.start_area(area)
        else:
            return self.grow_area(area)

    def start_first_area(self):
        self.h = self.random_hex()
        self.possible_hexes.append(self.h)
        self.a[self.h.y][self.h.x] = 2
        self.retag_neighbouring_hexes(self.h)
        self.areas[1] = {
            'hexes': [self.h],
            'neighbours': []
        }
        return True

    def start_area(self, area):
        shuffle(self.coordinates)
        for coord in self.coordinates:
            x = coord[0]
            y = coord[1]
            if self.a[y][x] == 0:
                h = hexutil.Hex(x, y)
                for n in h.neighbours():
                    if n.y in self.a and n.x in self.a[n.y] and self.a[n.y][n.x] == 1:
                        self.h = h
                        self.possible_hexes.append(h)
                        self.a[h.y][h.x] = 2
                        self.retag_neighbouring_hexes(h)
                        self.areas[area] = {
                            'hexes': [h],
                            'neighbours': []
                        }
                        return True

    def grow_area(self, area):
        while True:
            if self.h != self.areas[area]['hexes'][0] or self.h not in self.possible_hexes:
                self.h = rand_choice(self.possible_hexes)

            n = self.neighbour()
            if n:
                self.possible_hexes.append(n)
                self.a[n.y][n.x] = 2
                self.retag_neighbouring_hexes(n)
                self.areas[area]['hexes'].append(n)
                return True

            else:
                self.possible_hexes.remove(self.h)
                if not self.possible_hexes:
                    self.areas.pop(area)
                    return False

    def retag_neighbouring_hexes(self, hex):
        for n in hex.neighbours():
            if n.y in self.a and n.x in self.a[n.y]:
                if self.a[n.y][n.x] == 0:
                    self.a[n.y][n.x] = 1

    def neighbour(self):
        ns = self.h.neighbours()
        shuffle(ns)
        for n in ns:
            if n.y in self.a and n.x in self.a[n.y]:
                if self.a[n.y][n.x] != 2:
                    return n
        return False

    def add_neighbours(self):
        for a in self.areas:
            for h in self.areas[a]['hexes']:
                for n in h.neighbours():
                    if (n.y in self.a and n.x in self.a[n.y] and self.a[n.y][n.x] == 2
                        and n not in self.areas[a]['hexes']):
                        for k in self.areas:
                            if a == k:
                                continue
                            if n in self.areas[k]['hexes']:
                                if k not in self.areas[a]['neighbours']:
                                    self.areas[a]['neighbours'].append(k)
