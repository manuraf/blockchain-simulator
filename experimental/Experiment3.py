from .ThreadExperiment3 import ThreadExperiment3
import threading


class Experiment3(threading.Thread):

    def __init__(self, id, settings, repository):
        threading.Thread.__init__(self)

        self.repository = repository
        self.settings = settings
        self.id = id
        self.points = []

    def run(self):
        threads = []

        for i in range(1, 10):
            print_graph = True if i == 5 else False
            threads.append(ThreadExperiment3(print_graph, int(self.settings["node"]), int(self.settings["iteration"]), self.points, i))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        self.repository.save_experimental({'id': self.id, 'experiment': 3, 'settings': self.settings, 'points': self.points})






