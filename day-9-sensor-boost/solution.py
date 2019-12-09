inst_set = {
    1: {
        'mnem': 'add',
        'params': 3,
    },
    2: {
        'mnem': 'mul',
        'params': 3,
    },
    3: {
        'mnem': 'read',
        'params': 1,
    },
    4: {
        'mnem': 'out',
        'params': 1,
    },
    5: {
        'mnem': 'jmp',
        'params': 2,
    },
    6: {
        'mnem': 'jmpz',
        'params': 2,
    },
    7: {
        'mnem': 'lt',
        'params': 3,
    },
    8: {
        'mnem': 'eq',
        'params': 3,
    },
    99: {
        'mnem': 'halt',
        'params': 0,
    },
}


class Disassembler:
    
    def __init__(self, mem):
        self.mem = mem
    
    def _decode_instr(self, instr):
        op = instr%100
        instr //= 100
        a = instr%10
        instr //= 10
        b = instr%10
        instr //= 10
        c = instr%10
        instr //= 10

        return (op, a, b, c)
    
    def _disassemble_at(self, ip):
        instr = self.mem.get(ip)
        if instr is None:
            return ('', -1)
        if instr == 0:
            return ('[N/A] OP is zero (?)', 0)
        op, ma, mb, mc = self._decode_instr(instr)
        isdef = inst_set.get(op)
        if not isdef:
            return ('[N/A] Invalid OP: {}'.format(op), 0)
        modes = [ma, mb, mc]
        params = []
        for i in range(0, isdef['params']):
            param = self.mem.get(ip + i + 1)
            param = '0x{:04X}'.format(param)
            if not modes[i]:
                param = '@' + param
            else:
                param = ' ' + param
            params.append(param)
        return ('{:5} {}'.format(isdef['mnem'], ', '.join(params)), isdef['params'])
    
    def disassemble(self, start, op_count=1):
        ip = start
        n = op_count or 0
        while n or op_count is None:
            disasm, pc = self._disassemble_at(ip)
            n -= 1
            ip += pc + 1
            yield (disasm, ip)
            if pc < 0:
                break
    
    def dump_mem(self):
        for line, address in self.disassemble(start=0, op_count=None):
            yield '0x{:04X}: {}'.format(address, line)


class ICC:

    def __init__(self, mem, inpq=None):
        self.mem = mem
        self.ip = 0
        self.inpq = inpq or []
        self.verbose = False
        self.disasm = Disassembler(mem)
        self.base = 0
        self.out = None

    def log(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)

    def fetch(self):
        # fetch the instruction
        instr = self.mem[self.ip]
        self.ip += 1
        op, ma, mb, mc = self.decode(instr)

        a,b,c = self._fetch_params(op)

        return (op, (a,b,c), (ma, mb, mc))

    def _fetch_params(self, op):
        a = self.mem.get(self.ip, 0)
        self.ip += 1
        b = 0
        c = 0
        if op in [1, 2, 7, 8]:
            # fetch 2 extra, because opcodes 1 and 2 have 3 parameters
            b = self.mem.get(self.ip, 0)
            self.ip += 1
            c = self.mem.get(self.ip, 0)
            self.ip += 1
        elif op in [5, 6]:
            b = self.mem.get(self.ip, 0)
            self.ip += 1
        return (a, b, c)
    
    def _fetch_value(self, v, mode):
        if mode == 1:
            # immediate - mode 1
            return v
        if mode == 2:
            # relative mode
            self.log(' :: fetch relative: ', self.base, v, '(', self.base + v, ')')
            self.log(' ::  > ', self.mem.get(self.base + v, 0))
            return self.mem.get(self.base + v, 0)
        # mode 0 - positional
        return self.mem.get(v, 0)


    def _store_value(self, addr, value, mode):
        if mode == 2:
            addr += self.base
        self.mem[addr] = value

    def decode(self, instr):
        op = instr%100
        instr //= 100
        a = instr%10
        instr //= 10
        b = instr%10
        instr //= 10
        c = instr%10
        instr //= 10

        return (op, a, b, c)
    
    def input(self):
        if self.inpq:
            return self.inpq.pop(0)
        raise Exception('Wants to read, but input queue is empty')

    def execute(self):
        while True:
            self.log('%s: '%self.ip, end='')
            op, values, modes = self.fetch()
            self.log(op, values, modes)
            if op == 1:
                # add
                a = self._fetch_value(values[0], modes[0])
                b = self._fetch_value(values[1], modes[1])
                c = values[2]

                self._store_value(c, a + b, modes[2])
            elif op == 2:
                # mul
                a = self._fetch_value(values[0], modes[0])
                b = self._fetch_value(values[1], modes[1])
                c = values[2]

                self._store_value(c, a * b, modes[2])
            elif op == 3:
                # read
                v = self.input()
                addr = values[0]
                if modes[0] == 2:
                    addr += self.base
                self.mem[addr] = v

            elif op == 4:
                # output
                v = self._fetch_value(values[0], modes[0])
                self.out = v
                print('OUT: ', v)
            elif op == 5:
                # jump-if-true
                a = self._fetch_value(values[0], modes[0])
                b = self._fetch_value(values[1], modes[1])
                if a:
                    if b < 0:
                        raise Exception('set IP to bellow zero', a, b)
                    self.ip = b
            elif op == 6:
                # jump-if-false
                a = self._fetch_value(values[0], modes[0])
                b = self._fetch_value(values[1], modes[1])
                if a == 0:
                    if b < 0:
                        raise Exception('set IP to bellow zero', a, b)
                    self.ip = b
            elif op == 7:
                # less than
                a = self._fetch_value(values[0], modes[0])
                b = self._fetch_value(values[1], modes[1])
                c = values[2]
                if a < b:
                    self._store_value(c, 1, modes[2])
                else:
                    self._store_value(c, 0, modes[2])
            elif op == 8:
                # equals
                a = self._fetch_value(values[0], modes[0])
                b = self._fetch_value(values[1], modes[1])
                c = values[2]
                if a == b:
                    self._store_value(c, 1, modes[2])
                else:
                    self._store_value(c, 0, modes[2])
            elif op == 9:
                a = self._fetch_value(values[0], modes[0])
                self.log('Set base: ', self.base, a, ' to ', self.base + a)
                self.base += a
            elif op == 99:
                print('HALT')
                return
            else:
                raise Exception('Invalid opcode: ', op, values, modes)


def load_program(inpf):
    with open(inpf) as f:
        instructions = [int(i.strip()) for i in f.read().split(',')]
        mem = {}
        for i in range(0, len(instructions)):
            mem[i] = instructions[i]
        return mem

def part1():
    print('Part 1:')
    comp = ICC(load_program('input'), [1])
    comp.verbose = False
    comp.execute()
    return comp.out


def part2():
    print('Part 2: ')
    comp = ICC(load_program('input'), [2])
    comp.verbose = False
    comp.execute()
    return comp.out

part1()
part2()