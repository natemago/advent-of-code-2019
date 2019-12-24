import sys

sys.path.append('..')

from tools.intcomp import ICC, load_program

class TractorBeam:

    def __init__(self, prog_file):
        self.comp = ICC(load_program(prog_file),inpq=self.on_input, outq=self.on_out, quiet=True)
        self.area = {}
        self.pos = []
        self.buff = []
        self._bc = 0
    
    def load_coordinates(self):
        for i in range(0, 50):
            for j in range(0, 50):
                self.buff.append(i)
                self.buff.append(j)
    
    def on_input(self):
        c = self.buff[0]
        self._bc += 1
        self.pos.append(c)
        self.buff = self.buff[1:]
        #print('>',c)
        return c
    
    def on_out(self, v):
        self.area[(self.pos[0], self.pos[1])] = v
        #print(':', v, 'on', self.pos)
        self.pos = []

    def scan_area(self):
        while self.buff:
            self.comp.snapshot()
            self.comp.execute()
            self.comp.reset()
    
    def scan_position(self, x, y):
        if self.area.get((x,y)) is not None:
            return self.area[(x,y)]
        self.buff = [x,y]
        self.comp.snapshot()
        self.comp.execute()
        self.comp.reset()
        return self.area[(x,y)]
    
    def _area_count_on(self, axis, dist, start, end):
        return sum([self.area.get((dist, i) if axis else (i, dist), 0) for i in range(start, end+1)])

    def get_estimates(self):
        sx, ex = 0,49
        sy, ey = 0, 49

        while True:
            # walk left until there are not tiles horizontally
            if self._area_count_on(0, ey, sx, ex) >= 0:
                break
            ex -= 1
        
        while True:
            # walk up until the number of vertical == number of horizontal
            if abs(self._area_count_on(0, ey, sx, ex) - self._area_count_on(1, ex, sy, ey)) <= 1:
                break
            # walk up
            ey -= 1
        
        square_size = (self._area_count_on(0, ey, sx, ex) + self._area_count_on(1, ex, sy, ey))/2
        return (ex, ey, square_size)
    
    def calculate_position(self):
        dx, dy, square = self.get_estimates()

        return (((dx-square) * 100 / square), ((dy-square) * 100/square))
    
    def print_area(self):
        a = min([x for x,_ in self.area.keys()])
        b = max([x for x,_ in self.area.keys()])
        c = min([y for _,y in self.area.keys()])
        d = max([y for _,y in self.area.keys()])

        for y in range(c, d+1):
            for x in range(a, b+1):
                print('#' if self.area.get((x,y), 0) else '.', end='')
            print()
    
    def check_pos(self, x, y):
        cx = 0
        cy = 0
        i = 0
        while True:
            if not self.scan_position(x + i, y):
                break
            cx += 1
            i += 1

        i = 0
        for i in range(0, 100):
            if not self.scan_position(x, y+i):
                break
            cy += 1
            i += 1
        
        return (cx, cy)

def part1(prog_file):
    beam = TractorBeam(prog_file)
    beam.load_coordinates()
    beam.scan_area()
    beam.print_area()
    return sum([v for _,v in beam.area.items()])

def part2(prog_file):
    beam = TractorBeam(prog_file)
    beam.load_coordinates()
    beam.scan_area()
    beam.print_area()
    print('Estimates: ', beam.get_estimates())
    xest, yest = beam.calculate_position()
    print('Full Square position (est): ',xest, yest)
    xest = int(xest)
    yest = int(yest)
    
    x = xest
    y = yest
    while True:
        dx, dy = beam.check_pos(x,y)
        print('@', (x,y), 'is', (dx,dy))
        if dx == 100 and dy == 100:
            return x*10000 + y
        if dx < 100:
            y += 1
        else:
            if dx >= 100:
                y -= 1
        if dy < 100:
            x += 1
        else:
            if dy > 100:
                x -= 1
        


print('Part 1:', part1('input'))
print('Part 2:', part2('input'))