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
        if isinstance(n, V):
            self.vertices[n.n] = n
            return n
        v = V(n)
        self.vertices[n] = v
        return v
    
    def vertex(self, n):
        return self.vertices[n]
    
    def remove_vertex(self, v):
        if v.n not in self.vertices:
            return
        del self.vertices[v.n]
        
        self.edges = {vxs:edge for vxs, edge in filter(lambda vs: v not in vs, self.edges.items())}

    def add_edge(self, a, b, length=None):
        edge = E(a, b, length)
        if self.edges.get((a,b)):
            ex = self.edges[(a,b)]
            a.out_edges.remove(ex)
            b.in_edges.remove(ex)
        self.edges[(a,b)] = edge
        a.out_edges.append(edge)
        b.in_edges.append(edge)
        return edge

    def clone(self):
        cl = G()

        for n, v in self.vertices.items():
            cv = V(n, v.type)
            cl.add_vertex(cv)
        
        for vxs, edge in self.edges.items():
            va, vb = vxs
            ce = cl.add_edge(cl.vertex(va.n), cl.vertex(vb.n))
            ce.length = edge.length

        return cl

    def __repr__(self):
        return '{} vertices, {} edges'.format(len(self.vertices), len(self.edges))


def build_graph(inpf, use_portals=True):
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
            if use_portals:
                other = portals.get((x,y))
                if other == (xx, yy):
                    continue
            edge = graph.add_edge(graph.vertex(name), graph.vertex(rdoors[(xx, yy)]))
            edge.length = path_len
    
    if use_portals:
        # add portals as edges with 0 length
        for a,b in portals.items():
            va = graph.vertex(rdoors[a])
            vb = graph.vertex(rdoors[b])
            edge = graph.add_edge(va, vb)
            edge.length = 1
    
    return graph


def build_multilevel_graph(inpf, levels):
    '''


    1.BB.in.outer          1.BB.in.inner
    1.BB.out.outer         1.BB.out.inner

    1.BB.in.outer --> 1.BB.out.inner
    1.BB.in.inner --> 1.BB.out.outer


    --------------------------------------

    1.BB.in.outer  -->   1.CC.


    '''
    grid, portals, dmap, dtypes = load_input(inpf)

    tunnels = {}
    for door, _ in dmap.items():
        door = door[0:2]
        if door not in ['AA', 'BB']:
            tunnels[door + '0'] = door + '1'
            tunnels[door + '1'] = door + '0'

    og = build_graph(inpf, False)
    graph = G()

    # def _get_outer_vertex(g, n):
    #     v = g.vertex(n)
    #     if v.type != 'outer':
    #         raise Exception('not outer: ' + v)
    #     vx = V(n, v.type)
    #     reachable_vertices = []
    #     for edge in v.out_edges:
    #         ov = edge.b
    #         reachable_vertices.append((ov.n, ov.type, edge.length))
        
    #     return (vx, reachable_vertices)
    

    # aa, reachable = _get_outer_vertex(og, 'AA')

    # graph.add_vertex(aa)
    # for n, tp, length in reachable:
    #     if tp == 'inner':
    #         v_in = V(n+'.in', 'inner')
    #         v_out = V(n+'.out', 'inner')
    #         graph.add_vertex(v_in)
    #         graph.add_vertex(v_out)
    #         graph.add_edge(aa, v_out, length)
    #         graph.add_edge(v_in, aa, length)
    
    level = 1
    while level < levels:
        for _, v in og.vertices.items():
            if v.n in ['AA', 'ZZ']:
                continue
            graph.add_vertex(V('{}.{}.in'.format(level, v.n), v.type))
            graph.add_vertex(V('{}.{}.out'.format(level, v.n), v.type))
        
        for _, edge in og.edges.items():
            a = edge.a
            b = edge.b


            if a.n in ('AA', 'ZZ') or b.n in ('AA', 'ZZ'):
                continue
            if a.type == b.type:
                # in -> out and in -> in
                graph.add_edge(graph.vertex('{}.{}.in'.format(level, a.n)),
                            graph.vertex('{}.{}.out'.format(level, b.n)),
                            edge.length)
                graph.add_edge(graph.vertex('{}.{}.in'.format(level, a.n)),
                            graph.vertex('{}.{}.in'.format(level, b.n)),
                            edge.length)
                graph.add_edge(graph.vertex('{}.{}.in'.format(level, b.n)),
                            graph.vertex('{}.{}.out'.format(level, a.n)),
                            edge.length)
                graph.add_edge(graph.vertex('{}.{}.in'.format(level, b.n)),
                            graph.vertex('{}.{}.in'.format(level, a.n)),
                            edge.length)
            elif a.type == 'outer':
                graph.add_edge(
                    graph.vertex('{}.{}.in'.format(level, a.n)),
                    graph.vertex('{}.{}.out'.format(level, b.n)),
                    edge.length)
                graph.add_edge(
                    graph.vertex('{}.{}.in'.format(level, b.n)),
                    graph.vertex('{}.{}.out'.format(level, a.n)),
                    edge.length)
                if level > 1:
                    prev_n = tunnels[a.n]
                    graph.add_edge(
                        graph.vertex('{}.{}.out'.format(level-1, prev_n)),
                        graph.vertex('{}.{}.in'.format(level, a.n)),
                        1
                    )
                    graph.add_edge(
                        graph.vertex('{}.{}.out'.format(level, a.n)),
                        graph.vertex('{}.{}.in'.format(level-1, prev_n)),
                        1
                    )
            else:
                pass
        
        level += 1


    aa = og.vertex('AA')
    a = graph.add_vertex(V('AA', 'outer'))
    for edge in aa.out_edges:
        b = edge.b
        if b.type == 'inner':
            graph.add_edge(
                a,
                graph.vertex('1.{}.in'.format(b.n)),
                edge.length + 1
            )
    
    zz = og.vertex('ZZ')
    z = graph.add_vertex(V('ZZ', 'outer'))
    for edge in zz.in_edges:
        a = edge.a
        if a.type == 'inner':
            graph.add_edge(
                graph.vertex('1.{}.out'.format(a.n)),
                z,
                edge.length + 1
            )

    for _, v in graph.vertices.items():
        print(v)
    
    for _, edge in graph.edges.items():
        print(edge)

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
    


input_file = 'test_input'

graph = build_graph(input_file)
print(graph)
print('Part 1:', dijkstra(graph))

mg = build_multilevel_graph(input_file, 2)
print(mg)
print('Part 2:', dijkstra(mg))
