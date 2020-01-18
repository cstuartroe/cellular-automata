from web.settings_secret import *
from pymongo import MongoClient
from bson.objectid import ObjectId


class Mongo_Utility:

    def __init__(self, ep_id=''):

        client = MongoClient(MONGO_END_POINT, username=MONGO_USER, password=MONGO_PWD)
        db = client.biotaornada
        self.ep_col = db.epsilon
        self.ep_id = ep_id

    def initialize_epsilon(self, init_epsilon):
        if self.ep_col.estimated_document_count() == 0:
            self.ep_id = self.ep_col.insert_one({'epsilon': init_epsilon}).inserted_id
        elif self.ep_col.estimated_document_count() == 1:
            self.ep_id = self.ep_col.find_one()['_id']
            self.set_epsilon(init_epsilon)
        else:
            Mongo_Utility.remove_all_documents(self.ep_col)
            self.ep_id = self.ep_col.insert_one({'epsilon': init_epsilon}).inserted_id

    def get_epsilon(self):
        return self.ep_col.find_one()['epsilon']

    def set_epsilon(self, epsilon):
        new_value = {'$set': {'epsilon': epsilon}}
        self.ep_col.update_one({'_id': ObjectId(self.ep_id)}, new_value)

    def build_sample_doc(self, ruleset, value):
        pass

    @staticmethod
    def remove_all_documents(collection):
        for document in collection.find():
            doc_id = document['_id']
            collection.remove({'_id': ObjectId(doc_id)})

    @staticmethod
    def get_doc_count(collection):
        return collection.estimated_document_count()

