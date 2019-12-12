from queue import Queue

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


variables = 'abcnmpqrstij'


class _varnames:

    def __init__(self):
        self.used = {}
        self.idx = 0
    
    def get_name(self):
        n = variables[self.idx]
        c = self.used.get(n, 0)
        self.used[n] = c + 1
        if c:
            n = n + str(c)
        self.idx = (self.idx + 1) % len(variables)
        return n
    


class Disassembler:
    
    def __init__(self, mem, as_hex=False, num_padding=4, inv_as_data=True, show_comments=True):
        self.mem = mem
        self.varnames = _varnames()
        self.variables = {}
        self.as_hex = as_hex
        self.num_padding = num_padding
        self.inv_as_data = inv_as_data
        self.show_comments = show_comments

    def _format_number(self, v, padding=True):
        fmt = '{:%dd}' % self.num_padding if padding else '{:d}'
        if self.as_hex:
            fmt = '{:0%dX}' % self.num_padding if padding else '{:X}'
        return fmt.format(v)

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
    
    def _disassemble_param(self, param, mode):
        if mode == 0:
            # positional - indirect, possibly a variable
            if param < 0:
                return ('[{}]'.format(self._format_number(param, padding=False)), None, 0)
            var_name = self.variables.get(param)
            addr = self._format_number(param, padding=False)
            if var_name is None:
                # no such variable, create new
                var_name = self.varnames.get_name()
                self.variables[param] = var_name
            return (var_name, '{}@{}'.format(var_name, addr), self.mem.get(param, 0))
        elif mode == 1:
            # immediate value
            return (self._format_number(param), None, param)
        elif mode == 2:
            # Stack pointer
            if param:
                return ('[SP{}{}]'.format(
                    '+' if param > 0 else '',
                    self._format_number(param).strip()
                ), None, str(param))
            else:
                return ('[SP]', None, 'SP')
            return ('[SP + %d]'%param, None, str(param))
        else:
            return (self._format_number(param), 'Invalid parameter mode', 0)

    def _disassemble_at(self, ip, dump_vars=False):
        instr = self.mem.get(ip, 0)
        if instr == 0:
            if self.inv_as_data:
                return (self._format_number(instr) + '  ; data', 0, {})
            return ('[N/A] OP is zero (?)', 0, {})
        op, ma, mb, mc = self._decode_instr(instr)
        isdef = inst_set.get(op)
        if not isdef:
            if self.inv_as_data:
                return (self._format_number(op) + '  ; data', 0, {})
            return ('[N/A] Invalid OP: {}'.format(self._format_number(op)), 0, {})
        modes = [ma, mb, mc]
        params = []
        comment = []
        values = {}
        for i in range(0, isdef['params']):
            param = self.mem.get(ip + i + 1)
            param, comm, value = self._disassemble_param(param, modes[i])
            if comm:
                comment.append(comm)
            params.append(param)
            values[param] = value
        

        mnemonic = isdef['mnem']
        params_part = ', '.join(['{:>4}'.format(p) for p in params])
        comments_part = ';  ' + ', '.join(comment) if comment else ''

        asm_instr = '{:6}{}'.format(mnemonic, params_part)
        if self.show_comments:
            asm_instr = '{:40}{}'.format(asm_instr, comments_part)

        return (asm_instr, isdef['params'], values)
    
    def disassemble(self, start, op_count=1, end=None):
        ip = start
        n = op_count or 0
        while n or op_count is None:
            disasm, pc, values = self._disassemble_at(ip)
            n -= 1
            yield (disasm, ip, values)
            ip += pc + 1
            if pc < 0:
                break
            if end is not None and ip >= end:
                break
    

    def disassemble_part(self, start, end, show_address=True):
        dump = []

        for asm, addr, values in self.disassemble(start=start, end=end):
            m = asm
            if show_address:
                m = '{}: {}'.format(self._format_number(addr), m)
            
            dump.append((m, values))
        return dump
    
    def dump_one(self, address):
        return self.disassemble_part(address, address+1)[0]

    def dump_mem(self):
        end = max([addr for addr in self.mem.keys()])
        print('End=', end)
        
        for line, address,_ in self.disassemble(start=0, op_count=None, end=end):
            yield '{}: {}'.format(self._format_number(address), line)



