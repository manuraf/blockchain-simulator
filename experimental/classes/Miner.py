from experimental.classes.Block import Block
from experimental.classes.Transaction import Transaction
from experimental.classes.Util import Util
import numpy as np


class Miner:
    def __init__(self, minerId, hashrate, costo_energia,budget,comportamento, genesys, time_created=0, mining_pool=None):
        self.minerId = minerId
        self.hashrate = hashrate
        self.energy_cost = costo_energia
        self.init_budget = budget
        self.budget = budget
        self.chainBudget = 0
        self.comportamento = comportamento
        self.main_chain = {0:genesys}
        self.secondary_chain = {}
        self.blocks_to_release_after = []
        self.orphans = []
        self.mining_pool=mining_pool
        self.time_created = time_created
        self.age = 0

    # one block if he is the miner of rate,
    # others blocks if he has wanted release after the block
    def mining(self, rate, time, reward, fee):
        self.budget -= self.energy_cost
        blocks_to_release = []

        # is miner of this block
        if self.hashrate[0] <= rate < self.hashrate[1]:

            # add block to the main chain and add miner's transaction
            mc_height = len(self.main_chain)
            block = Block(self.main_chain[mc_height-1], time)
            block.addTransaction(Transaction(fee, self.minerId, reward))

            self.main_chain[mc_height] = block

            if self.is_share_block():
                blocks_to_release.append(block)
            else:
                self.blocks_to_release_after.append(block)

        # release block mined before
        for item in list(self.blocks_to_release_after):
            if time > item.getTime():
                blocks_to_release.append(item)
                self.blocks_to_release_after.remove(item)

        return blocks_to_release

    def is_share_block(self):
        # return self.comportamento == 0

        values = [self.get_budget()*0.01,self.energy_cost,self.hashrate[1]-self.hashrate[0],1]
        sum = 0

        for i in range(0, len(values)):
            sum += self.comportamento[i] * values[i]

        return np.tanh(sum) > 0.5


    def add_block(self, block):
        # verify if parent is on top of the main chain
        if not Util.verify_belong_chain_and_add(self.main_chain, block):

            # if it's not, verify if secondary_chain exists
            if len(self.secondary_chain) > 0:

                # verify if parent is on top of the secondary chain
                if Util.verify_belong_chain_and_add(self.secondary_chain, block):

                    # if it's in secondary chain, check the height of the chains
                    # if secondary chain's height is higher than main chain's height
                    #   switch main and fork chain
                    if len(self.secondary_chain) > len(self.main_chain):
                        tmp_chain = self.secondary_chain
                        self.secondary_chain = self.main_chain
                        self.main_chain = tmp_chain

                else:
                    if block.getHeight() > len(self.main_chain)-1:
                        # block is an orphan and add it inside of list orphans
                        self.orphans.append(block)

            else:
                # if it's not check if there are some parent within the main chain
                # and building secondary chain
                new_secondary_chain = Util.build_secondary_chain(block, self.main_chain)

                if new_secondary_chain is not None:
                    self.secondary_chain = new_secondary_chain
                    self.secondary_chain[len(self.secondary_chain)] = block
                else:
                    if block.getHeight() > len(self.main_chain)-1:
                        # block is an orphan and add it inside of list orphans
                        self.orphans.append(block)

    def downloadBlockchain(self, neighbor):
        for key in neighbor.getMainChain():
            self.main_chain[key] = neighbor.getMainChain()[key]

    def resolve_orphans_block(self, neighbors):
        for orphaned in self.orphans:

            for neighbor in neighbors:
                right_chain = [orphaned]
                current_block = orphaned
                orphaned_resolved = False

                while True:
                    if current_block.getParent() is None: break
                    parent = neighbor.get_block_by_hash(current_block.getParent().getHash())
                    if parent is None: break

                    # check if it is a known block
                    if self.is_known_parent_and_switch_chains(parent, right_chain):
                        # i found the right chain, switch chains and remove orphaned block
                        orphaned_resolved = True
                        break
                    else:
                        right_chain.append(parent)
                        current_block = parent

                if orphaned_resolved: break

        self.orphans = []

    def is_known_parent_and_switch_chains(self, parent, right_chain):
        height = len(right_chain)
        # check main-chain
        height_founded = self._isWithinChain(self.main_chain, parent.getHash(), height)
        if height_founded > 0:
            # switch chains, orphaned to main and main to fork
            self.secondary_chain = self.main_chain
            self.main_chain = self._copyChain(self.secondary_chain, height_founded, right_chain)
            return True

        # check fork-chain
        height_founded = self._isWithinChain(self.secondary_chain, parent.getHash(), height)
        if height_founded > 0:
            # switch chains, orphaned to main and main to fork
            temp_chain = self.main_chain
            self.main_chain = self._copyChain(self.secondary_chain, height_founded, right_chain)
            self.secondary_chain = self.main_chain
            return True

        return False

    def _copyChain(self, chain, end, blocks_to_added):
        new_chain = {}

        for i in chain:
            if i > end: break
            new_chain[i] = chain[i]

        for block in blocks_to_added:
            end += 1
            new_chain[end] = block

        return new_chain

    def _isWithinChain(self, chain, hash_block, stopped):
        len_chain = len(chain)
        if len_chain == 0:
            return -1

        i = len_chain
        while i > 0 and i > len_chain-stopped-1:
            i -= 1
            block = chain[i]
            if block.getHash() == hash_block:
                return i
        return -1

    def getLastBlock(self):
        return self.main_chain[len(self.main_chain)-1]

    def get_block_by_hash(self, hash_block):
        len_main = len(self.main_chain)
        while len_main > 0:
            len_main -= 1
            block = self.main_chain[len_main]
            if block.getHash() == hash_block:
                return block

        len_fork = len(self.secondary_chain)
        while len_fork > 0:
            len_fork -= 1
            block = self.secondary_chain[len_fork]
            if block.getHash() == hash_block:
                return block

        return None

    def getId(self):
        return self.minerId

    def get_budget(self):
        return self.budget + self.get_chain_budget()

    def get_init_budget(self):
        return self.init_budget

    def get_chain_budget(self):
        budget = 0
        for i_block in self.main_chain:
            block = self.main_chain[i_block]
            for t in block.getTransactions():
                if t.getOutNode() == self.minerId:
                    budget += t.getOutAmount() + t.getFee()

                if t.getInNode() == self.minerId:
                    budget -= t.getOutAmount()

        return budget

    def addBudget(self, amount):
        self.budget += amount

    def get_energy_cost(self):
        return self.energy_cost

    def get_behaviour(self):
        return self.comportamento

    def set_behaviour(self, behaviour):
        self.comportamento = behaviour

    def get_power(self):
        return self.hashrate[1] - self.hashrate[0]

    def get_hashrate(self):
        return self.hashrate

    def set_hashrate(self, hashrate):
        self.hashrate = hashrate

    def set_age(self, age):
        self.age = age

    def get_age(self):
        self.age

    def getHeight(self):
        return len(self.main_chain)

    def getOrphaned(self):
        return self.orphans

    def getMainChain(self):
        return self.main_chain

    def get_time_created(self):
        return self.time_created

    def getStringOfBlockchains(self):

        string_mainchain = "Main Chain --> \n"

        for height in self.main_chain:
            string_mainchain += "[{}:{}] \n".format(height,self.main_chain[height].getHash())

        if len(self.secondary_chain) == 0: return string_mainchain

        string_forkchain = "Fork Chain --> \n"

        for height in self.secondary_chain:
            string_forkchain += "[{}:{}] \n".format(height, self.secondary_chain[height].getHash())

        return string_mainchain + " \n " + string_forkchain

    def get_string_of_mainchain(self):

        string_mainchain = "Main Chain --> \n"

        for height in self.main_chain:
            string_mainchain += "[{}:{}]".format(height,self.main_chain[height].getHash().hexdigest())

        return string_mainchain

