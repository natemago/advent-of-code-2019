import sys
sys.path.append('..')


from tools.intcomp import ICC, load_program
from queue import Queue
from threading import Thread
import curses
from threading import Thread, Timer, Event

class UI:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, win):
        pass

class Text(UI):

    def __init__(self, text, x, y, width, height):
        super(Text, self).__init__(x,y,width,height)
        self.text = text

    def draw(self, win):
        if isinstance(self.text, list):
            for i in range(0, min(len(self.text), self.height)):
                win.addnstr(self.x, self.y+i, self.text[i], self.width)
            return
        win.addstr(self.x, self.y, self.text)

class Map(Text):

    def __init__(self, gmap, gport, x, y, width, height):
        super(Map, self).__init__('', x, y, width, height)
        self.gmap = gmap
        self.gport = gport
    
    def get_text(self):
        gx, gy = self.gport
        text = []
        for i in range(gy, gy + self.height):
            row = ''
            for j in range(gx, gx + self.width):
                row += self.gmap.get((j, i), ' ')
            text.append(row)
        return text
    
    def draw(self, win):
        self.text = self.get_text()
        super(Map, self).draw(win)


class Screen:

    def __init__(self):
        self._redraw = Event()
        self._main_loop = Thread(target=self._draw)
        self.children = []
        self.inp = Queue()
    
    def add(self, child):
        self.children.append(child)

    def draw(self, win):
        while self._redraw.wait():
            win.clear()
            for ui in self.children:
                ui.draw()
            win.refresh()
            try:
                k = win.getkey()
                self.inp.put(k)
            except:
                return

    def _draw(self):
        curses.wrapper(self.draw)
    
    def show(self):
        self._main_loop.start()
    
    def refresh(self):
        self._redraw.set()
    
    def get_input(self):
        return self.inp.get()

class Robot:

    def __init__(self, prog_file, on_out=None, on_in=None):
        self.inq = Queue()
        self.comp = ICC(load_program(prog_file), inpq=self._on_input, outq=self._on_out, quiet=True)
        self.pos = (0,0)
        self.on_out = on_out
        self.on_in = on_in
        self.comp.on_halt = lambda: print('>>GAME OVER<<')

    def _on_input(self):
        if self.on_in:
            v = self.on_in()
            if v is not None:
                self.inq.put(v)
        return self.inq.get()
    
    def _on_out(self, v):
        if self.on_out:
            self.on_out(chr(v))
            return
        print(chr(v), end='')

    def run(self):
        self.comp.execute()

    def send_cmd(self, cmd):
        for c in cmd + '\n':
            self.inq.put(ord(c))

    def go(self, direction):
        self.send_cmd(direction)
    
    def take(self, item):
        self.send_cmd('take ' + item)
    
    def drop(self, item):
        self.send_cmd('drop ' + item)
    
    def inventory(self):
        self.send_cmd('inv')

class DisplayTerminal:
    
    def __init__(self, robot_program):
        self.robot = Robot(robot_program, self._on_out, self._on_in)
        self.robot.comp.on_halt = self._on_halt
        self.stdin_thread = Thread(target=self._read_user_input)
        self.stdin_thread.start()
        self.map = {}
        self.pos = (0,0)
        self.outbuff = ''
        self.doors = []
        self.items = []
        self.screen = Screen()
        self.screen.add(Text('Exploratory Robot: ', 0, 0, 130, 1))
        self.screen.add(Map(self.map, (-25, -15), 0, 1, 50, 30))

    def _on_out(self, c):
        self.outbuff += c
    
    def _on_in(self):
        if self.outbuff:
            self.output_available(self.outbuff)
            self.outbuff = ''

    def output_available(self, buffer):
        self._parse_buffer(buffer)

    def _parse_buffer(self):
        buff = buffer.strip()
        directions = False
        items = False
        self.doors = []
        self.items = []
        if not buff.strip().endswith('Command?'):
            print(buff)
            return
        for line in buff.splitlines():
            line = line.strip()
            if line == 'Doors here lead:':
                directions = True
                items = False
                continue
            if line == 'Items here:':
                directions = False
                items = True
                continue
            if line == 'Command?':
                break
            if directions:
                if line:
                    self.doors.append(line[2:])
                    continue
            elif items:
                if line:
                    self.items.append(line[2:])
                    continue

    def _on_halt(self):
        if self.outbuff:
            print(self.outbuff)
        print('GAME OVER')

    def _read_user_input(self):
        while True:
            inp = input('>')
            self.robot.send_cmd(inp)
    
    def run_robot(self):
        self.robot.run()




# terminal = DisplayTerminal('input')
# terminal.run_robot()

screen = Screen()
screen.show()
screen.refresh()