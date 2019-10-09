from .ThreadExperiment5 import ThreadExperiment5
import threading

from experimental.classes.Ecosystem import Ecosystem
from experimental.classes.ValuesChange import ValuesChange


class Experiment8(threading.Thread):

    def __init__(self, id, settings, repository):
        threading.Thread.__init__(self)

        self.repository = repository
        self.settings = settings
        self.id = id
        self.points = []

    def run(self):
        ecosystem = Ecosystem(ValuesChange(int(self.settings["node"]), int(self.settings["iteration"])), 0.5)
        miners_alive, chains, average_broadcast, miners_dead, fringprint_at_dead, miners_budget = ecosystem.run(True)
        record = {'id': self.id, 'experiment': 8, 'settings': self.settings}
        labels = {}

        i_miner = 0
        iterations = max(list(map(lambda x: len(miners_budget[x]), miners_budget)))
        for key in miners_budget:
            miner = miners_alive[key] if key in miners_alive else miners_dead[key]

            if miner.get_time_created() == 0:
                miner_budget = miners_budget[key]
                current_iterations = len(miner_budget)

                if i_miner == 0:
                    for i in range(iterations):
                        self.points.append([i+1])
                    i_miner += 1

                if current_iterations < iterations:
                    final_budget = list(map(lambda x: 0, range(iterations - current_iterations)))
                    miner_budget = miner_budget + final_budget

                for i in range(iterations):
                    self.points[i].append(miner_budget[i])

                labels[str(i_miner)] = "[({})({})({})]".format(round(miner.get_hashrate()[1]-miner.get_hashrate()[0], 4), round(miner.get_init_budget(), 0), round(miner.get_energy_cost(), 4))
                i_miner += 1

        record['points'] = self.points
        record['labels'] = labels

        self.repository.save_experimental(record)






