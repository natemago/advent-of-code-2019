import sys

sys.path.append('..')

from tools.intcomp import ICC, load_program


def turn_left(x, y):
    return (y, -x)

def turn_right(x, y):
    return (-y, x)



class PaintRobot:

    def __init__(self, shield):
        self.state = 'color'
        self.pos = (0,0)
        self.direction = (0, -1)
        self.shield = shield
        self.states = {
            'color': 'dir',
            'dir': 'color'
        }
    
    def scan_shield(self):
        return self.shield.get(self.pos, 0)

    def move(self):
        self.pos = (self.pos[0] + self.direction[0], self.pos[1] + self.direction[1])

    def next(self, v):
        if self.state == 'color':
            if v not in [0, 1]:
                raise Exception('Ivalid color: ' +  v)
            self.shield[self.pos] = v
            #print('PAINT')
        else:
            if v not in [0, 1]:
                raise Exception('Ivalid direction: ' +  v)
            self.direction = turn_right(*self.direction) if v else turn_left(*self.direction)
            self.move()
        self.state = self.states[self.state]
        #print('MOVE')

def print_shield(shield):
    sx = min([x for x,_ in shield.keys()])
    ex = max([x for x,_ in shield.keys()])
    sy = min([y for _, y in shield.keys()])
    ey = max([y for _, y in shield.keys()])
    for y in range(sy, ey+1):
        for x in range(sx, ex + 1):
            print('#' if shield.get((x,y)) else '.', end='')
        print()

def test():
    shield = {}
    robot = PaintRobot(shield)

    for v in [1,0, 0,0, 1,0, 1,0, 0,1, 1,0, 1,0]:
        robot.next(v)
        print_shield(shield)
        print('------------')
    
    print(shield)
    print(len(shield))


def part1():
    shield = {}
    robot = PaintRobot(shield)
    def on_scan():
        return robot.scan_shield()
    
    def on_paint(v):
        robot.next(v)

    comp = ICC(load_program('input'), inpq=on_scan, outq=on_paint)
    comp.execute()

    return len(shield)

def part2():
    shield = {}
    shield[(0,0)] = 1
    robot = PaintRobot(shield)
    def on_scan():
        return robot.scan_shield()
    
    def on_paint(v):
        robot.next(v)
        #print_shield(shield)

    comp = ICC(load_program('input'), inpq=on_scan, outq=on_paint)
    comp.execute()

    print_shield(shield)


print('Part 1:', part1())
part2()