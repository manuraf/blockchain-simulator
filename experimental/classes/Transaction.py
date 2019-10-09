
class Transaction:
    def __init__(self, fee, outNode, outAmount, inNode=None, inAmount=None):
        self.inNode = inNode
        self.inAmount = inAmount
        self.outNode = outNode
        self.outAmount = outAmount
        self.fee = fee

    def getOutNode(self):
        return self.outNode

    def getOutNode(self):
        return self.outNode

    def getOutAmount(self):
        return self.outAmount

    def getInNode(self):
        return self.inNode

    def getInAmount(self):
        return self.inAmount

    def getFee(self):
        return self.fee


