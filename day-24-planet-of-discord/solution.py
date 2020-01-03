def load_input(inpf):
    grid = []
    with open(inpf) as f:
        for line in f:
            grid.append([c for c in line.strip()])
    return grid


def get_adjacent(grid, x, y):
    adj = []
    for dx, dy in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
        xx, yy = dx+x, dy+y
        if xx >= 0 and xx < len(grid[0]) and yy >= 0 and yy < len(grid):
            adj.append(grid[yy][xx])
    return adj



def next_iter(grid):
    ng = []
    for y in range(0, len(grid)):
        row = []
        for x in range(0, len(grid[y])):
            adj = get_adjacent(grid, x, y)
            bugs = sum([1 if c == '#' else 0 for c in adj])
            curr = grid[y][x]
            if curr == '#':
                if bugs == 0 or bugs > 1:
                    curr = '.'
            elif curr == '.':
                if bugs in [1,2]:
                    curr = '#'
            row.append(curr)
        ng.append(row)
    return ng

def biodiv_rating(grid):
    p = 0
    rating = 0
    for r in grid:
        for c in r:
            if c == '#':
                rating += 2**p
                print('@', p, 'plus', 2**p)
            p += 1
    return rating

def print_grid(grid):
    print('\n'.join(''.join(r) for r in grid))



def count_bugs(grid):
    return sum([sum([1 if c == '#' else 0 for c in row]) for row in grid])

class RecursivelyFoldedGrids:

    def __init__(self, start_grid):
        self.grids = {
            0: start_grid,
        }
    
    def grid_at(self, level):
        grid = self.grids.get(level)
        if not grid:
            grid = [['.' for i in range(0, 5)] for _ in range(0, 5)]
            grid[2][2] = '?'
            self.grids[level] = grid
        return grid
    
    def get_adjacent(self, x,y, level):
        grid = self.grid_at(level)
        adjacent = []
        for xx, yy, up_level, down_level in [
            (x-1, y, 'right', (1, 2)),
            (x+1, y, 'left', (3, 2)),
            (x, y-1, 'down', (2, 1)),
            (x, y+1, 'up', (2, 3)),
            ]:
            if (xx, yy) == (2,2):
                # go level up (the nested grid)
                nested = self.grid_at(level + 1)
                if up_level == 'left':
                    # print('  ..',x,y,level, '@',xx,yy,'+adj=',[nested[i][0] for i in range(0, 5)])
                    # print('  ..',level +1, nested)
                    # print(' .....')
                    adjacent += [nested[i][0] for i in range(0, 5)]
                elif up_level == 'right':
                    adjacent += [nested[i][4] for i in range(0, 5)]
                elif up_level == 'down':
                    adjacent += nested[4]
                else:
                    adjacent += nested[0]
            elif xx < 0 or xx > 4 or yy < 0 or yy > 4:
                # outside this rectangle (from the grid encasing this grid)
                encasing = self.grid_at(level - 1)
                ex, ey = down_level
                adjacent.append(encasing[ey][ex])
            else:
                adjacent.append(grid[yy][xx])
        return adjacent
    
    def next_minute_at_level(self, level):
        ng = []
        grid = self.grid_at(level)

        for y in range(0, 5):
            row = []
            for x in range(0, 5):
                if (x, y) == (2, 2):
                    row.append('?')
                    continue
                tile = grid[y][x]
                adjacent = self.get_adjacent(x, y, level)
                bugs = sum([1 if t == '#' else 0 for t in adjacent])
                if tile == '#':
                    if bugs == 0 or bugs > 1:
                        row.append('.')
                        continue
                elif tile == '.':
                    if bugs in [1,2]:
                        row.append('#')
                        continue
                row.append(tile)
            ng.append(row)

        return ng

    def next_minute(self):
        levels = sorted(self.grids.keys())
        grids = {
            0: self.next_minute_at_level(0),
        }

        i = -1
        while True:
            grid = self.next_minute_at_level(i)
            if count_bugs(grid) == 0 and i < min(levels):
                break
            grids[i] = grid
            i -= 1
        
        i = 1
        while True:
            grid = self.next_minute_at_level(i)
            if count_bugs(grid) == 0 and i > max(levels):
                break
            grids[i] = grid
            i += 1
        self.grids.update(grids)
    
    def bugs_count(self):
        bugs = 0
        for _, grid in self.grids.items():
            for r in grid:
                for c in r:
                    if c == '#':
                        bugs += 1
        return bugs


def part1(inpf):
    grid = load_input(inpf)
    states = {}
    count = 0
    states[''.join([''.join(r) for r in grid])] = 0
    print_grid(grid)
    while True:
        grid = next_iter(grid)
        print(' ---- ')
        print_grid(grid)
        state = ''.join([''.join(r) for r in grid])
        if states.get(state) is not None:
            return biodiv_rating(grid)
        states[state] = count
        count += 1
        print(count)



def part2(inpf, iterations):
    grids = RecursivelyFoldedGrids(load_input(inpf))

    for i in range(0, iterations):
        grids.next_minute()
    
    return grids.bugs_count()

print('Part 1:', part1('input'))
print('Part 2:', part2('input', 200))