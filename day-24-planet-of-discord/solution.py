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



class Grids:

    def __init__(self, lzgrid):
        self.grids = [lzgrid]
        self.zgrid = 0
        self.get_grid(-1)
        self.get_grid(1)
    
    def get_grid(self, level):
        level = level + self.zgrid
        if level >= 0 and level < len(self.grids):
            return self.grids[level]
        if level == -1:
            grid = [['.' for i in range(0, 5)] for j in range(0, 5)]
            grid[2][2] = '?'
            self.grids = [grid] + self.grids
            self.zgrid += 1
            return grid
        if level < -1:
            raise Exception('Level too low: ' + str(level))
        if level == len(self.grids):
            grid = [['.' for i in range(0, 5)] for j in range(0, 5)]
            grid[2][2] = '?'
            self.grids.append(grid)
            return grid
        raise Exception('Level too high: ' + str(level))

    def get_grid_side(self, level, side):
        grid = self.get_grid(level)
        if side == 'top':
            return grid[0]
        if side == 'left':
            return [grid[i][0] for i in range(0, 5)]
        if side == 'right':
            return [grid[i][4] for i in range(0, 5)]
        if side == 'bottom':
            return grid[4]
        raise Exception('Invalid grid side: ' + side)

    def get_adjacent(self, level, x, y):
        adj = []
        grid = self.get_grid(level)
        for dx, dy, inside_grid_side, up_level in [
            (-1, 0, 'right', (1, 2)),
            (0, 1, 'bottom', (2, 1)),
            (1, 0, 'left', (3, 2)),
            (0, -1, 'top', (2, 3))]:
            xx, yy = dx + x, dy + y
            if xx >= 0 and xx < 5 and yy >= 0 and yy < 5:
                curr = grid[yy][xx]
                if curr == '?':
                    # plus the side of the top level grid
                    adj += self.get_grid_side(level + 1, inside_grid_side)
                else:
                    adj.append(curr)
            else:
                # get the tile from the grid containing this grid
                top_grid = self.get_grid(level-1)
                tx, ty = up_level
                adj.append(top_grid[ty][tx])
        
        return adj

    def bug_rule(self, tile, adjacent):
        if tile == '?':
            return None # skip
        bugs = sum([1 if t == '#' else 0 for t in adjacent])
        if tile == '#':
            if bugs == 0 or bugs > 1:
                return '.'
        elif tile == '.':
            if bugs in [1,2]:
                return '#'
        return tile
    
    def next_iteration(self, level):
        ng = []
        grid = self.get_grid(level)
        for y in range(0, len(grid)):
            row = []
            for x in range(0, len(grid[y])):
                if x == 2 and y == 2:
                    row.append('?')
                    continue
                adjacent = self.get_adjacent(level, x, y)
                tile = grid[y][x]
                row.append(self.bug_rule(tile, adjacent))
            ng.append(row)
        return ng
    
    def next_phase(self):
        grids = []
        # calculate level zero
        grids.append(self.next_iteration(0))

        # calculate up
        i = self.zgrid
        level = 1
        for i in range(self.zgrid + 1, len(self.grids)):
            grids.append(self.next_iteration(level))
            level += 1
        
        i = self.zgrid - 1
        level = -1
        while i >= 0:
            grids += [self.next_iteration(level)]
            level -= 1
            i -= 1
        
        if len(self.grids) - len(grids) != 2:
            # we have more grids than expected?
            raise Exception('Currently having %d grids and there are new %d grids' % (en(self.grids), len(grids)))
    
        # replace the grids with the new state
        for i in range(0, len(grids)):
            self.grids[i+1] = grids[i]

    def get_number_of_bugs(self):
        count = 0
        for grid in self.grids:
            for row in grid:
                for c in row:
                    if c == '#':
                        count += 1
        return count


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
    zg = load_input(inpf)
    zg[2][2] = '?'
    grids = Grids(zg)

    for i in range(0, iterations):
        print('Phase', i)
        grids.next_phase()

    i = 0
    for grid in grids.grids:
        print('Level: ', i - grids.zgrid)
        print_grid(grid)
        print('---------')
        i += 1
    return grids.get_number_of_bugs()

#print('Part 1:', part1('input'))
print('Part 2:', part2('test_input', 1))