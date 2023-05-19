from pymongo import MongoClient


class Db():
    def __init__(self):
        db_uri = 'mongodb://arxivdb:27017'
        self.connection = MongoClient(db_uri)
        self.db = self.connection.arxiv

    def __del__(self):
        self.connection.close()
