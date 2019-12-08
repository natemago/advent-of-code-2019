def load_data(file_name):
    with open(file_name) as f:
        return [int(d) for d in f.read().strip()]

def read_layer(pos, w, h, data):
    return data[pos: pos + w*h]


def read_layers(data, w, h):
    pos = 0
    layers = []

    while pos < len(data):
        layers.append(read_layer(pos, w, h, data))
        pos += w*h

    return layers

def count(d, layer):
    i = 0
    for pixel in layer:
        if pixel == d:
            i += 1
    return i

def print_layer(layer, w, h):
    for i in range(0, h):
        for j in range(0, w):
            px = layer[i*w + j]
            if px == 0 or px == 2:
                print(' ', end='')
            else:
                print('#', end='')
        print()


def stack_layer(base, top, w, h):
    stacked = []
    for i in range(0, h):
        for j in range(0, w):
            p = i*w+j
            tp = top[p]
            if tp == 2:
                stacked.append(base[p])
            else:
                stacked.append(top[p])
    return stacked


def part1():
    data = load_data('input')
    layers = read_layers(data, 25, 6)
    print(len(layers), 'layers.')
    fzl = min(layers, key=lambda layer: count(0, layer))
    print_layer(fzl, 25, 6)

    return count(1, fzl) * count(2, fzl)


def part2():
    layers = read_layers(load_data('input'), 25, 6)
    layers = [l for l in reversed(layers)]

    base = layers[0] # base
    for layer in layers[1:]:
        base = stack_layer(base, layer, 25, 6)
    
    print_layer(base, 25, 6)


print('Part 1: ', part1())
print('Part 2: ', part2())