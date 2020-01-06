from queue import Queue

def load_input(inpf):
    grid = []
    with open(inpf) as f:
        for line in f:
            grid.append([c for c in line.strip()])
    return grid


DOORS = [chr(ord('A') + i) for i in range(0, 26)]
KEYS = [chr(ord('a') + i) for i in range(0, 26)]
print(DOORS)
print(KEYS)


def get_near(grid, x, y, keys):
    near = []
    for dx, dy in [(1, 0), (0, -1), (-1, 0), (0, 1)]:
        xx = x + dx
        yy = y + dy
        if xx >= 0 and xx<len(grid[0]) and yy >= 0 and yy < len(grid):
            c = grid[yy][xx]
            #print('  __ ', c)
            if c == '#':
                continue
            if c in '.@':
                near.append((xx, yy))
            elif c in DOORS:
                # check if we have the key
                #print('  __ a door')
                if c.lower() in keys:
                    near.append((xx, yy))
            else:
                if c in KEYS:
                    near.append((xx, yy))
    return near

def find_next_keys(grid, x, y, keys, path):
    q = Queue()
    q.put((x,y, path, keys))

    visited = set()
    new_keys = []

    while not q.empty():
        x, y, path, keys = q.get()
        if (x,y) in visited:
            continue
        visited.add((x,y))
        path = path + [(x,y)]
        for xx, yy in get_near(grid, x, y, keys):
            c = grid[yy][xx]
            #print('at',x,y,' looking at', c)
            if c in DOORS:
                #print(' .. door')
                if c.lower() in keys:
                    #print('  .. .. unlock')
                    q.put((xx, yy, path, keys))
            elif c in KEYS:
                # grab the key
                #print(' .. a key')
                if c not in keys:
                    # new key
                    #print(' .. new one')
                    new_keys.append((xx,yy, path))
                else:
                    q.put((xx, yy, path, keys))    
            else:
                #print(' .. hallway')
                q.put((xx, yy, path, keys))
    
    return new_keys


def total_keys_set(grid):
    keys = set()
    for r in grid:
        for c in r:
            if c in KEYS:
                keys.add(c)
    return keys

def start_point(grid):
    for y in range(0, len(grid)):
        for x in range(0, len(grid[y])):
            if grid[y][x] == '@':
                return (x,y)


def collect_all_keys(grid):
    goal = total_keys_set(grid)
    print(goal)
    print(len(goal))
    
    x,y = start_point(grid)
    print(x,y)
    q = Queue()
    q.put((x,y, [(x,y)], set()))

    while not q.empty():
        x,y,path, keys = q.get()

        new_keys = find_next_keys(grid, x, y, keys, path)
        for xx, yy, kpath in new_keys:
            key = grid[yy][xx]
            nkeys = keys.union({key})
            print('keys=', len(nkeys))
            if nkeys == goal:
                # lucky?
                return len(path + kpath)
            q.put((xx, yy, path + kpath, nkeys))
    
    raise Exception('Nope!')


def test(inpf):
    grid = load_input(inpf)
    x,y = start_point(grid)
    nk = find_next_keys(grid, x, y, set(), [(x,y)])
    for x,y,path in nk:
        print('Key:', grid[y][x])
        print('Path: ', path)
        print('------------')
    
    print(collect_all_keys(grid))

def part1(inpf):
    grid = load_input(inpf)
    return collect_all_keys(grid)


class V:

    def __init__(self, v, x, y):
        self.v = v
        self.x = x
        self.y = y
        self.in_edges = []
        self.out_edges = []
    
    def __str__(self):
        return '{} ({},{})'.format(self.v, self.x, self.y)
    
    def __repr__(self):
        return self.__str__()

class E:

    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.doors = set()
        self.keys = set()
        self.length = None
    
    def can_reach(self, keys):
        if not len(self.keys):
            return True
        if not keys:
            return False
        for d in self.doors:
            if d.lower() not in keys:
                return False
        return True
    
    def __str__(self):
        return '{} -> {}, {} steps, doors: {}, over keys: {}'.format(self.a.v, self.b.v, self.length, self.doors, self.keys)
    
    def __repr__(self):
        return self.__str__()


class Graph:

    def __init__(self):
        self.vertices = {}
        self.edges = {}
    
    def vertex(self, v):
        return self.vertices[v]

    def add_vertex(self, vertex):
        self.vertices[vertex.v] = vertex
    
    def add_edge(self, a, b):
        edge = E(a,b)
        if self.edges.get((a,b)):
            raise Exception('already added')
        self.edges[(a,b)] = edge
        a.out_edges.append(edge)
        b.in_edges.append(edge)
        return edge
    
    def __str__(self):
        return '{} vertices, {} edges'.format(len(self.vertices), len(self.edges))
    
    def __repr__(self):
        return self.__str__()


