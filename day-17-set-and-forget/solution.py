import sys
sys.path.append('..')

from tools.intcomp import ICC, load_program


def scan_scaffolds(prog_input):
    buff = []
    icc = ICC(load_program(prog_input), outq=lambda v: buff.append(chr(v)), quiet=True)
    icc.execute()
    buff = ''.join(buff)

    smap = []
    for line in buff.split('\n'):
        line = line.strip()
        if line:
            smap.append([c for c in line])
    
    return smap


def get_near(smap, x,y):
    near = []
    for xx, yy in [(x, y-1), (x-1, y), (x, y+1), (x+1, y)]:
        if xx >= 0 and xx < len(smap[0]) and yy >= 0 and yy < len(smap):
            near.append((xx, yy))
    return near


def is_intersection(smap, x, y):
    if smap[y][x] == '#':
        near = get_near(smap, x, y)
        if len(near) == 4:
            for xx, yy in near:
                if smap[yy][xx] != '#':
                    return False
            return True
    return False


def part1(prog_file):
    scaffolds = scan_scaffolds(prog_file)
    intersections = []
    for y in range(0, len(scaffolds)):
        for x in range(0, len(scaffolds[y])):
            if is_intersection(scaffolds, x, y):
                intersections.append((x,y))
    
    return sum([x*y for x,y in intersections])

directions = {
    '^': (0, -1),
    '<': (-1, 0),
    'V': (0, 1),
    '>': (1, 0),
}

turns = {
    # curr    left     right
    (0, -1): ((-1, 0),(1, 0)),
    (-1, 0): ((0, 1),(0, -1)),
    (0, 1):  ((1, 0),(-1, 0)),
    (1, 0):  ((0, -1),(0, 1)),
}

def _replace(arr, what, replacement):
    result = []

    i = 0
    while i < len(arr):
        if i + len(what) > len(arr):
            result.append(arr[i])
            i += 1
            continue
        j = 0
        while j < len(what):
            if arr[i+j] != what[j]:
                break
            j += 1
        if j == len(what):
            # match
            result += replacement
            i += j
            continue
        result.append(arr[i])
        i += 1

    return result


def reduce_path(path):

    start = 0
    while start < len(path):
        for i in range(0, 10): # Max 10
            if start + i + 1 > len(path):
                continue
            a = path[start: start + i + 1]
            ae = start + i + 1
            #print('ae=',ae, a)
            for j in range(0, 10):
                if ae + j + 1 > len(path):
                    continue
                b = path[ae: ae + j + 1]
                be = ae + j + 1
                #print('be=', be, b)
                for k in range(0, 10):
                    if be + k + 1 > len(path):
                        continue
                    c = path[be: be + k + 1]
                    t = _replace(path, a, 'A')
                    t = _replace(t, b, 'B')
                    t = _replace(t, c, 'C')
                    if set(t) == {'A', 'B', 'C'}:
                        print('OK')
                        ok = True
                        for aa in [a,b,c]:
                            if len(''.join(aa)) > 20:
                                ok = False
                                break
                        if not ok:
                            continue
                        return (t,{
                            'A': a,
                            'B': b,
                            'C': c,
                        })

        start += 1

    return None

class VacuumRobot:

    def __init__(self, prog_file):
        self.comp = ICC(load_program(prog_file), inpq=self.on_input, outq=self.on_out, quiet=True)
        self.comp.mem[0] = 2
        self.buff = []
        self.scaffolds = scan_scaffolds(prog_file)
        self.pos, self.dir = self.get_robot_position()
        self.dir = directions[self.dir]
        self.last_out = None
    
    def on_input(self):
        if self.buff:
            v = self.buff[0]
            print('  >>', v, chr(v))
            self.buff = self.buff[1:]
            return v
        while True:
            inp = input('>')
            if inp.strip():
                self.buff = [ord(c) for c in inp.strip()] + [10]
                return self.on_input()

    def on_out(self, v):
        if v > 255:
            print('ERR:', v)
        else:
            print(chr(v), end='')
        self.last_out = v
    
    def run(self):
        self.comp.execute()
    
    def get_robot_position(self):
        for y in range(0, len(self.scaffolds)):
            for x in range(0, len(self.scaffolds[y])):
                if self.scaffolds[y][x] in '><^V':
                    return ((x, y), self.scaffolds[y][x])
    
    def load_program(self, program, routines):
        prg = ','.join(program) + '\n'

        defs = []
        for key, tasks in routines.items():
            defs.append(','.join([t[0]+','+t[1:] for t in tasks]))
        
        prg += '\n'.join(defs) + '\n'

        self.buff = [ord(c) for c in prg]

    def walk_path_sim(self):
        path = []
        while True:
            ld, rd = turns[self.dir]
            
            turn = None
            turn_dir = None
            i = 0
            for lbl, xx, yy in [('L', *ld), ('R', *rd)]:
                x, y = self.pos
                x += xx
                y += yy
                if x >= 0 and x < len(self.scaffolds[0]) and y >= 0 and y < len(self.scaffolds):
                    if self.scaffolds[y][x] == '#':
                        turn = lbl
                        turn_dir = turns[self.dir][i]
                        break
                    i += 1
            
            if not turn:
                break
            self.dir = turn_dir
            i = 0
            while True:
                x, y = self.pos
                x += self.dir[0]
                y += self.dir[1]
                if x < 0 or x >= len(self.scaffolds[0]) or y < 0 or y >= len(self.scaffolds):
                    break
                if self.scaffolds[y][x] != '#':
                    break
                i += 1
                self.pos = (x,y)
            path.append(turn + str(i))
        
        return path
    

def part2(prog_file):
    vr = VacuumRobot(prog_file)
    print('Run interactively')
    #
    path = vr.walk_path_sim()
    program = reduce_path(path)
    if not program:
        print('Did not found program :(')
        return
    vr.load_program(*program)
    vr.run()
    return vr.last_out


#print('Part 1: ', part1('input'))
print('Part 2:', part2('input'))
