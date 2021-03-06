import random
from experimental.classes.Miner import Miner
from experimental.classes.Block import Block


class Default:

    def __init__(self, n_node, iteration, waiting=0):
        self.n_node = n_node
        self.i_node = n_node

        self.energy_cost = 1
        self.budget = int(iteration / 2)
        self.behaviour = 0

        self.global_iteration = iteration
        self.current_iteration = iteration

        self.global_wait = waiting
        self.current_wait = waiting

        self.miners = {}
        self.genesys_block = Block(None, 0)

    def _init_miners(self):
        probs = list(map(lambda x: random.random(), range(self.n_node)))
        tot = sum(probs)
        probs = list(map(lambda x: x/tot, probs))

        self.miners[0] = Miner(0, [0, probs[0]], self.energy_cost, self.budget, self.behaviour, self.genesys_block)

        for i in range(1, len(probs)):
            old_val = self.miners[i - 1].get_hashrate()[1]
            new_val = old_val + probs[i]
            self.miners[i] = Miner(i, [old_val, new_val], self.energy_cost, self.budget, self.behaviour, self.genesys_block)

        return self.miners

    def get_setting(self):
        return self._init_miners()

    def get_max_budget(self):
        return self.global_iteration

    def miner_dead(self, miner, time):
        del self.miners[miner.getId()]
        self.miners[self.i_node] = Miner(self.i_node, miner.get_hashrate(), self.energy_cost, self.budget, self.behaviour, self.genesys_block)
        self.i_node += 1
        return [self.miners[self.i_node-1]]

    def is_time_to_mine(self, blocks):
        self.current_wait -= 1

        if self.current_iteration > 0 and self.current_wait < 0:
            self.current_iteration -= 1
            self.current_wait = self.global_wait
            return True

        return False

    def is_time_to_stop(self, blocks):
        return not (self.current_iteration > 0 or len(blocks) > 0)


