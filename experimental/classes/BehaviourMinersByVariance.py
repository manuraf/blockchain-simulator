import random
import numpy as np
from experimental.classes.Miner import Miner
from experimental.classes.Block import Block


class BehaviourMinersByVariance:

    def __init__(self, n_node, iteration, variance):
        self.n_node = n_node
        self.i_node = n_node
        self.variance = variance

        self.energy_cost = 1
        self.budget = int(iteration / 2)

        self.global_iteration = iteration
        self.current_iteration = iteration

        self.behaviour = 0
        self.miners = {}
        self.genesys_block = Block(None, 0)

    def _init_miners(self):

        probs = list(np.random.normal(100, self.variance, self.n_node))
        tot = sum(probs)
        probs = list(map(lambda x: x / tot, probs))

        comportamento = 0

        self.miners[0] = Miner(0, [0, probs[0]], self.energy_cost, self.budget, comportamento, self.genesys_block)

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

        if self.current_iteration > 0 and len(blocks) == 0:
            self.current_iteration -= 1
            return True

        return False

    def is_time_to_stop(self, blocks):
        return not (self.current_iteration > 0 or len(blocks))


