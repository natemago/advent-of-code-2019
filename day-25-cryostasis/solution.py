import sys


sys.path.append('..')


from tools.intcomp import ICC, load_program
from queue import Queue


def parse_output(buffer):
    messages = []
    lines = buffer.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i+=1
            continue
        if line.startswith('=='):
            message = {
                'doors': [],
                'items': [],
                'info': [],
                'title': line[2:-2].strip(),
            }
            
            messages.append(message)
            i += 1
            continue
        if line.strip() == 'Doors here lead:':
            i += 1
            line = lines[i].strip()
            while line.startswith('-'):
                message['doors'].append(line[2:].strip())
                i += 1
                line = lines[i].strip()
            continue
        if line.strip() == 'Items here:':
            i += 1
            line = lines[i].strip()
            while line.startswith('-'):
                message['items'].append(line[2:].strip())
                i += 1
                line = lines[i].strip()
            continue
        if line.strip() == 'Command?':
            break
        if i == 1:
            message = {
                'doors': [],
                'items': [],
                'info': [],
            }
            messages.append(message)
        message['info'].append(line)
        i+=1
    
    return messages

class Robot:

    def __init__(self, program, interactive=False, handler=None):
        self.comp = ICC(load_program(program),
                        quiet=True,
                        inpq=self.on_inp,
                        outq=self.on_out)
        self.comp.on_halt = self.on_halt
        self.outbuff = []
        self.inpbuff = []
        self.inpq = Queue()
        self.messages = None
        self.interactive = interactive
        self.handler = handler
    
    def on_out(self, v):
        self.outbuff.append(chr(v))
    
    def on_inp(self):
        if self.outbuff:
            self.messages = parse_output(''.join(self.outbuff))
            if self.interactive:
                for message in self.messages:
                    print('\n'.join(['%s: %s'%(k,v) for k,v in message.items()]))
            self.outbuff = []
        if not self.inpbuff:
            if self.interactive:
                self.inpbuff = input('CMD>') + '\n'
            else:
                if self.handler:
                    self.inpbuff = self.handler(self.messages)
                else:
                    raise Exception('input buffer empty')
        c = self.inpbuff[0]
        self.inpbuff = self.inpbuff[1:]
        return ord(c)
    
    def on_halt(self):
        self.messages = parse_output(''.join(self.outbuff))
        if self.interactive:
            for message in self.messages:
                print('\n'.join(['%s: %s'%(k,v) for k,v in message.items()]))
        self.outbuff = []
        if self.handler:
            self.handler(self.messages, halt=True)

    def run(self):
        self.comp.execute()
    
    def snapshot(self):
        return self.comp.snapshot(save=False)
    
    def send(self, command):
        self.inpbuff = [ord(c) for c in command] + [10]


from threading import Thread
from random import shuffle, randint
from time import sleep


items = []
visited = set()
directions = []
take = []
drop = []

def _handler(message, halt=None):
    print('\n'.join(['%s: %s' % e for e in message.items()]))
    print('Items:', items)
    print('Visited:', visited)
    print('-------------------')
    if halt:
        print('Game over')
        return
    if message.get('info'):
        info = ''.join(message['info']).lower()
        if 'password' in info or 'pass' in info:
            input('Maybe password?')
        
        if 'droids on this ship are lighter than the detected value' in info:
            if items:
                shuffle(items)
                for i in range(0, randint(0, len(items))):
                    item = items[i]
                    drop.append(item)
                return
    #sleep(0.1)
    if drop:
        if message.get('title', '') != 'Pressure-Sensitive Floor':
            shuffle(drop)
            item = drop.pop()
            items.remove(item)
            return 'drop ' + item + '\n'
    if message.get('title'):
        visited.add(message['title'])

        if message['doors']:
            directions.clear()
            for d in message['doors']:
                directions.append(d)
        
        if message['items']:
            take.clear()
            itms = message['items']
            shuffle(itms)
            for i in range(0, randint(1, len(itms))):
                take.append(itms[i])
    if take:
        item = take.pop()
        if item not in ['photons', 'molten lava', 
                        'giant electromagnet', 'infinite loop',
                        'escape pod']:
            items.append(item)
            return 'take ' + item + '\n'
    if directions:
        shuffle(directions)
        return directions.pop() + '\n'

def handler(messages, halt=None):
    command = None
    for message in messages:
        cmd = _handler(message, halt)
        if cmd:
            command = cmd
    
    return command



robot = Robot('input', handler=handler)
robot.run()