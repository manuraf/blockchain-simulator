import hashlib


class Block:
    def __init__(self, parent, time):
        self.parent = parent
        # self.miner = miner
        self.time = time
        self.height = 0
        self.transactions = []

        if parent != None: 
               self.height = parent.getHeight()+1

        # calculate hash
        hash_block = "{}{}".format(self.height,self.time)
        if parent != None: 
               hash_block = "{}{}".format(hash_block,parent.getHash())

        self.hash = hashlib.sha224(hash_block.encode('utf-8'))

    def addTransaction(self, transaction):
        self.transactions.append(transaction)

    def getTransactions(self):
        return self.transactions

    def getParent(self):
        return self.parent

    def getHash(self):
        return self.hash

    def getHeight(self):
        return self.height

    def getTime(self):
        return self.time

    def getMiner(self):
        if len(self.transactions) > 0:
            return self.transactions[0].getOutNode()
        return None

    def __str__(self):
        return "{} {}".format(self.height, self.hash)
