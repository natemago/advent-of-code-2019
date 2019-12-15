from math import ceil
from queue import Queue


class Substance:

    def __init__(self, name, units=1):
        self.name = name
        self.composition = []
        self.units = units
    
    def add_ingredient(self, substance, units):
        self.composition.append((substance, units))

    

class SubstanceTree:

    def __init__(self):
        self.nodes = {}
    
    def add_node(self, substance):
        sub = Substance(substance)
        if self.nodes.get(substance):
            raise Exception('Two reactions for the same product: ' + substance)
        self.nodes[substance] = sub
    
    def add_composition(self, substance, sunits, composition):
        sub = self.nodes.get(substance)
        sub.units = sunits
        if not sub:
            raise Exception('Substance {} is not known'.format(substance))
        
        for units, subs_name in composition:
            ingr = self.nodes.get(subs_name)
            if not ingr:
                raise Exception('Unknown ingredient: ' + subs_name)
            sub.add_ingredient(ingr, units)
    
    def build_tree(self, ingredients):

        self.add_node('ORE')  # We always have ORE

        for _, product in ingredients:
            self.add_node(product[1])
        
        for composition, product in ingredients:
            self.add_composition(product[1], product[0], composition)
    
    def calculate_ore_for_fuel(self, fuel=1):
        q = Queue()

        q.put((self.nodes['FUEL'], fuel))

        produced = {}
        extra = {}

        while not q.empty():
            substance, quantity = q.get()
            batch_size = substance.units
            quantity = int(quantity)

            extra_produced = extra.get(substance.name, 0)
            quantity -= extra_produced

            orig_quantity = quantity
            if quantity % batch_size:
                # must produce full batches only
                quantity = ((quantity//batch_size) + 1) * batch_size
            
            batches = quantity//batch_size

            total = batches*batch_size
            extra[substance.name] = total - orig_quantity
            produced[substance.name] = produced.get(substance.name, 0) + (total - extra_produced)

            for ingr, units in substance.composition:
                q.put((ingr, batches*units))

        return produced['ORE']

def load_ingredients(inf):
    ingredients = []

    with open(inf) as f:
        for line in f:
            line = line.strip().split('=>')
            composition = []
            product = line[1].strip().split()
            product = (int(product[0].strip()), product[1].strip())

            for comp in line[0].strip().split(','):
                comp = comp.split()
                composition.append((int(comp[0].strip()), comp[1].strip()))
            
            ingredients.append((composition, product))

    return ingredients


def part1():
    tree = SubstanceTree()
    tree.build_tree(load_ingredients('input'))

    return tree.calculate_ore_for_fuel()


def part2():
    # binary search
    tree = SubstanceTree()
    tree.build_tree(load_ingredients('input'))

    s = 1
    e = 1000000000000
    RES = 1000000000000

    while True:
        mid = (s+e)//2
        ore = tree.calculate_ore_for_fuel(mid)
        if ore == RES:
            return mid
        if e-s == 1:
            if ore < RES and tree.calculate_ore_for_fuel(e) >= RES:
                return mid
            raise Exception('Invalid bounds')
        elif ore < RES:
            s = mid
        else:
            e = mid

print('Part 1: ', part1())
print('Part 2: ', part2())