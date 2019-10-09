import threading

from experimental.classes.Ecosystem import Ecosystem
from experimental.classes.WaitUntilFullBroadcast import WaitUntilFullBroadcast


class ThreadExperiment2(threading.Thread):

    def __init__(self, print_graph, nodes, iteration, points, p):
        threading.Thread.__init__(self)
        self.print_graph = print_graph
        self.node = nodes
        self.points = points
        self.p = p
        self.iteration = iteration

    def run(self):
        ecosystem = Ecosystem(WaitUntilFullBroadcast(self.node, self.iteration), self.p)
        miners_alive, chains, average_broadcast, miners_dead, fringprint_at_dead, miners_budget = ecosystem.run(self.print_graph)
        self.points.append([self.p, average_broadcast])