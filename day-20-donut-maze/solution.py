from queue import Queue

def load_input(inpf):
    grid = []
    with open(inpf) as f:

        for line in f.read().splitlines():
            if not line.strip():
                continue
            grid.append([c for c in line])
    
    doors = []

    # horizontal doors
    y = 0
    for row in grid:
        for i in range(0, len(row) - 1):
            door = row[i] + row[i+1]
            #print(door)
            if door.isalpha():
                if i == 0:
                    doors.append((i+2, y, door, 'outer'))
                elif i == len(row) - 2:
                    doors.append((i-1, y, door, 'outer'))
                elif i+2 < len(row) and row[i+2] == '.':
                    doors.append((i+2, y, door, 'inner'))
                else:
                    doors.append((i-1, y, door, 'inner'))

                # if i == 0 or (i+2 < len(row) and row[i+2] == '.'):
                #     doors.append((i + 2, y, door))
                # elif i == len(row) - 2 or (i > 0 and row[i-1] == '.'):
                #     doors.append((i-1, y, door))
        y += 1

    for x in range(0, len(grid[0])):
        for y in range(0, len(grid)-1):
            door = grid[y][x] + grid[y+1][x]
            if door.isalpha():
                if y == 0:
                    doors.append((x, y+2, door, 'outer'))
                elif y == len(grid) - 2:
                    doors.append((x, y-1, door, 'outer'))
                elif y+2 < len(grid) and grid[y+2][x] == '.':
                    doors.append((x, y+2, door, 'inner'))
                else:
                    doors.append((x, y-1, door, 'inner'))

                # if y == 0 or (y+2 < len(grid) and grid[y+2][x] == '.'):
                #     doors.append((x, y + 2, door))
                # elif y == len(grid) - 2 or (y > 0 and grid[y-1][x] == '.'):
                #     doors.append((x, y - 1, door))
    door_map = {}
    door_types = {}
    for x, y, door, tp in doors:
        mapping = door_map.get(door)
        if not mapping:
            mapping = []
            door_map[door] = mapping
        mapping.append((x,y))
        door_types[(x,y)] = tp
    
    portals = {}
    for _, entrances in door_map.items():
        if len(entrances) == 2:
            portals[entrances[0]] = entrances[1]
            portals[entrances[1]] = entrances[0]

    return (grid, portals, door_map, door_types)


def available_tiles(x, y, grid):
    #print(x,y)
    available = []
    for xx, yy in [
            (x+1, y),
            (x, y-1),
            (x-1, y),
            (x, y+1)]:
        tile = grid[yy][xx]
        #print(xx, yy, tile)
        if tile == '.':
            #print(' .. append')
            available.append((xx, yy))
    return available


def reach_doors(x,y, grid, doors):
    terminal = set()
    for _, entrances in doors.items():
        terminal = terminal.union(set(entrances))
    
    reached = []
    q = Queue()
    visited = set()
    start = (x,y)

    q.put((x, y, 0))

    visited.add((x,y))

    while not q.empty():
        x, y, path_len = q.get()
        if (x,y) in visited:
            if (x,y) != start:
                #print('out?')
                continue
        
        visited.add((x,y))

        if (x,y) in terminal and (x,y) != start:
            reached.append((x,y, path_len))

        for xx, yy in available_tiles(x, y, grid):
            #print(xx, yy)
            q.put((xx, yy, path_len + 1))

    return reached

class V:

    def __init__(self, n, _type=None):
        self.n = n
        self.type = _type
        self.in_edges = []
        self.out_edges = []
    
    def __repr__(self):
        return 'V({}, {})'.format(self.n, self.type)
    
    def __eq__(self, o):
        if isinstance(o, V):
            return o.n == self.n
        return False
    
    def __hash__(self):
        return self.n.__hash__()
    

class E:

    def __init__(self, a, b, length=0):
        self.a = a
        self.b = b
        self.length = length
    
    def __repr__(self):
        return '{} <-> {}, {} steps'.format(self.a, self.b, self.length)
    
    def __eq__(self, o):
        if isinstance(o, E):
            return o.a == self.a and o.b == self.b
        return False
    
    def __hash__(self):
        return '{}<>{}'.format(self.a, self.b).__hash__()



class G:

    def __init__(self):
        self.vertices = {}
        self.edges = {}
    
    def add_vertex(self, n):
        v = V(n)
        self.vertices[n] = v
        return v
    
    def vertex(self, n):
        return self.vertices[n]
    
    def add_edge(self, a, b):
        edge = E(a, b)
        if self.edges.get((a,b)):
            ex = self.edges[(a,b)]
            a.out_edges.remove(ex)
            b.in_edges.remove(ex)
        self.edges[(a,b)] = edge
        a.out_edges.append(edge)
        b.in_edges.append(edge)
        return edge

    def __repr__(self):
        return '{} vertices, {} edges'.format(len(self.vertices), len(self.edges))


def build_graph(inpf):
    grid, portals, dmap, dtypes = load_input(inpf)
    graph = G()

    doors = {}
    for door, entrances in dmap.items():
        if len(entrances) == 1:
            doors[door] = entrances[0]
        else:
            for i in range(0, 2):
                doors[door + str(i)] = entrances[i]
    
    rdoors = {}
    for name, pos in doors.items():
        v = graph.add_vertex(name)
        rdoors[pos] = name
        v.type = dtypes[pos]
    
    for name, door in doors.items():
        x, y  = door
        for xx, yy, path_len in reach_doors(x, y, grid, dmap):
            other = portals.get((x,y))
            if other == (xx, yy):
                continue
            edge = graph.add_edge(graph.vertex(name), graph.vertex(rdoors[(xx, yy)]))
            edge.length = path_len
    
    # add portals as edges with 0 length
    for a,b in portals.items():
        va = graph.vertex(rdoors[a])
        vb = graph.vertex(rdoors[b])
        edge = graph.add_edge(va, vb)
        edge.length = 1
    
    return graph


def dijkstra(graph):
    start = graph.vertex('AA')
    end = graph.vertex('ZZ')

    distance = {start.n: 0}
    visited = set()

    q = [start]

    while q:
        q = sorted(q, key=lambda v: distance.get(v.n, 2**30))
        curr = q[0]
        print(curr, curr.out_edges)
        q = q[1:]
        if curr in visited and curr != start:
            continue
        if curr == end:
            return distance[curr.n]
        dist = distance[curr.n]
        visited.add(curr)
        for edge in curr.out_edges:
            nn = edge.b
            alt = edge.length + dist
            if alt < distance.get(nn.n, 2**30):
                distance[nn.n] = alt
            q.append(nn)
    



grid, portals, dmap, dtypes = load_input('input')

# l = 'a'
# for _,p in dmap.items():
#     x,y= p[0]
#     grid[y][x] = l
#     if len(p) > 1:
#         x,y = p[1]
#         grid[y][x] = l

#     l = chr(ord(l) + 1)


for row in grid:
    print(''.join(row))

print('{} doors, {} portals'.format(len(dmap), len(portals)))

ax, ay = dmap['AA'][0]
print(reach_doors(ax, ay, grid, dmap))

graph = build_graph('input')
print(graph)
print('Part 1:', dijkstra(graph))