import random
from experimental.classes.Miner import Miner
from experimental.classes.Block import Block


class ValuesChangeLowHashrate:

    def __init__(self, n_node, iteration, energy_cost=None):
        self.n_node = n_node
        self.i_node = n_node

        self.energy_cost = energy_cost

        self.global_iteration = iteration
        self.current_iteration = iteration
        self.hashrate_left = 0

        self.behaviour = 0
        self.miners = {}
        self.genesys_block = Block(None, 0)

    def _init_miners(self):
        probs = list(map(lambda x: random.random(), range(self.n_node)))
        tot = sum(probs)
        probs = list(map(lambda x: x * 0.1 / tot, probs))

        new_budget = int(self.global_iteration * random.random())
        new_energy_cost = random.random() if self.energy_cost is None else self.energy_cost
        self.miners[0] = Miner(0, [0, probs[0]], new_energy_cost, new_budget, self.behaviour, self.genesys_block, 0)

        for i in range(1, len(probs)):
            old_val = self.miners[i - 1].get_hashrate()[1]
            new_val = old_val + probs[i]
            new_budget = int(self.global_iteration * random.random())
            new_energy_cost = random.random() if self.energy_cost is None else self.energy_cost
            self.miners[i] = Miner(i, [old_val, new_val], new_energy_cost, new_budget, self.behaviour, self.genesys_block, 0)

        return self.miners

    def get_setting(self):
        return self._init_miners()

    def get_max_budget(self):
        return self.global_iteration

    def miner_dead(self, miner, time):
        del self.miners[miner.getId()]
        old_range = miner.get_hashrate()[1] - miner.get_hashrate()[0]
        new_range = (old_range + self.hashrate_left) * random.random()
        new_miner_rate = [miner.get_hashrate()[0], miner.get_hashrate()[0]+new_range]
        new_budget = int(self.global_iteration * random.random())
        new_energy_cost = random.random() if self.energy_cost is None else self.energy_cost

        self.miners[self.i_node] = Miner(self.i_node, new_miner_rate, new_energy_cost, new_budget, self.behaviour, self.genesys_block, time_created=time)
        self.hashrate_left = old_range + self.hashrate_left - new_range

        # shift miners
        if new_range < old_range:
            offset = miner.get_hashrate()[1]-(miner.get_hashrate()[0]+new_range)
            for i in self.miners:
                current_miner = self.miners[i]
                if current_miner.get_hashrate()[0] > miner.get_hashrate()[0]:
                    new_rate = [current_miner.get_hashrate()[0]-offset, current_miner.get_hashrate()[1]-offset]
                    current_miner.set_hashrate(new_rate)
        else:
            offset =  miner.get_hashrate()[0] + new_range - miner.get_hashrate()[1]
            for i in self.miners:
                current_miner = self.miners[i]
                if current_miner.get_hashrate()[0] > miner.get_hashrate()[0]:
                    new_rate = [current_miner.get_hashrate()[0] + offset, current_miner.get_hashrate()[1] + offset]
                    current_miner.set_hashrate(new_rate)

        self.i_node += 1
        return [self.miners[self.i_node-1]]

    def is_time_to_mine(self, blocks):

        if self.current_iteration > 0 and len(blocks) == 0:
            self.current_iteration -= 1
            return True

        return False

    def is_time_to_stop(self, blocks):
        return not (self.current_iteration > 0 or len(blocks))