def find_keys(grid):
    keys = []
    for y in range(0, len(grid)):
        for x in range(0, len(grid[y])):
            c = grid[y][x]
            if c in KEYS or c == '@':
                keys.append((x,y,c))
    return keys


def get_path_tiles(x,y, grid):
    tiles = []
    for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
        xx,yy = x+dx, y+dy
        if xx >= 0 and xx < len(grid[0]) and yy >= 0 and yy < len(grid):
            tile = grid[yy][xx]
            if tile == '#':
                continue
            tiles.append((xx, yy, tile))
    return tiles


def from_key_to_key(a, b, grid):
    q = Queue()
    
    x,y = a.x, a.y

    visited = set()
    visited.add((x,y))

    q.put((x,y, set(), set(), 0))

    while not q.empty():
        x,y,doors,keys, length = q.get()
        if (x,y) in visited:
            if (x,y) != (a.x, a.y):
                continue
        
        tile = grid[y][x]
        if tile == b.v:
            return (doors, keys, length)
        visited.add((x,y))
        if tile in DOORS:
            doors = doors.union({tile})
        elif tile in KEYS:
            keys = keys.union(tile)
        for nx, ny, _ in get_path_tiles(x, y, grid):
            q.put((nx, ny, doors, keys, length + 1))


def build_graph(grid):
    keys = find_keys(grid)
    graph = Graph()

    for x,y,key in keys:
        graph.add_vertex(V(key, x, y))
    
    print('Keys:', len(keys))
    for i in range(0, len(keys)):
        for j in range(0, len(keys)):
            if i == j:
                continue
            a = graph.vertex(keys[i][2])
            b = graph.vertex(keys[j][2])
            edge = graph.add_edge(a, b)
            doors, over_keys, length = from_key_to_key(a, b, grid)
            edge.doors = doors
            edge.length = length
            edge.keys = over_keys
            print(a, b, edge)

    
    return graph

def get_reachable(key, graph, keys):
    q = Queue()
    reachable = []
    #visited = set([graph.vertex(k) for k in keys])
    visited = set([k for k in keys])

    visited.add(key)
    q.put((key, keys, 0))

    while not q.empty():
        k, keys, length = q.get()
        if k.v not in keys:
            keys = keys.union(k.v)
        if k.v not in visited:
            reachable.append((k, keys, length))
        else:
            if k != key:
                continue
        visited.add(k.v)
        
        for edge in k.out_edges:
            if edge.can_reach(keys):
                q.put((edge.b, keys.union(set()), length + edge.length))
    return reachable


def collect_all(node, graph, keys, cache):
    kk = ''.join(sorted(keys))
    #if len(keys) == len(graph.vertices):
    if set(graph.vertices.keys()).issubset(keys):
        return 0  # no more distance to go
    if (node.v, kk) in cache:
        return cache[(node.v, kk)]
    
    min_len = 2**32
    reachable = get_reachable(node, graph, keys)
    if not reachable:
        return min_len
    
    for next_node, collected_keys, distance in reachable:
        min_len = min(min_len, distance + collect_all(next_node, graph, collected_keys, cache))

    cache[(node.v, kk)] = min_len
    return min_len


def split_the_grid(grid):
    x,y = start_point(grid)
    grid[y][x] = '#'
    grid[y+1][x] = '#'
    grid[y-1][x] = '#'
    grid[y][x-1] = '#'
    grid[y][x+1] = '#'
    grid[y+1][x-1] = '@'
    grid[y+1][x+1] = '@'
    grid[y-1][x-1] = '@'
    grid[y-1][x+1] = '@'

    def _get_grid(sy, ey, sx, ex):
        g = []
        for y in range(sy, ey+1):
            r = []
            g.append(r)
            for x in range(sx, ex + 1):
                r.append(grid[y][x])
        return g
    
    return (
        _get_grid(0, y, 0, x),
        _get_grid(y, len(grid) - 1, 0, x),
        _get_grid(0, y, x, len(grid[0]) - 1),
        _get_grid(y, len(grid)-1, x, len(grid[0]) - 1),
    )

def print_grid(grid):
    for r in grid:
        print(''.join(r))
    

def tackle_grid_part(grid):
    graph = build_graph(grid)
    keys_to_collect = graph.vertices.keys()
    print(graph)
    return collect_all(graph.vertex('@'), graph, set(KEYS) - keys_to_collect, {})

def part1():
    grid = load_input('input')
    graph = build_graph(grid)
    print(graph)
    return collect_all(graph.vertex('@'), graph, set(), {})


def part2():
    grid = load_input('input')
    total = 0
    for grd in split_the_grid(grid):
        print_grid(grd)
        steps = tackle_grid_part(grd)
        print('Part:', steps)
        total += steps
        
    return total

print('Part 1:', part1())
print('Part 2:', part2())
