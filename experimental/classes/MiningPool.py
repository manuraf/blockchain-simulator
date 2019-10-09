
class MiningPool:
    def __init__(self):
        self.miners = []
        self.totalPower = 0

    def getMiners(self):
        return self.miners

    def addMiners(self, miner):
        self.miners.append(miner)
        self.totalPower += miner.get_hashrate()

    def addTransactionsAndDistributeRewardAndFee(self, block, reward, fee):
        for miner in mines:
            perc = miner.get_hashrate() / self.totalPower
            #miner.addBudget(amount * perc)
            block.addTransaction(Transaction(perc * fee, miner.getId(), perc * reward))

    def getTotalPower(self):
        return self.totalPower

