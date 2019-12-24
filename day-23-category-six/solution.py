import sys
sys.path.append('..')

from tools.intcomp import ICC, load_program


def new_computer(prog_file, inq, outq):
    comp = ICC(load_program(prog_file), inpq=inq, outq=outq, quiet=True)
    #comp.verbose = True
    return comp

class Cluster:

    def __init__(self, prog_file, on_send_packet=None, on_all_idle=None):
        self.buffers = {}
        self.tmp_buffers = {}
        self.computers = []
        self.prog_file = prog_file
        self.on_send_packet = on_send_packet
        self.on_all_idle = on_all_idle
        self.idle = []
        self._idle_count = 100

    def init_cluster(self, size=50):
        for i in range(0, 50):
            self.buffers[i] = [i]
            self.computers.append(new_computer(self.prog_file, self.on_input(i), self.on_output(i)))
            self.idle.append(self._idle_count)

    
    def on_input(self, address):
        def _on_input():
            buff = self.buffers.get(address)
            if not buff:
                self.idle[address] -= 1
                if self.idle[address] < 0:
                    self.idle[address] = 0
                if sum(self.idle) == 0:
                    if self.on_all_idle:
                        self.on_all_idle()
                return -1
            v = buff[0]
            self.buffers[address] = buff[1:]
            return v
        return _on_input
    
    def on_output(self, address):
        def _on_output(v):
            self.idle[address] = self._idle_count
            buff = self.tmp_buffers.get(address)
            
            if buff is None:
                buff = []
                self.tmp_buffers[address] = buff
            
            buff.append(v)
            
            if len(buff) == 3:
                if buff[0] != 255:
                    if not self.buffers.get(buff[0]):
                        self.buffers[buff[0]] = []
                    self.buffers[buff[0]] += buff[1:]
                self.tmp_buffers[address] = []
                if self.on_send_packet:
                    self.on_send_packet(buff[0], buff[1], buff[2])
        return _on_output
    
    def run_all_seq(self):
        self._running = True
        while self._running:
            for c in self.computers:
                c.step()
    
    def stop_all_seq(self):
        self._running = False
    
    def are_all_idle(self):
        if len(self.buffers) >= 50:
            for _, buff in self.buffers.items():
                if buff:
                    return False
            return True
        return False


def part1(prog_file):
    def _on_send_packet(address, x, y):
        #print('SND: ', address, x, y)
        if address == 255:
            cluster.stop_all_seq()
            print('Part 1:', y)

    cluster = Cluster(prog_file, _on_send_packet)
    cluster.init_cluster(50)
    print(cluster.buffers)
    cluster.run_all_seq()


def part2(prog_file):
    SKIP = 1000 
    nat = {'skip': SKIP, 'prev_sent': None}

    def check_for_idle():
        if nat.get('last'):
            if nat.get('skip'):
                nat['skip'] -= 1
                return
            nat['skip'] = SKIP
            x,y = nat['last']
            cluster.buffers[0] = [x,y]
            #print('NAT -> 0', (x,y))
            if nat.get('prev_sent') is None:
                nat['prev_sent'] = (x,y)
            elif nat['prev_sent'] == (x,y):
                cluster.stop_all_seq()
                print('Part 2:', y)
                return
            nat['prev_sent'] = (x,y)

    def _on_send_packet(address, x, y):
        #print(address, '<-', x, y)
        if address == 255:
            nat['last'] = (x,y)

    cluster = Cluster(prog_file, _on_send_packet, check_for_idle)
    cluster.init_cluster(50)
    cluster.run_all_seq()

part1('input')
part2('input')