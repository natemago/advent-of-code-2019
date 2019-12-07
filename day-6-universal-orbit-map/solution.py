class Node:

    def __init__(self, name, data=None):
        self.data = data or {}
        self.name = name
        self.children = []
    
    def add_child(self, node):
        self.children.append(node)
        if node.data.get('parent'):
            print(node.name, ' already orbits ', node.data('parent').name)
        node.data['parent'] = self
    
    def update_depth(self):
        parent = self.data.get('parent')
        if not parent:
            self.data['depth'] = 0
        else:
            self.data['depth'] = parent.data['depth'] + 1
        
        for child in self.children:
            child.update_depth()

    def get_path_from_root(self):
        path = []

        node = self
        while node:
            path.append(node.name)
            node = node.data.get('parent')

        return [k for k in reversed(path)]


class UniversalOrbitMap:

    def __init__(self):
        self.nodes = {}
        self.com = None
    
    def _get_node(self, name):
        node = self.nodes.get(name)
        if not node:
            node = Node(name)
            self.nodes[name] = node
        return node

    def orbit(self, com, obj):
        # object orbits com
        com_node = self._get_node(com)
        obj_node = self._get_node(obj)

        com_node.add_child(obj_node)
    
    def calculate_com(self):
        for _, node in self.nodes.items():
            if node.data.get('parent') is None:
                if self.com:
                    raise Exception('Found more than one COM. First is ' + self.com.name + ' but found other: ' + node.name)
                self.com = node
        if not self.com:
            raise Exception('No COM found. Circular graph!')
        
        return self.com
    
    def orbit_count_checksums(self):
        self.com.update_depth()
        total_orbits = 0
        for _, node in self.nodes.items():
            total_orbits += node.data.get('depth', 0)
        return total_orbits
    

    def calculate_orbital_transfers(self):
        you = self.nodes['YOU']
        santa = self.nodes['SAN']
        path_you = you.get_path_from_root()
        path_santa = santa.get_path_from_root()

        # find where paths diverge
        while True:
            if path_you[0] != path_santa[0]:
                break
            path_you = path_you[1:]
            path_santa = path_santa[1:]
        
        return len(path_you) + len(path_santa) - 2



def load_input(file_name):
    orbits = []

    with open(file_name) as inpf:
        for line in inpf:
            line = line.strip()
            if line:
                orbits.append(line.split(')'))

    return orbits


uom = UniversalOrbitMap()

for orbits in load_input('input'):
    uom.orbit(orbits[0], orbits[1])

print('COM: ', uom.calculate_com().name)
print('Part 1: ', uom.orbit_count_checksums())
print('Part 2: ', uom.calculate_orbital_transfers())