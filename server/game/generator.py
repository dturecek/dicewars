import hexutil
from random import randint, choice as rand_choice, shuffle


class BoardGenerator(object):
    """Generator of game board
    """
    def __init__(self):
        """
        Attributes
        ----------
        min_x, max_x, min_y, max_y : int
            Boundary values for Hex coordinates
        """
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
        """Get random Hex from the board

        Returns
        -------
        hexutil.Hex
            Random hex from within the game board
        """
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
        """Method generating the board

        Returns
        -------
        dict
            Dictionary of areas in the game board. Contains names of adjacent 
            areas and coordinates of the hexes of each area
        """
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
            self.__create_area(i)
        self.__add_neighbours()

        return self.areas

    def __create_area(self, area):
        """Create an area from Hexes
        """
        self.possible_hexes = []
        i = 0
        size = randint(12, 18)
        while i < size:
            ret = self.__add_hex_to_area(area)
            i += 1
            if not ret:
                i = 0
        self.__fill_area(area)

    def __fill_area(self, area):
        """Fills empty Hexes inside the area
        """
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
                    self.__retag_neighbouring_hexes(n)
                    self.a[n.y][n.x] = 2
                    self.areas[area]['hexes'].append(n)
                    break

    def __add_hex_to_area(self, area):
        """Add a single Hex to area being created
        """
        if not self.areas:
            return self.__start_first_area()
        elif area not in self.areas:
            return self.__start_area(area)
        else:
            return self.__grow_area(area)

    def __start_first_area(self):
        """Add first Hex to first area on the board
        """
        self.h = self.random_hex()
        self.possible_hexes.append(self.h)
        self.a[self.h.y][self.h.x] = 2
        self.__retag_neighbouring_hexes(self.h)
        self.areas[1] = {
            'hexes': [self.h],
            'neighbours': []
        }
        return True

    def __start_area(self, area):
        """Add first Hex to an area
        """
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
                        self.__retag_neighbouring_hexes(h)
                        self.areas[area] = {
                            'hexes': [h],
                            'neighbours': []
                        }
                        return True

    def __grow_area(self, area):
        """Add hex to already existing area
        """
        while True:
            if self.h != self.areas[area]['hexes'][0] or self.h not in self.possible_hexes:
                self.h = rand_choice(self.possible_hexes)

            n = self.__neighbour()
            if n:
                self.possible_hexes.append(n)
                self.a[n.y][n.x] = 2
                self.__retag_neighbouring_hexes(n)
                self.areas[area]['hexes'].append(n)
                return True

            else:
                self.possible_hexes.remove(self.h)
                if not self.possible_hexes:
                    self.areas.pop(area)
                    return False

    def __retag_neighbouring_hexes(self, hex):
        """Mark adjacent Hexes as neighbours to already used Hex
        """
        for n in hex.neighbours():
            if n.y in self.a and n.x in self.a[n.y]:
                if self.a[n.y][n.x] == 0:
                    self.a[n.y][n.x] = 1

    def __neighbour(self):
        """Get random adjacent Hex
        """
        ns = self.h.neighbours()
        shuffle(ns)
        for n in ns:
            if n.y in self.a and n.x in self.a[n.y]:
                if self.a[n.y][n.x] != 2:
                    return n
        return False

    def __add_neighbours(self):
        """Add neighbours of an area to the areas dict based
        """
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
