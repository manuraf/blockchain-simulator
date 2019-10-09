from .ThreadExperiment5 import ThreadExperiment5
import threading

from experimental.classes.Ecosystem import Ecosystem
from experimental.classes.ValuesChange import ValuesChange


class Experiment7(threading.Thread):

    def __init__(self, id, settings, repository):
        threading.Thread.__init__(self)

        self.repository = repository
        self.settings = settings
        self.id = id
        self.points = []

    def run(self):
        ecosystem = Ecosystem(ValuesChange(int(self.settings["node"]), int(self.settings["iteration"]), 1), 0.5)
        miners_alive, chains, average_broadcast, miners_dead, fringprint_at_dead, miners_budget = ecosystem.run(True)

        for i in range(0, len(fringprint_at_dead)):
            dead = fringprint_at_dead[i]

            self.points.append([dead[2], dead[3], dead[4]]) # , dead[5]])

        self.repository.save_experimental({'id': self.id, 'experiment': 7, 'settings': self.settings, 'points': self.points})






