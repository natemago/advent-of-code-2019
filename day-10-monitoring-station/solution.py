from queue import Queue
from math import atan2, sin, cos, pi as Pi

def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)

def load_input(inpf):
    grid = []
    with open(inpf) as f:
        for line in f:
            grid.append([1 if c == '#' else 0 for c in line.strip()])
    return grid

def mark_hidden(grid, zx, zy, ax, ay):
    #print('Mark hidden: ', ax, ay)
    x = zx
    y = zy
    d = gcd(abs(ax), abs(ay))
    #print('d=',d)

    ax = ax // d
    ay = ay // d
    while True:
        x += ax
        y += ay

        if x >= 0 and x < len(grid[0]) and y >= 0 and y < len(grid):
            grid[y][x] = -1
        else:
            break


def print_grid(grid, x=None, y=None):
    marks = {
        -3: 'V',
        -2: '.',
        -1: 'H',
        0: '.',
        1: '#'
    }
    yy = 0
    for row in grid:
        xx = 0
        for c in row:
            if xx == x and yy == y:
                print('X', end='')
            else:
                print(marks[c], end='')
            xx += 1
        yy += 1
        print('')


def get_neighbours(grid, x, y):
    neighbours = []
    for xx, yy in [
        (x-1, y-1), (x, y-1), (x+1, y-1),
        (x-1, y),             (x+1, y),
        (x-1, y+1), (x, y+1), (x+1, y+1),
    ]:
        if xx >= 0 and xx < len(grid[0]) and yy >= 0 and yy < len(grid):
            if grid[yy][xx] >= 0:
                neighbours.append((xx, yy))
    
    return neighbours

def check_visible_asteroids(grid, x, y):
    grid = [[c for c in r] for r in grid]  # clone grid
    q = Queue()
    q.put((x,y))
    
    count = 0
    break_at = 0
    while not q.empty():
        xx, yy = q.get()
        seen = -2
        if grid[yy][xx] < 0:
            continue # seen
        if grid[yy][xx] == 1 and (xx, yy) != (x,y):
            count += 1
            mark_hidden(grid, xx, yy, xx-x, yy-y)
            seen = -3

        # mark
        grid[yy][xx] = seen  # seen
        neighbours = get_neighbours(grid, xx, yy)
        for n in neighbours:
            q.put(n)
    #print_grid(grid, x, y)
    return (count, grid)


def get_asteroids(grid):
    asteroids = []
    y = 0
    for row in grid:
        x = 0
        for c in row:
            if c == 1:
                asteroids.append((x,y))
            x += 1
        y += 1
    return asteroids


def find_best_asteroid(inpf):
    grid = load_input(inpf)
    visible_count = []
    for asteroid in get_asteroids(grid):
        #print('Counting for:', asteroid)
        cnt, marked = check_visible_asteroids(grid, asteroid[0], asteroid[1])
        visible_count.append((asteroid, cnt, marked))
    
    visible_count = sorted(visible_count, key=lambda c: c[1])
    return visible_count[-1]


def rot(p, ang):
    x,y = p
    return (
        x*cos(ang) - y * sin(ang),
        x*sin(ang) + y *cos(ang)
    )

def print_grid_sparse(grid, x=None, y=None):
    marks = {
        -2: 'S',
        -1: 'H',
        0: '.',
    }
    yy = 0
    for row in grid:
        xx = 0
        for c in row:
            if xx == x and yy == y:
                print('   X', end='')
            else:
                m = marks.get(c)
                if m is None:
                    print('%4d' % c, end='')
                else:
                    print('%4s' % marks[c], end='')
            xx += 1
        yy += 1
        print('')

def find_visible(grid, sx, sy):
    visible = []

    y = 0
    for row in grid:
        x = 0
        for c in row:
            if c == -3:
                # translate
                xx = x - sx
                yy = y - sy
                # rotate Pi/2
                xx, yy = rot((xx, yy), -Pi/2)
                # calculate atan
                visible.append((x, y, atan2(yy,xx)))
            x += 1
        y += 1

    return visible


def part2(asteroid, count, grid):
    print_grid(grid, *asteroid)
    visible = find_visible(grid, *asteroid)
    visible = sorted(visible, key=lambda g: g[2])
    two_hund = visible[199]
    i = 1
    for v in visible:
        grid[v[1]][v[0]] = i
        i += 1
    
    print_grid_sparse(grid, *asteroid)
    return two_hund[0]*100 + two_hund[1]

def part1():
    best = find_best_asteroid('input')
    print('Part 1: ', best[1])
    return best

print('Grid:')
print_grid(load_input('input'))
print('====================================')
print('** Solutions **')
best = part1()
print('Part 2:', part2(*best))