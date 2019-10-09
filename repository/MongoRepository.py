from pymongo import MongoClient


class MongoRepository:

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        # self.client = MongoClient('172.31.41.179', 27017)

    def get_experiments(self, id):
        db = self.client.test_database
        experimentals = db.experimentals
        param_id = int(id)
        ids = []
        for x in experimentals.find({"experiment": param_id}, {"id": 1, "settings": 2, "_id": 0}):
            ids.append({"id": x["id"], "settings": x["settings"]})
        return ids

    def get_experiment(self, id):
        db = self.client.test_database
        experimentals = db.experimentals
        param_id = int(id)
        return experimentals.find_one({"id": param_id},{ "points": 1, "settings": 2, "labels": 3, "_id": 0 })

    def save_experimental(self, experimental):
        db = self.client.test_database
        experimentals = db.experimentals
        experimental_id = experimentals.insert_one(experimental).inserted_id

    def get_client(self):
        return self.client


if __name__ == '__main__':
    mongorp = MongoRepository()
    db = mongorp.get_client().test_database
    # experimentals = db.experimentals
    # print(experimentals.find_one())
    cursor = mongorp.get_experiments(1)
    print(cursor)