class ICC:

    def __init__(self, mem, inpq=None, outq=None):
        self.mem = mem
        self.ip = 0
        self.inpq = inpq or []
        self.verbose = False
        self.disasm = Disassembler(mem)
        self.base = 0
        self.out = outq
        self._commands = {}
        self.interactive = False
        self._register_commands()

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

    def _disasm_curr(self):
        decoded, values = self.disasm.dump_one(self.ip)
        decoded_values = []
        for k in sorted(values.keys()):
            v = values[k]
            if isinstance(v, str):
                if v == 'SP':
                    v = self.mem.get(self.base, 0)
                else:
                    v = self.mem.get(self.base + int(v), 0)
            decoded_values.append('{} is {}'.format(k,v))
        
        return '{}\n\t{}'.format(decoded, ', '.join(decoded_values))


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
        if isinstance(self.inpq, Queue):
            return self.inpq.get()
        elif callable(self.inpq):
            return self.inpq()
        if self.inpq:
            return self.inpq.pop(0)
        raise Exception('Wants to read, but input queue is empty')

    def execute(self):
        while True:
            self.log(self._disasm_curr())
            op, values, modes = self.fetch()
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
                if isinstance(self.out, Queue):
                    self.out.put(v)
                elif callable(self.out):
                    self.out(v)
                else:
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

            if self.interactive:
                self._trap()
    
    def add_command(self, name, handler, help=None):
        self._commands[name.lower()] = (handler, help)
    
    def _trap(self):
        while True:
            inp = input('icc>')
            inp = inp.strip()
            if not inp:
                return
            params = inp.split()
            cmd = params[0].lower()
            hnd = self._commands.get(cmd)
            if not hnd:
                print('> Invalid command.')
                continue
            try:
                cont = hnd[0](cmd, params[1:])
                if cont:
                    break
            except Exception as e:
                print('Error:', str(e))
    
    def _help(self, name, params):
        print('Available commands:')
        for cmd, hlp in sorted([(cmd, v[1]) for cmd, v in self._commands.items()]):
            print('\t%s - %s' % (cmd, hlp or cmd))
    
    def _dump(self, name, params):
        if params:
            start = int(params[0])
            count = None
            if len(params) > 1:
                count = int(params[1])
            for (line, addr) in self.disasm.disassemble(start, count):
                print('0x{:04X}: {}'.format(addr, line))
            
            return
        print('----- MEMORY DUMP -----')
        for line in self.disasm.dump_mem():
            print(line)
        print('-----------------------')
    
    def _inspect(self, cmd, params):
        if not params:
            print('Format: inspect <what>')
            return
        what = params[0]
        if hasattr(self, what):
            print(getattr(self, what))
        else:
            print('No such property:', what)
    
    def _set_input(self, cmd, params):
        if not params:
            print('Add an int value(s) to be added to the input queue')
            return
        
        params = [int(p) for p in params]
        self.inpq += params
    
    def _continue(self, *args):
        self.interactive = False
        return True

    def _register_commands(self):
        self.add_command('?', self._help, 'Prints help.')
        self.add_command('help', self._help, 'Prints help.')
        self.add_command('dump', self._dump, 'Dump part of or the whole memory.')
        self.add_command('i', self._inspect, 'Inspect a property. Example: i inpq')
        self.add_command('inspect', self._inspect, 'Inspect a property. Example: inspect inpq')
        self.add_command('put', self._set_input, 'Add one or more values (int) to the input queue.')
        self.add_command('cont', self._continue, 'Exit interactive mode and continue running.')


def load_program(inpf):
    with open(inpf) as f:
        instructions = [int(i.strip()) for i in f.read().split(',')]
        mem = {}
        for i in range(0, len(instructions)):
            mem[i] = instructions[i]
        return mem