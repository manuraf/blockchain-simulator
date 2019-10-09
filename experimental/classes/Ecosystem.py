import networkx as nx
import numpy as np
import random
import logging
import os
import matplotlib.pyplot as plt

from experimental.classes.Util import Util


class Ecosystem:

    def __init__(self, behaviour, p):
        self.behaviour = behaviour
        self.p = p
        self.miners = behaviour.get_setting()
        self.miners_budget = {}

        self.time = 0
        self.reward = 12

        self.graph = nx.erdos_renyi_graph(len(self.miners), self.p)
        self.nodes = self.graph.nodes()
        self.pos = nx.spring_layout(self.graph)

        # list of <hash-block : block>
        self.blocks = {}
        self.blocksMined = []
        self.miners_dead = {}
        self.time_last_dead = 0
        self.times_broadcast = []
        self.fringprint_at_dead = []
        self.standard_deviation = []

        # list of <hash-block : color>
        self.color = ['b', 'r', 'y', 'green', 'violet']
        self.colorBlocks = {}
        self.indexBlock = 0

        # for each hash-block I have miners who receive the block
        self.consensus = {}

    def run(self, print_graph=False):

        if print_graph:
            self.remove_img()
            self.plot_graph()

        fringprint = self._fringprint_network()

        while not self.behaviour.is_time_to_stop(self.blocks):

            new_blocks = []

            if self.behaviour.is_time_to_mine(self.blocks):

                rate = random.uniform(0, 1)

                # check if some miners have mined blocks and add them in new_blocks
                for key in self.miners:
                    miner = self.miners[key]
                    blocks_miner = miner.mining(rate, self.time, self.reward, 1)
                    new_blocks.extend(blocks_miner)

                if len(new_blocks) > 0 :
                    # add new_blocks inside blocks_to_broadcast
                    self.setBlocksMined(new_blocks)

            self._broadcast_one(print_graph)

            if print_graph: self._plot_img()

            dead = 0

            for key in list(self.miners):
                miner = self.miners[key]
                budget = miner.get_budget()

                self._update_miners_budget(key, budget)
                self._printBlockchains(miner)
                self._resolveOrphaned(miner)

                if budget < 0:
                    dead += 1
                    self._remove_node(miner)

            if dead > 0:
                self.fringprint_at_dead.append([dead, self.time, self.time - self.time_last_dead, fringprint[0], fringprint[1], fringprint[2]])
                self.time_last_dead = self.time
                fringprint = self._fringprint_network()

            self.standard_deviation.append(Util.calculate_standard_deviation(self.miners))

            self.time += 1

        return self.miners, \
               Util.get_chains(self.miners), \
               Util.evaluate_average_broadcast(self.times_broadcast), \
               self.miners_dead, \
               self.fringprint_at_dead, \
               self.miners_budget, \
               self.standard_deviation

    def _fringprint_network(self):
        total_power = list(map(lambda x: int(self.miners[x].get_power() * 1000), self.miners.keys()))
        power_variance = np.var(total_power) / np.var([0,100]) * 100

        total_budget = list(map(lambda x: self.miners[x].get_init_budget(), self.miners.keys()))
        budget_variance = np.var(total_budget) / np.var([0, self.behaviour.get_max_budget()]) * 100

        total_cost = list(map(lambda x: int(self.miners[x].get_energy_cost() * 100), self.miners.keys()))
        cost_variance = np.var(total_cost) / np.var([0,100]) * 100
        return [int(power_variance), int(budget_variance), int(cost_variance)]

    def _remove_node(self, miner):
        self.graph.remove_node(miner.getId())
        new_miners = self.behaviour.miner_dead(miner, self.time)
        self._add_node(new_miners)
        miner.set_age(self.time - miner.get_time_created())

        self.miners_dead[miner.getId()] = miner # [age, miner.get_power(), miner.get_init_budget(), miner.get_energy_cost()]

    def _add_node(self, miners):
        for miner in miners:
            self.graph.add_node(miner.getId())
            neighbor = None

            for node in self.graph.nodes():
                if node != miner.getId():
                    if random.random() < self.p:
                        self.graph.add_edge(node, miner.getId())
                        neighbor = node

            if neighbor is not None:
                miner.downloadBlockchain(self.miners[neighbor])

        self.pos = nx.spring_layout(self.graph)

    def _update_miners_budget(self, id, current_budget):

        if id not in self.miners_budget:
            self.miners_budget[id] = list(map(lambda x: 0, range(self.time+1)))

        self.miners_budget[id].append(current_budget)

    def _printBlockchains(self, miner):
        logging.info(' MINER {}'.format(miner.getId()));
        logging.info(miner.getStringOfBlockchains())

    def _resolveOrphaned(self, miner):
        if len(miner.getOrphaned()) > 0:

            i_neighbors = list(self.graph.neighbors(miner.getId()))
            neighbors = []

            for key in self.miners:
                neighbor = self.miners[key]
                if neighbor.getId() in i_neighbors:
                    neighbors.append(neighbor)
            miner.resolve_orphans_block(neighbors)

    def _broadcast_one(self, print_graphs=True):

        # logging.info("\n \n Executing time: {}".format(self.time))
        # logging.info("consensus network: {}".format(self.consensus))
        has_changed = False

        if len(self.blocks) > 0:

            active = self._get_nodes_active()

            consensus_new = {key:[] for key in self.consensus}
            # logging.info("active {} nodes".format(active))

            for n in filter(lambda n: n not in active, self.nodes):
                # get n's neighbors
                neighbors = list(self.graph.neighbors(n))

                # for each block, get neighbors of n which has it
                # and what is the hash block with more neighbors of n
                neighbors_have_block,max_hash = self._getNeighborsHaveBlockAndMaxHash(n, neighbors)

                if max_hash is None: continue
                # some n's neighbors have almost one block which n does not have
                # maxHash is the hash block closest to n
                has_changed = True

                # add this block to n's blockchain
                consensus_new[max_hash].append(n)
                self.miners[n].add_block(self.blocks[max_hash])

                del neighbors_have_block[max_hash]
                if len(neighbors_have_block) == 0: continue

                # if there are more than one block, add others blocks
                for key in neighbors_have_block:
                    if len(neighbors_have_block[key]) == 0: continue
                    consensus_new[key].append(n)
                    self.miners[n].add_block(self.blocks[key])

        if print_graphs:
            self.__update_color()

        # logging.info("--> {}".format(has_changed))

        # if blockchain changes, update consensus
        if has_changed:
            for key in consensus_new:     
                self.consensus[key].extend(consensus_new[key])
                if len(self.consensus[key]) >= len(self.miners):
                    # if all nodes have received the block, I remove it from consensus
                    self._delete_blocks(key)
        else:
            self._delete_blocks()

        self.__addBlocksMined()
        # logging.info("\n")
        return has_changed

    # associate to block one color
    def __setColorToBlock(self, hash):
        color = self.color[self.indexBlock]
        self.colorBlocks[hash] = color

        if self.indexBlock == len(self.color)-1:
            self.indexBlock = 0
        else:
            self.indexBlock += 1

    def setBlocksMined(self, blocks):
        if len(blocks) == 0: return

        self.blocksMined = blocks
        for block in blocks:
            self.__setColorToBlock(block.getHash())

    def _delete_blocks(self, hash=None):
        if hash is not None:
            # store time broadcast
            block = self.blocks[hash]
            time = self.time - block.getTime()
            self.times_broadcast.append(time)

            del self.consensus[hash]
            del self.blocks[hash]
        else:
            if len(self.blocks) > 0:
                # store time broadcast
                block = next(iter(self.blocks.values()))
                time = self.time - block.getTime()
                self.times_broadcast.append(time)

            self.consensus = {}
            self.blocks = {}

    def __addBlocksMined(self):
        if len(self.blocksMined) > 0:

            for b in self.blocksMined:
                self.blocks[b.getHash()]=b
                self.consensus[b.getHash()]=[b.getMiner()]

        self.blocksMined = []

    def _get_nodes_active(self):
        miners = list(map(lambda key: self.miners[key], self.miners.keys()))
        if len(self.consensus) == 0: return miners

        active = []
        for miner in miners:
            has_received = True
            # check if miner has received all blocks
            for k in self.consensus:
                has_received = miner.getId() in self.consensus[k]
                if not has_received: break

            if has_received: active.append(miner.getId())
        return active

    # { hash : [miner0,miner1], ... }  
    def _getNeighborsHaveBlockAndMaxHash(self,node,neighbors):
        neighbors_have_block = {}
        maxHash = None
        max_h = 0
        for key in self.consensus:
            miners = self.consensus[key]
            if node in miners : continue
            neighbors_have_block[key] = [n for n in neighbors if n in miners]
            h = len(list(neighbors_have_block[key]))
            if h > max_h : maxHash = key
        return neighbors_have_block, maxHash

    def plot_graph(self, label=True, grey=True):
        plt.axis('off')
        self.__update_color(label, grey)
        plt.savefig("img\Graph.png")

    def _plot_img(self, show=False):
        plt.axis('off')
        plt.text(1, 1, "t: {}".format(self.time), ha='right', va='top')
        # plt.text(0.8, 1, "h: {}".format(self.iteration-self.i_iteration), ha='right', va='top')
        plt.savefig("img/Graph_{}.png".format(self.time))
        # plt.legend()
        if show:
            plt.show()
        plt.close()

    def __update_color(self, label=True, grey=False):
        # {'color':{'bounder':[miner]}}
        colorsMiners = {}
        unions = set()

        # for each miner get last block and associate the color
        if len(self.colorBlocks) > 0:
            for key in self.miners:
                miner = self.miners[key]

                # get color of hash block
                hash_block = miner.getLastBlock().getHash()
                color_block = 'grey'
                if hash_block in self.colorBlocks:
                    color_block = self.colorBlocks[hash_block]

                # get color of hash block
                color_parent_block = 'grey'
                if not miner.getLastBlock().getParent() is None:
                    hash_parent_block = miner.getLastBlock().getParent().getHash()
                    if hash_parent_block in self.colorBlocks:
                        color_parent_block = self.colorBlocks[hash_parent_block]

                """""
                if hash_block in self.colorBlocks:
                    color = self.colorBlocks[hash_block]
                    if color in colorsMiners:
                        colorsMiners[color].append(miner.getId())
                    else:
                        colorsMiners[color] = [miner.getId()]
                """

                if color_block in colorsMiners:
                    if color_parent_block in colorsMiners[color_block]:
                        colorsMiners[color_block][color_parent_block].append(miner.getId())
                    else:
                        colorsMiners[color_block][color_parent_block] = [miner.getId()]
                else:
                    colorsMiners[color_block] = {color_parent_block: [miner.getId()]}

            for key_child in colorsMiners:
                for key_parent in colorsMiners[key_child]:
                    nx.draw_networkx_nodes(self.graph, self.pos,
                                   nodelist=list(colorsMiners[key_child][key_parent]),
                                   node_color=key_child, label="{}".format(0),
                                   node_size=100, edgecolors=key_parent,
                                   alpha=0.8)
                    unions = unions.union(colorsMiners[key_child][key_parent])

        normal_nodes = set(self.nodes).difference(unions)

        if grey:
            nx.draw_networkx_nodes(self.graph, self.pos,
                                   nodelist=list(normal_nodes),
                                   node_color='grey', label="{}".format(0),
                                   node_size=50,
                                   alpha=0.8)
        else:
            nx.draw_networkx_nodes(self.graph, self.pos,
                                   nodelist=list(normal_nodes),
                                   node_color='black', label="{}".format(0),
                                   node_size=50,
                                   alpha=0.8)

        nx.draw_networkx_edges(self.graph, self.pos,
                               width=0.8, alpha=0.5,
                               edge_color='grey')
        if label:
            nx.draw_networkx_labels(self.graph, self.pos,
                                    font_size=8, font_family='sans-serif')

    def remove_img(self):
        for root, dirs, files in os.walk("./img"):
            for filename in files:
                try:
                    os.remove("img/" + filename)
                except OSError:
                    pass

