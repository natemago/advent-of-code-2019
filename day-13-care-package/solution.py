import sys

sys.path.append('..')

from tools.intcomp import ICC, load_program
from time import sleep

class Arcade:

    def __init__(self, game_file, coins=None, animate=False):
        self.comp = ICC(load_program(game_file),
                        inpq=self._on_input,
                        outq=self._on_out,
                        quiet=True)
        self.buff = []
        self.grid = {}
        self.score = 0
        self.animate = animate
        if coins:
            self.comp.mem[0] = coins

    def _on_out(self, v):
        self.buff.append(v)
        if len(self.buff) == 3:
            self._on_cmd(*self.buff)
            self.buff = []
    
    def _on_cmd(self, x, y, tid):
        if x == -1 and y == 0:
            self.score = tid
            return
        self.grid[(x,y)] = tid
    
    def _find_pos(self, tile):
        for pos, tid in self.grid.items():
            if tid == tile:
                return pos

    def _move(self):
        ball_pos = self._find_pos(4)
        paddle = self._find_pos(3)
        if paddle[0] < ball_pos[0]:
            return 1
        elif paddle[0] > ball_pos[0]:
            return -1
        else:
            return 0

    def _on_input(self):
        if self.animate:
            self.print_gird()
        # inp = input('ARC>') or ''
        # return int(inp.strip() or '0')
        move = self._move()
        if self.animate:
            sleep(0.1)
        return move

    def run(self):
        self.comp.execute()
    
    def print_gird(self):
        blocks = {
            0: ' ',
            1: '▓',
            2: '#',
            3: '▂',
            4: 'o',
        }
        a = min(x for x,_ in self.grid.keys())
        b = max(x for x,_ in self.grid.keys())
        c = min(y for _,y in self.grid.keys())
        d = max(y for _,y in self.grid.keys())

        print('Score:', self.score)
        for i in range(c, d+1):
            for j in range(a, b+1):
                tile = self.grid.get((j,i), 0)
                print(blocks[tile], end='')
            print()
    

def part1():
    arcade = Arcade('input')
    arcade.run()
    count = 0
    for _, tid in arcade.grid.items():
        if tid == 2:
            count += 1
    arcade.print_gird()
    return count

def part2(animate=False):
    arcade = Arcade('input', 2, animate=animate)
    arcade.run()
    arcade.print_gird()


print('Part 1:', part1())
print('Part 2: Simulating the game...')
part2(True)