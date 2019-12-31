def load_input(prog_file):
    prog = []
    with open(prog_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith('cut '):
                prog.append(('cut', int(line[len('cut '):].strip())))
            elif line.startswith('deal with increment '):
                prog.append(('incr', int(line[len('deal with increment ')-1:].strip())))
            else:
                prog.append(('rev', None))
    return prog


def deal_into_new_stack(i, deck_size):
    return deck_size - i - 1

def cut_n_cards(i, n, deck_size):
    if n == 0:
        return i
    if n > 0:
        if i < n:
            return (deck_size - n) + i
        else:
            return i - n
    else:
        if i >= (deck_size + n):
            return i - (deck_size + n)
        else:
            return i - n

def deal_with_increment(i, n, deck_size):
    return (i*n) % deck_size


def execute_proc(prog, i, deck_size):
    for task, n in prog:
        if task == 'rev':
            i = deal_into_new_stack(i, deck_size)
        elif task == 'cut':
            i = cut_n_cards(i, n, deck_size)
        else:
            i = deal_with_increment(i, n, deck_size)
    return i


def part1(prog_file, deck_size):
    program = load_input(prog_file)
    return execute_proc(program, 2019, 10007)

print('Part 1:', part1('input', 10007))

### Part 2 - Take 2

def mmi(n,m):
    '''
    Modular multiplicative index of n (mod m).
    Turns out is easy in python when m is prime
    '''
    return pow(n, m-2, m)

def lineq(x1,c1, x2, c2, m):
    '''
    Solve linear system of 2 modular equations mod m for x1,x2
    a*x1 + b = c1
    a*x2 + b = c2
    ===============
    a*x1-a*x2 = c1-c2
    a(x1 - x2) = (c1-c2)
    a = (c1-c2)*mmi(x1-x2)

    then for b:
    b = c1 - a*x1 (mod m)
    '''
    a = (c1 - c2) * mmi(x1 - x2, m)
    a = a % m
    b = c1 - a*x1
    b = b%m
    return (a,b)

def part2_t2(progf):
    '''
    Turns out the whole problem is linear modular equation of the type:
    f(x) = a*x + b (mod M)

    I've tried multiple times to get a and b, but it didn't pan out.
    Another approach is needed.

    Let's suppose we know the end values where a card will end up for 2 different
    cards (let's say card 3 and 7):
    f(3) = c1, and
    f(7) = c2

    then we can solve system of two linear modular equations to get a and b:
    a*3 + b = c1 (mod M)
    a*7 + b = c2 (mod M)

    Using this, we can then solve part 2 with some more (modular) algebra.
    '''
    program = load_input(progf)
    M = 119315717514047
    N = 101741582076661
    x1, x2 = 3, 7
    c1 = execute_proc(program, x1, M)
    c2 = execute_proc(program, x2, M)
    a,b = lineq(x1, c1, x2, c2, M)
    '''
    Now we know the general equation of the problem for 1 iteration:
    f(x) = a*x + b

    Given we have the function to calculate the next iteration:
    X0 = f(x) = a*x + b

    Calculating the next iteration is basically applying the same function again:
    X1 = f(X0) = f(f(x))

    Then XN would be:
    XN = f(f(f( ... N times f(X0)))), which is:
    XN = f<N>(x) = a**n * x + b * ((a**n - 1)//(a - 1))

    So the general form of this function is:
    g(x) = f<N>(x) = A*x + B (mod M)
    where:
    A = a**n
    B = b*(a**n - 1)*mmi(a-1)
    '''
    A = pow(a, N, M)
    B = (b*(pow(a, N, M) - 1) * mmi(a-1, M))  % M

    '''
    Now we have the following:
    Ax + B = 2020 (mod M)
    we need to solve for x:
    x = (2020 - B)*mmi(A, M) (mod M)
    '''
    x = (((2020 - B)%M) * mmi(A, M)) % M
    print('Part 2: ', x)

print('Part 2, take 2')
part2_t2('input')