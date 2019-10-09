import random
import datetime
import imageio
import os

from repository.MongoRepository import MongoRepository
from experimental.Experiment1 import Experiment1
from experimental.Experiment2 import Experiment2
from experimental.Experiment3 import Experiment3
from experimental.Experiment4 import Experiment4
from experimental.Experiment5 import Experiment5
from experimental.Experiment6 import Experiment6
from experimental.Experiment7 import Experiment7
from experimental.Experiment8 import Experiment8
from experimental.Experiment9 import Experiment9


class Service:

    def __init__(self):
        self.repository = MongoRepository()

    def execute(self, n_expe, settings):
        id = int(random.random() * 1000)
        if n_expe == 1:
            thread = Experiment1(id, settings, self.repository)
            thread.start()
        elif n_expe == 2:
            thread = Experiment2(id, settings, self.repository)
            thread.start()
        elif n_expe == 3:
            thread = Experiment3(id, settings, self.repository)
            thread.start()
        elif n_expe == 4:
            thread = Experiment4(id, settings, self.repository)
            thread.start()
        elif n_expe == 5:
            thread = Experiment5(id, settings, self.repository)
            thread.start()
        elif n_expe == 6:
            thread = Experiment6(id, settings, self.repository)
            thread.start()
        elif n_expe == 7:
            thread = Experiment7(id, settings, self.repository)
            thread.start()
        elif n_expe == 8:
            thread = Experiment8(id, settings, self.repository)
            thread.start()
        elif n_expe == 9:
            thread = Experiment9(id, settings, self.repository)
            thread.start()

        return id

    def get_experiments(self, id):
        return self.repository.get_experiments(id)

    def get_experiment(self, id):
        return self.repository.get_experiment(id)

    def create_gif(self):
        images = []
        filenames = []

        for root, dirs, files in os.walk("./img"):
            for filename in files:
                filenames.append("img/" + filename)

        filenames.sort(key=lambda x: os.stat(os.path.join(".", x)).st_mtime)

        if len(filenames) > 50:
            filenames = filenames[:50]

        for filename in filenames:
            images.append(imageio.imread(filename))

        output_file = 'img/Gif-%s.gif' % datetime.datetime.now().strftime('%Y-%M-%d-%H-%M-%S')
        imageio.mimsave(output_file, images, duration=0.5)
        return output_file

