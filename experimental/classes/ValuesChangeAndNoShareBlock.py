import random
from experimental.classes.Miner import Miner
from experimental.classes.Block import Block


class ValuesChangeAndNoShareBlock:

    def __init__(self, n_node, iteration, energy_cost=None):
        self.n_node = n_node
        self.i_node = n_node

        self.energy_cost = energy_cost

        self.global_iteration = iteration
        self.current_iteration = iteration
        self.budget = int(iteration / 2)

        self.behaviour = 0
        self.miners = {}
        self.genesys_block = Block(None, 0)

    def _init_miners(self):
        probs = list(map(lambda x: random.random(), range(self.n_node)))
        tot = sum(probs)
        probs = list(map(lambda x: x / tot, probs))

        new_energy_cost = random.random() if self.energy_cost is None else self.energy_cost
        behaviour = [random.random(), random.random(), random.random(), random.random()]

        self.miners[0] = Miner(0, [0, probs[0]], new_energy_cost, self.budget, behaviour, self.genesys_block, 0)

        for i in range(1, len(probs)):
            old_val = self.miners[i - 1].get_hashrate()[1]
            new_val = old_val + probs[i]
            new_energy_cost = random.random() if self.energy_cost is None else self.energy_cost
            behaviour = [random.random(), random.random(), random.random(), random.random()]

            self.miners[i] = Miner(i, [old_val, new_val], new_energy_cost, self.budget, behaviour, self.genesys_block, 0)

        return self.miners

    def get_setting(self):
        return self._init_miners()

    def get_max_budget(self):
        return self.global_iteration

    def miner_dead(self, miner, time):
        del self.miners[miner.getId()]

        self.miners[self.i_node] = Miner(self.i_node, miner.get_hashrate(), miner.get_energy_cost(), self.budget, miner.get_behaviour(), self.genesys_block, time_created=time)

        miner_max_budget = self.miners[self.i_node]
        for i in self.miners:
            current_miner = self.miners[i]
            if current_miner.get_budget() > miner_max_budget.get_budget():
                miner_max_budget = current_miner

        perc0 = miner_max_budget.get_behaviour()[0] / 10
        perc1 = miner_max_budget.get_behaviour()[1] / 10
        perc2 = miner_max_budget.get_behaviour()[2] / 10
        perc3 = miner_max_budget.get_behaviour()[3] / 10

        perc0 = perc0 if miner.get_behaviour()[0] - miner_max_budget.get_behaviour()[0] > 0 else perc0*(-1)
        perc1 = perc1 if miner.get_behaviour()[1] - miner_max_budget.get_behaviour()[1] > 0 else perc1*(-1)
        perc2 = perc2 if miner.get_behaviour()[2] - miner_max_budget.get_behaviour()[2] > 0 else perc2*(-1)
        perc3 = perc3 if miner.get_behaviour()[3] - miner_max_budget.get_behaviour()[3] > 0 else perc3*(-1)

        behaviour = [miner.get_behaviour()[0]-perc0, miner.get_behaviour()[1]-perc1, miner.get_behaviour()[2]-perc2, miner.get_behaviour()[3]-perc3]
        self.miners[self.i_node].set_behaviour(behaviour)

        self.i_node += 1
        return [self.miners[self.i_node-1]]

    def is_time_to_mine(self, blocks):

        if self.current_iteration > 0 and len(blocks) == 0:
            self.current_iteration -= 1
            return True

        return False

    def is_time_to_stop(self, blocks):
        return not (self.current_iteration > 0 or len(blocks))


