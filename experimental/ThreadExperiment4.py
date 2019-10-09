import threading

from experimental.classes.Ecosystem import Ecosystem
from experimental.classes.Default import Default


class ThreadExperiment4(threading.Thread):

    def __init__(self, print_graph, nodes, iteration, points, waiting):
        threading.Thread.__init__(self)
        self.print_graph = print_graph
        self.node = nodes
        self.points = points
        self.waiting = waiting
        self.iteration = iteration

    def run(self):
        ecosystem = Ecosystem(Default(self.node, self.iteration, waiting=self.waiting), 0.5)
        miners_alive, chains, average_broadcast, miners_dead, fringprint_at_dead, miners_budget = ecosystem.run(self.print_graph)
        self.points.append([self.waiting, len(miners_dead)])