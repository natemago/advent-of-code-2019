import re

class Moon:

    def __init__(self, pos):
        self.pos = pos
        self.v = [0,0,0]
    
    def move(self):
        self.pos = (
            self.pos[0] + self.v[0],
            self.pos[1] + self.v[1],
            self.pos[2] + self.v[2]
        )
    
    def apply_gravity(self, b):
        for i in range(0, 3):
            pa = self.pos[i]
            pb = b.pos[i]
            if pa > pb:
                self.v[i] -= 1
                b.v[i] += 1
            elif pa == pb:
                continue
            else:
                self.v[i] += 1
                b.v[i] -= 1
    
    def total_energy(self):
        potential = sum([abs(p) for p in self.pos])
        kinetic = sum([abs(v) for v in self.v])
        return potential * kinetic
    
    def __repr__(self):
        return 'pos=<x={}, y={}, z={}> vel=<x={}, y={}, z={}>'.format(*self.pos,*self.v)

    def __str__(self):
        return self.__repr__()

class Simulation:

    def __init__(self, bodies):
        self.bodies = bodies
        self.states = {0: {}, 1: {}, 2: {}}
        self.found = {}
    
    def cycle(self):
        for i in range(0, len(self.bodies) - 1):
            for j in range(i+1, len(self.bodies)):
                a,b = self.bodies[i], self.bodies[j]
                a.apply_gravity(b)
        
        for body in self.bodies:
            body.move()
    
    def run_simulation(self, steps):
        for i in range(0, steps):
            #print('After {} steps:'.format(i))
            #self.print_bodies()
            self.cycle()
    

    def _state(self, axis):
        return '{}:{}'.format(
            ','.join([str(b.pos[axis]) for b in self.bodies]),
            ','.join([str(b.v[axis]) for b in self.bodies]))

    def find_cycle(self):
        i = 0
        while True:
            self.cycle()
            for ax in range(0, 3):
                if self.found.get(ax):
                    continue
                state = self._state(ax)
                cycle = self.states[ax].get(state)
                if cycle is not None:
                    self.found[ax] = {
                        'start': cycle,
                        'length': i - cycle,
                    }
                    print('Found for {} - {}'.format(ax, self.found[ax]))
                self.states[ax][state] = i
            if len(self.found) == 3:
                break
            i += 1

        if self.found[0]['start'] == 0 and self.found[1]['start'] == 0 and self.found[2]['start'] == 0:
            return compute_lcm(self.found[0]['length'], self.found[1]['length'], self.found[2]['length'])

        raise Exception("Cannot calculate right now :)")

    def total_energy(self):
        return sum([b.total_energy() for b in self.bodies])
    
    def print_bodies(self):
        for b in self.bodies:
            print(b)

def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)

def _compute_lcm(x, y):
   return x*y//gcd(x,y)

def compute_lcm(*args):
    print('Compute lcm:', args)
    if len(args) == 2:
        return _compute_lcm(args[0], args[1])
    vals = [_compute_lcm(args[0], args[1]), *args[2:]]
    return compute_lcm(*vals)

def load_bodies(inpf):
    bodies = []
    with open(inpf) as f:
        for line in f:
            m = re.search(r'\<x=(?P<x>[-?\d]+), y=(?P<y>[-?\d]+), z=(?P<z>[-?\d]+)\>', line)
            if not m:
                raise Exception('Line: ' + line)
            x,y,z = int(m.group('x')),int(m.group('y')),int(m.group('z'))
            bodies.append(Moon(pos=[x,y,z]))
    return bodies

def part1():
    simulation = Simulation(load_bodies('input'))
    simulation.run_simulation(1000)
    return simulation.total_energy()

def part2():
    simulation = Simulation(load_bodies('input'))
    return simulation.find_cycle()

print('Part 1: ', part1())
print('Part 2:', part2())