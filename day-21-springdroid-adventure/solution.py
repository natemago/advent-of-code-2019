import sys

sys.path.append('..')

from tools.intcomp import ICC, load_program


def _print(v):
    if v < 256:
        print(chr(v), end='')
    else:
        print('NON ASCII:', v)

def _write_buff(s):
    buff = [ord(c) for c in s]
    d= {'i':  0}
    def _next():
        if d['i'] >= len(buff):
            raise Exception('Buffer empty')
        c = buff[d['i']]
        d['i'] += 1
        return c
    
    return _next

def part1(inpf):
    '''
    0000 - DEAD
    0001 - JUMP
    0010 - STAY
    0011 - JUMP
    0100 - STAY
    0101 - JUMP
    0110 - STAY
    0111 - JUMP
    1000 - DEAD
    1001 - JUMP
    1010 - STAY
    1011 - JUMP
    1100 - STAY
    1101 - JUMP
    1110 - STAY
    1111 - STAY

    0000 - DEAD


    0001 - JUMP
    0011 - JUMP
    0101 - JUMP
    0111 - JUMP
    1001 - JUMP
    1011 - JUMP
    1101 - JUMP

    '''
    prog = [
        'NOT A T',
        'OR  T J',
        'NOT  B T',
        'OR T J',
        'NOT C T',
        'OR T J',
        'AND D J',
        'WALK'
    ]
    prog = '\n'.join(prog) + '\n'
    comp = ICC(load_program(inpf), inpq=_write_buff(prog), outq=_print, quiet=True)
    comp.execute()

def part2(inpf):
    '''
    @ABCDEFGHI
    #   #   #
  #####.#.#.#...###
    #####.#.#.#...###
    #####.#.#.#...###
     ???#--- -


    r or (not b and not e)
    '''
    prog = [
        'NOT A T',
        'NOT B J',
        'OR T J',
        'NOT C T',
        'OR T J',
        'AND D J',
        'NOT E T',
        'AND H T',
        'OR E T',
        'AND T J',
        'RUN'
    ]
    prog = '\n'.join(prog) + '\n'
    comp = ICC(load_program(inpf), inpq=_write_buff(prog), outq=_print, quiet=True)
    comp.execute()
    

part1('input')
part2('input')