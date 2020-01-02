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


#print('Part 1: ', part1('input'))
test('test_input')