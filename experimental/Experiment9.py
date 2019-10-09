from .ThreadExperiment5 import ThreadExperiment5
import threading

from experimental.classes.Ecosystem import Ecosystem
from experimental.classes.ValuesChangeAndNoShareBlock import ValuesChangeAndNoShareBlock


class Experiment9(threading.Thread):

    def __init__(self, id, settings, repository):
        threading.Thread.__init__(self)

        self.repository = repository
        self.settings = settings
        self.id = id
        self.points = []

    def run(self):
        ecosystem = Ecosystem(ValuesChangeAndNoShareBlock(int(self.settings["node"]), int(self.settings["iteration"])), 0.5)
        miners_alive, chains, average_broadcast, miners_dead, fringprint_at_dead, miners_budget, standard_deviation = ecosystem.run(True)
        record = {'id': self.id, 'experiment': 9, 'settings': self.settings}

        record['points'] = []

        for i in range(len(standard_deviation)):
            record['points'].append([i, standard_deviation[i]])

        self.repository.save_experimental(record)






