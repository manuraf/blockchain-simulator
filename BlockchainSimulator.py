import logging
import os
from experimental.classes.Ecosystem import Ecosystem

from experimental.classes.Default import Default
from experimental.classes.WaitUntilFullBroadcast import WaitUntilFullBroadcast
from experimental.classes.ValuesChange import ValuesChange
from experimental.classes.ValuesChangeLowHashrate import ValuesChangeLowHashrate
from experimental.classes.ValuesChangeAndNoShareBlock import ValuesChangeAndNoShareBlock
from experimental.classes.BehaviourMinersByVariance import BehaviourMinersByVariance

log_name = "logs/BlockChainSimulator.log"
try:
    os.remove(log_name)
except OSError:
    pass

logging.basicConfig(filename=log_name,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.INFO, datefmt="%H:%M:%S",
                    filemode='w')

#ecosystem = Ecosystem(Default(10, 20, Block(None, 0), 4), 0.5)
#ecosystem = Ecosystem(ValuesChangeAndNoShareBlock(10, 20, 5), 0.5)
ecosystem = Ecosystem(ValuesChangeAndNoShareBlock(20, 200), 0.5)
alive, chains, time_broadcast, miners_dead, fringprint_at_dead, miners_budget, standard_deviation = ecosystem.run(True)
print(len(miners_dead))

'''
1- rendere più evidenti i nodi con le relative altezze (magari cerchiari col colore del predecessore)
2- vedere chi ha un blocco nuovo ma non lo condivide
'''