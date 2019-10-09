from .ThreadExperiment5 import ThreadExperiment5
import threading

from experimental.classes.Ecosystem import Ecosystem
from experimental.classes.ValuesChange import ValuesChange


class Experiment6(threading.Thread):

    def __init__(self, id, settings, repository):
        threading.Thread.__init__(self)

        self.repository = repository
        self.settings = settings
        self.id = id
        self.points = []

    def run(self):
        ecosystem = Ecosystem(ValuesChange(int(self.settings["node"]), int(self.settings["iteration"])), 0.5)
        miners_alive, chains, average_broadcast, miners_dead, fringprint_at_dead, miners_budget = ecosystem.run(True)

        for key in miners_dead:
            miner_dead = miners_dead[key]
            energy_cost = ''
            if miner_dead.get_energy_cost() < 0.33:
                energy_cost = 'Low'
            elif 0.33 <= miner_dead.get_energy_cost() <= 0.65:
                energy_cost = 'Medium'
            elif miner_dead.get_energy_cost() > 0.65:
                energy_cost = 'High'

            self.points.append([str(miner_dead.getId()), miner_dead.get_age(), miner_dead.get_power(), miner_dead.get_init_budget(), energy_cost])

        self.repository.save_experimental({'id': self.id, 'experiment': 6, 'settings': self.settings, 'points': self.points})






