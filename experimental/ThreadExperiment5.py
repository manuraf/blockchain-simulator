import threading

from experimental.classes.Ecosystem import Ecosystem
from experimental.classes.BehaviourMinersByVariance import BehaviourMinersByVariance


class ThreadExperiment5(threading.Thread):

    def __init__(self, print_graph, nodes, iteration, points, variance):
        threading.Thread.__init__(self)
        self.print_graph = print_graph
        self.node = nodes
        self.points = points
        self.variance = variance
        self.iteration = iteration

    def run(self):
        ecosystem = Ecosystem(BehaviourMinersByVariance(self.node, self.iteration, self.variance), 0.5)
        miners_alive, chains, average_broadcast, miners_dead, fringprint_at_dead, miners_budget = ecosystem.run(self.print_graph)
        self.points.append([self.variance, len(miners_dead)])