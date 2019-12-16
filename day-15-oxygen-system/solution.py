import sys

sys.path.append('..')

from tools.intcomp import ICC, load_program
from queue import Queue

DIRECTIONS = {
    (0, -1): 1,
    (0, 1): 2,
    (-1, 0): 3,
    (1, 0): 4,
}

GRADIENT = [46 for i in range(0, 32)]
GRADIENT += [47 for i in range(0, 32)]
GRADIENT += [48 for i in range(0, 32)]
GRADIENT += [50 for i in range(0, 32)]
GRADIENT += [50 for i in range(0, 32)]
GRADIENT += [51 for i in range(0, 32)]
GRADIENT += [92 for i in range(0, 32)]
GRADIENT += [91 for i in range(0, 32)]
GRADIENT += [90 for i in range(0, 32)]
GRADIENT += [89 for i in range(0, 32)]
GRADIENT += [88 for i in range(0, 32)]
GRADIENT += [52 for i in range(0, 32)]


bg = lambda text, color: "\33[48;5;" + str(color) + "m" + text + "\33[0m"

def print_grid(grid, pos=None, colored=None):
    a = min([x for x,_ in grid.keys()])
    b = max([x for x,_ in grid.keys()])
    c = min([y for _,y in grid.keys()])
    d = max([y for _,y in grid.keys()])

    blocks = {
        -1: '░',
        0: ' ',
        1: '█',
        2: 'S',
    }

    for y in range(c-1, d+2):
        for x in range(a-1, b+2):
            c = ''
            if pos and pos == (x,y):
                c = 'D'
            else:
                c = blocks[grid.get((x,y), -1)]
            if colored and colored.get((x,y)):
                print(bg(c, GRADIENT[colored[(x,y)]]), end='')
            else:
                print(c, end='')

        print()


def find_path(grid, start, end):
    # BFS
    q = Queue()
    q.put((start, []))
    visited = set()

    c = 0
    while not q.empty():
        pos, path = q.get()
        if pos in visited:
            continue
        if pos == end:
            path.append(end)
            return path
        visited.add(pos)
        for p in get_possitions(grid, pos, end):
            q.put((p, path + [pos]))
        c += 1
    

def get_possitions(grid, pos, incl=None):
    positions = []
    for d in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        x = pos[0] + d[0]
        y = pos[1] + d[1]
        if (x,y) == incl:
            positions.append((x,y))
        elif grid.get((x,y), -1) == 0:
            positions.append((x,y))
    return positions

def get_unexplored(grid, pos):
    unexplored = []
    for d in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        x = pos[0] + d[0]
        y = pos[1] + d[1]
        if grid.get((x,y)) is None:
            unexplored.append((x,y))
    return unexplored

def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

class RepairDroidProxy:

    def __init__(self, program):
        self.grid = {}
        self.unexplored = []
        self.pos = (0,0)
        self.comp = ICC(load_program(program), inpq=self.on_move_cmd, outq=self.on_robot_out, quiet=True)
        self.grid[(0,0)] = 0
        self.move = None
        self.path = None
        self.oxygen_system = None
        self.oxygen_system_path = None
    
    def _get_unexplored(self):
        unexplored = get_unexplored(self.grid, self.pos)
        for un in unexplored:
            if un not in self.unexplored:
                self.unexplored.append(un)
        
        self.unexplored = sorted(self.unexplored, key=lambda x: dist(self.pos, x))
    
    def on_move_cmd(self):
        if self.path:
            p = self.path[0]
            self.path = self.path[1:]
            self.move = p
            cmd = DIRECTIONS[(p[0] - self.pos[0], p[1] - self.pos[1])]
            return cmd
        self._get_unexplored()
        if not self.unexplored:
            raise Exception('FOUND')
        up = self.unexplored[0]
        self.unexplored = self.unexplored[1:]
        self.path = find_path(self.grid, self.pos, up)[1:]
        return self.on_move_cmd()
    
    def on_robot_out(self, v):
        if v == 0:
            # a wall
            self.grid[self.move] = 1
        elif v == 1:
            # empty space
            self.pos = self.move
            self.move = None
            self.grid[self.pos] = 0
        else:
            # we have found the Oxygen system
            self.pos = self.move
            self.move = None
            self.grid[self.pos] = 2
            # Calculate the path here
            self.oxygen_system_path = [r for r in reversed(find_path(self.grid, self.pos, (0,0)))]
            self.oxygen_system = self.pos
        print()
        print_grid(self.grid, self.pos)
        #from time import sleep
        #sleep(0.1)
    
    def fill_with_oxygen(self):
        oxygen = {}
        visited = set()

        q = Queue()
        q.put((self.oxygen_system, 0))
        oxygen[self.oxygen_system] = 0
        

        while not q.empty():
            pos, m = q.get()

            if pos in visited:
                continue
            
            visited.add(pos)

            for p in get_possitions(self.grid, pos):
                if oxygen.get(p) is not None:
                    continue
                oxygen[p] = m + 1
                q.put((p, m+1))
        print()
        print_grid(self.grid, self.pos, oxygen)
        return max([v for _,v in oxygen.items()])

    def run_droid(self):
        try:
            self.comp.execute()
        except Exception as e:
            if str(e) == 'FOUND':
                print('Found Oxygen System at', self.oxygen_system, ' Path: ', self.oxygen_system_path)
                print('Part 1: Path len: ', len(self.oxygen_system_path)-1)
                return
            raise e


def part1and2():
    droid = RepairDroidProxy('input')
    droid.run_droid()
    print('Part 2: ', droid.fill_with_oxygen())


part1and2()