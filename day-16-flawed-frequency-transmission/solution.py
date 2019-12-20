def load_input(inpf):
    with open(inpf) as f:
        return [int(c) for c in f.read().strip()]


def print_pattern(seq, offset, pos, neg):
    out = ['0' for _ in seq]

    for i in pos:
        idx = (i + 1) * offset
        end = idx + offset + 1
        

def phase_digit(seq, s, offset, pos, neg):
    #p = ['0' for _ in seq]
    for k in range(0,len(pos)):
        i, out = pos[k]
        idx = i*(offset+1) + offset
        out = out or False
        if idx >= len(seq):
            if out:
                pos.pop()
                break
            pos[k] = (i, True)
            out = True
        pi = i*offset + offset - 1

        if offset == 0:
            #p[idx] = '+'
            s += seq[idx]
            continue

        #print(idx, pi, offset, ',  ', end='')
        if out:
            # remove the previous ones
            for j in range(pi, min(pi + offset, len(seq))):
                #p[j] = '/'
                s -= seq[j]
        else:
            for j in range(pi, min(pi + offset, idx)):
                #p[j] = '-' if p[j] == '0' else '_'
                s -= seq[j]

            for j in range(max(pi + offset, idx), min(idx + offset + 1, len(seq))):
                #p[j] = '+'
                s += seq[j]
    
    for k in range(0,len(neg)):
        i, out = neg[k]
        idx = i*(offset+1) + offset
        out = out or False
        if idx >= len(seq):
            if out:
                neg.pop()
                break
            neg[k] = (i, True)
            out = True
        pi = i*offset + offset - 1

        if offset == 0:
            #p[idx] = '+'
            s -= seq[idx]
            continue

        #print(idx, pi, offset, ',  ', end='')
        if out:
            # remove the previous ones
            for j in range(pi, min(pi + offset, len(seq))):
                #p[j] = '/'
                s += seq[j]
        else:
            for j in range(pi, min(pi + offset, idx)):
                #p[j] = '-' if p[j] == '0' else '_'
                s += seq[j]

            for j in range(max(pi + offset, idx), min(idx + offset + 1, len(seq))):
                #p[j] = '+'
                s -= seq[j]
            
    #print()
    #print(' '.join(['{:2}'.format(c) for c in p]))
    return s

def phase(seq):
    pos = [(i, False) for i in range(0, len(seq), 4)]
    neg = [(i, False) for i in range(2, len(seq), 4)]

    nseq = []
    s = 0
    for i in range(0, len(seq)):
        s = phase_digit(seq, s, i, pos, neg)
        nseq.append(abs(s) % 10)
        print('  @', i)
    
    return nseq


def calculate_phases(seq, count):
    s = seq
    for i in range(0, count):
        s = phase(s)
        print('Phase', i+1, 'complete.')
    return s


def hack(seq, offset):
    seq = seq[offset:]
    

    ns = seq
    for phase in range(0, 100):
        print('Calculating phase: ', phase+1)
        s = 0
        ts = []
        for i in range(0, len(seq)):
            s += ns[- i - 1]
            ns[-i-1] = s % 10
        
    return ns

def part2(inpf):
    seq = load_input(inpf)
    seq = seq*10000
    print('Input generated...')
    offset = int(''.join([str(seq[i]) for i in range(0, 7)]))
    print('Offset is: ', offset)

    if offset >= len(seq) // 2:
        print('Do the hack.')
        return hack(seq, offset)[0: 8]

    seq = calculate_phases(seq, 100)

    return ''.join([str(c) for c in seq[offset: offset+8]])


print('Part 1: ', calculate_phases(load_input('input'), 100)[0:8])
print('Part 2: ', part2('input'))