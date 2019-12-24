
def deal_into_new_stack(deck,*args):
    return [v for v in reversed(deck)]


def cut_n_cards(deck, n):
    #print(' .. cut', n)
    #print(deck)
    deck = deck[n:] + deck[0:n]
    #print(deck)
    return deck


def deal_with_increment(deck, n):
    #print(' .. incr', n)
    #print(deck)
    nd = [0 for i in deck]
    for i in range(0, len(deck)):
        nd[(i*n)%len(deck)] = deck[i]
        #print(nd)
    return nd


def load_input(prog_file):
    prog = []
    with open(prog_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith('cut '):
                prog.append((line, cut_n_cards, int(line[len('cut '):].strip())))
            elif line.startswith('deal with increment '):
                prog.append((line, deal_with_increment, int(line[len('deal with increment ')-1:].strip())))
            else:
                prog.append((line, deal_into_new_stack, None))
    return prog


def part1(prog_file, deck_size):
    program = load_input(prog_file)
    deck = [i for i in range(0, deck_size)]

    for line, task, args in program:
        print(line)
        args = [args]
        deck = task(deck, *args)
    print(deck)
    return deck.index(2019)

#print(deal_with_increment([i for i in range(0, 10)], 7))

#print('Test:', part1('test_input', 10))
print('Part 1:', part1('input', 10007))