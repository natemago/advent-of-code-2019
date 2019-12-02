def exec(program):
    pc = 0

    while True:
        if pc < 0 or pc >= len(program):
            print('PC outside range')
            break
        instr = program[pc]
        if instr == 99:
            print('Normal HALT')
            break
        a = program[pc + 1]
        b = program[pc + 2]
        dest = program[pc + 3]
        if instr == 1:
            program[dest] = program[a] + program[b]
        elif instr == 2:
            program[dest] = program[a] * program[b]
        else:
            raise Exception('Invalid instruction ', instr, ' at postition: ', pc)
        
        pc += 4


def load_prog(inpf):
    with open(inpf) as f:
        return [int(p.strip()) for p in f.read().strip().split(',')]


def test_exec(prg):
    exec(prg)
    print(prg)


def part1():
    program = load_prog('input')
    program[1] = 12
    program[2] = 2
    exec(program)
    return program[0]


def part2():
    program = load_prog('input')

    for noun in range(0, 100):
        for verb in range(0, 100):
            p = [k for k in program]
            p[1] = noun
            p[2] = verb
            exec(p)
            if p[0] == 19690720:
                return noun * 100 + verb
    raise Exception('None found?')


#test_exec([1,9,10,3,2,3,11,0,99,30,40,50])
print('Part 1: ', part1())
print('Part 2: ', part2())