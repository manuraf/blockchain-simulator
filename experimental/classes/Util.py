import hashlib
import numpy as np


class Util:

    @staticmethod
    def get_chains(miners):
        chains = {}

        for miner in miners:
            blockchain = miners[miner].get_string_of_mainchain()
            hash_block = hashlib.sha224(blockchain.encode('utf-8')).hexdigest()

            if hash_block in chains:
                length = chains[hash_block]
                chains[hash_block] = length + 1
            else:
                chains[hash_block] = 1

        return chains

    @staticmethod
    def evaluate_average_broadcast(times_broadcast):
        return sum(times_broadcast) / len(times_broadcast)

    @staticmethod
    def build_secondary_chain(block, main_chain):
        secondary_chain = None
        i_height = len(main_chain) - 2
        is_parent = False
        while i_height >= 0:
            last_block = main_chain[i_height]
            if block.getParent().getHash() == last_block.getHash():
                is_parent = True
                secondary_chain = {}

            if is_parent:
                secondary_chain[i_height] = last_block
            i_height = i_height - 1

        return secondary_chain

    @staticmethod
    def verify_belong_chain_and_add(chain, block):
        height = len(chain)
        if height == 0: return False
        last_block = chain[height-1]

        if block.getParent().getHash() == last_block.getHash():
            # add block to the main chain
            chain[height] = block
            return True
        return False

    @staticmethod
    def calculate_standard_deviation(miners):
        array_a1 = list(map(lambda x: miners[x].get_behaviour()[0], miners.keys()))
        variance_a1 = np.var(array_a1)

        array_a2 = list(map(lambda x: miners[x].get_behaviour()[1], miners.keys()))
        variance_a2 = np.var(array_a2)

        array_a3 = list(map(lambda x: miners[x].get_behaviour()[2], miners.keys()))
        variance_a3 = np.var(array_a3)

        array_a4 = list(map(lambda x: miners[x].get_behaviour()[3], miners.keys()))
        variance_a4 = np.var(array_a4)

        return max([variance_a1, variance_a2, variance_a3, variance_a4])
