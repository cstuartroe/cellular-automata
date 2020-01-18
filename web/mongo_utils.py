from web.settings_secret import *
from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
from ruleset_learning import RulesetLearner
from games import ProbabilisticConway, RedVsBlue, Rhomdos, name_to_class

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

    def count_by_name(self, game_name, pre=True):
        if pre:
            results = self.pre_sample_col.find({'game_name': game_name})
        else:
            results = self.storage.find({'game_name': game_name})

        return results.count()

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

    def update_rating(self, game_id, rating):
        new_value = {'$set': {'rating': rating}}
        self.pre_sample_col.update_one({'key': game_id}, new_value)

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

        game_class = name_to_class(game_name)[0]

        results = self.pre_sample_col.find({'game_name': game_name})
        num_samples = results.count()

        samples = np.zeros((num_samples, game_class.RULE_SPEC.num_dimensions))
        labels = np.zeros((num_samples, 1))

        count = 0

        for document in results:
            ruleset = eval(document['ruleset'])
            rating = float(document['rating'])
            doc_id = document['_id']

            rule_array = np.reshape(np.asarray(ruleset), (game_class.RULE_SPEC.num_dimensions, ))

            samples[count] = rule_array
            labels[count] = rating

            self.storage.insert_one(document)
            self.pre_sample_col.remove({'_id': doc_id})

            count += 1

        print(samples)
        print(labels)

        trainer = RulesetLearner(game_class, '', game_args=[], game_kwargs={'width': -1, 'height': -1},
                                 num_frames=20, num_trials=5)

        trainer.continue_training(game_name=game_name, samples=samples, labels=labels)






