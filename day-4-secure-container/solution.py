def is_valid(password):
    if password < 100000:
        return False
    p = password % 10
    password //= 10
    two_same = False
    while password:
        c = password % 10
        if p < c:
            return False
        if p == c:
            two_same = True
        password //= 10
        p = c

    return two_same

def is_valid_part_2(password):
    if password < 100000:
        return False
    
    groups = []
    while password:
        c = password % 10
        i = 1
        password //= 10
        while password:
            n = password % 10
            if c != n:
                groups.append((c, i))
                break
            password //= 10
            i += 1
        if not password:
            groups.append((c, i))
    if not groups:
        return True

    p, _ = groups[0]
    for c, _ in groups[1:]:
        if c > p:
            return False
        p = c
    
    for _, i in groups:
        if i == 2:
            return True
    

    return False


def passwords(a, b, is_valid):
    count = 0
    while a <= b:
        if is_valid(a):
            count += 1
        a += 1
    return count

print(is_valid(111111))
print(is_valid(223450))
print(is_valid(123789))

print('Part 1: ', passwords(353096, 843212, is_valid))
print('Part 2: ', passwords(353096, 843212, is_valid_part_2))