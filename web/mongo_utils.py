from web.settings_secret import *
from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
from ruleset_learning import RulesetLearner

class MongoUtility:

    def __init__(self, ep_id=''):

        client = MongoClient(MONGO_END_POINT, username=MONGO_USER, password=MONGO_PWD)
        db = client.biotaornada
        self.ep_col = db.epsilon
        self.pre_sample_col = db.pre_training
        self.storage = db.storage
        self.ep_id = ep_id

    def initialize_epsilon(self, init_epsilon):
        if self.ep_col.estimated_document_count() == 0:
            self.ep_id = self.ep_col.insert_one({'epsilon': init_epsilon}).inserted_id
        elif self.ep_col.estimated_document_count() == 1:
            self.ep_id = self.ep_col.find_one()['_id']
            self.set_epsilon(init_epsilon)
        else:
            MongoUtility.remove_all_documents(self.ep_col)
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

    @staticmethod
    def sample_to_json(id, ruleset, game_name, value=-1, grad_steps=0, grad_max=0, grad_min=0, frames=50):
        st_set = str(ruleset.tolist())

        json = {'key': id, 'game_name': game_name, 'ruleset': st_set, 'rating': value, 'grad_steps': grad_steps,
                'grad_max': grad_max, 'grad_min': grad_min, 'frames': frames}

        return json

    def send_sample(self, json, pre=True):
        if pre:
            self.pre_sample_col.insert_one(json)
        else:
            self.storage.insert_one(json)

    def update_rating(self, rule_id, rating):
        new_value = {'$set': {'rating': rating}}
        self.pre_sample_col.update_one({'key': rule_id}, new_value)

    def prune_samples(self, pre=True):
        if pre:
            self.pre_sample_col.delete_many({'rating': -1})
        else:
            self.storage.delete_many({'rating': -1})

    def add_game(self, rule_id, game, pre=True):
        json = {}

        for key, value in game.__dict__.items():
            if isinstance(value, np.ndarray):
                value = str(value.tolist())
            json[key] = value

        new_value = {'$set': json}

        if pre:
            self.pre_sample_col.update_one({'key': rule_id}, new_value)
        else:
            self.storage.update_one({'key': rule_id}, new_value)

    def get_sample(self, game_id, pre=False):
        if pre:
            return self.pre_sample_col.find_one({'key': game_id})
        else:
            return self.storage.find_one({'key': game_id})

    def dump_and_train(self, game_name):

        results = self.pre_sample_col.find({'game_name': game_name})
        num_samples = results.count()

        samples = np.zeros((num_samples, game_name.RULE_SPEC.num_dimensions))
        labels = np.zeros((num_samples, 1))

        model_load_from = f'storage/models/{game_name}_model.h5'

        count = 0

        for document in results:
            ruleset = eval(document['ruleset'])
            rating = float(document['rating'])
            doc_id = document['_id']

            rule_array = np.reshape(np.asarray(ruleset), (game_name.RULE_SPEC.num_dimensions, ))

            samples[count] = rule_array
            labels[count] = rating

            self.storage.insert_one(document)
            self.pre_sample_col.remove({'_id': doc_id})

            count += 1

        # RulesetLearner.continue_training(samples=samples, labels=labels, load_from=model_load_from)






