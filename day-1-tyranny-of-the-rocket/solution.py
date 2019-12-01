def part1(numbers):
    return sum([n//3-2 for n in numbers])


def module_fuel(m):
    fuel = 0
    while True:
        mf = m//3 - 2
        if mf <= 0:
            break
        m = mf
        fuel += m
    return fuel

def part2(numbers):
    return sum([module_fuel(n) for n in numbers])


numbers = []
with open('input') as f:
    for line in f:
        line = line.strip()
        if line:
            numbers.append(int(line.strip()))

print('Part 1: ', part1(numbers))
print('Part 2: ', part2(numbers))