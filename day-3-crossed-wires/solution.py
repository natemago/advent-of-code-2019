def mark(board, x, y, wire, steps):
    if board.get((x,y)) and not board[(x,y)].get(wire):
        board[(x,y)][wire] = steps
        board[(x,y)]['X'] = sum([v for _,v in board[(x,y)].items()])
        return
    if not board.get((x,y)):
        board[(x,y)] = {}
    board[(x,y)][wire] = steps


def trace_path(instructions, wire, board):
    x = 0
    y = 0
    count = 0
    mark(board, x, y, wire, count)
    for inst in instructions:
        direction = inst[0]
        steps = int(inst[1:])
        for i in range(0, steps):
            if direction == 'L':
                x -= 1
            elif direction == 'U':
                y -= 1
            elif direction == 'R':
                x += 1
            else: # down
                y += 1
            count += 1
            mark(board, x, y, wire, count)

def load_wires(inpf):
    wires = {}
    wire = 0
    with open(inpf) as f:
        for line in f:
            line = line.strip()
            if line:
                wire += 1
                wires[wire] = [i.strip() for i in line.split(',')]
    return wires

def part1():
    wires = load_wires('input')
    board = {}
    for wire, instructions in wires.items():
        trace_path(instructions, wire, board)
    
    intersections = []
    for pos, v in board.items():
        if pos != (0,0) and v.get('X'):
            intersections.append(pos)
    
    closest_intersection = sorted(intersections, key=lambda pos: abs(pos[0]) + abs(pos[1]))[0]

    return abs(closest_intersection[0]) + abs(closest_intersection[1])


def part2():
    wires = load_wires('input')
    board = {}
    for wire, instructions in wires.items():
        trace_path(instructions, wire, board)
    
    intersections = []
    for pos, v in board.items():
        if pos != (0,0) and v.get('X'):
            intersections.append((pos, v['X']))
    
    least_steps = sorted(intersections, key=lambda p: p[1])
    return least_steps[0][1]

print('Part 1: ', part1())
print('Part 2: ', part2())
