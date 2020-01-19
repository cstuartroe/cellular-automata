from web.settings_secret import *
from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
from ruleset_learning import RulesetLearner
from games import ProbabilisticConway, RedVsBlue, Rhomdos, name_to_class
import logging

INFO_LOGGER = logging.getLogger('info_logger')
ERROR_LOGGER = logging.getLogger('error_logger')

class MongoUtility:

    def __init__(self, game_name='', ep_id=''):

        client = MongoClient(MONGO_END_POINT, username=MONGO_USER, password=MONGO_PWD)
        db = client.biotaornada
        self.ep_col = db.epsilon
        self.pre_train = db.pre_training
        self.storage = db.storage
        self.ep_id = {game_name: ep_id}

    def initialize_epsilon(self, init_epsilon, game_name):
        num_results = self.count_by_name(game_name, ep=True)

        if num_results == 0:
            self.ep_id[game_name] = self.ep_col.insert_one(
                {'game_name': game_name, 'epsilon': init_epsilon}
            ).inserted_id
        elif num_results == 1:
            self.ep_id = self.ep_col.find_one({'game_name': game_name})['_id']
            self.set_epsilon(init_epsilon, game_name)
        else:
            MongoUtility.remove_all_documents(self.ep_col)
            self.ep_id[game_name] = self.ep_col.insert_one(
                {'game_name': game_name, 'epsilon': init_epsilon}
            ).inserted_id

    def get_epsilon(self, game_name):
        return self.ep_col.find_one({'game_name': game_name})['epsilon']

    def set_epsilon(self, epsilon, game_name):
        new_value = {'$set': {'epsilon': epsilon}}
        self.ep_col.update_one({'_id': ObjectId(self.ep_id[game_name])}, new_value)

    @staticmethod
    def remove_all_documents(collection):
        for document in collection.find():
            doc_id = document['_id']
            collection.remove({'_id': ObjectId(doc_id)})

    @staticmethod
    def get_doc_count(collection):
        return collection.estimated_document_count()

    def count_by_name(self, game_name, pre=True, ep=False):
        if pre:
            results = self.pre_train.find({'game_name': game_name})
        elif ep:
            results = self.ep_col.find({'game_name': game_name})
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
            self.pre_train.insert_one(json)
        else:
            self.storage.insert_one(json)

    def update_rating(self, game_id, rating):
        new_value = {'$set': {'rating': rating}}
        self.pre_train.update_one({'key': game_id}, new_value)

    def prune_samples(self, pre=True):
        if pre:
            self.pre_train.delete_many({'rating': -1})
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
            self.pre_train.update_one({'key': rule_id}, new_value)
        else:
            self.storage.update_one({'key': rule_id}, new_value)

    def get_sample(self, game_id, pre=False):
        if pre:
            return self.pre_train.find_one({'key': game_id})
        else:
            return self.storage.find_one({'key': game_id})

    def dump_and_train(self, game_name, dump_after):

        game_class = name_to_class(game_name)[0]

        trainer = RulesetLearner(game_class, '', game_args=[], game_kwargs={'width': -1, 'height': -1},
                                 num_frames=20, num_trials=5)

        results = self.pre_train.find({'game_name': game_name})
        num_samples = results.count()

        samples = np.zeros((num_samples, game_class.RULE_SPEC.num_dimensions))
        labels = np.zeros((num_samples, 1))

        steps_per = trainer.steps_per_epoch

        INFO_LOGGER.info(f'STEPS PER: {steps_per}')
        INFO_LOGGER.info(f'SAMPLES/STEPSPER: {int(num_samples/steps_per)}')

        if int(num_samples/steps_per) <= 0 or int(num_samples % steps_per) != 0:
            return dump_after

        else:
            count = 0

            for document in results:
                ruleset = eval(document['ruleset'])
                rating = float(document['rating'])
                doc_id = document['_id']

                rule_array = np.reshape(np.asarray(ruleset), (game_class.RULE_SPEC.num_dimensions, ))

                samples[count] = rule_array
                labels[count] = rating

                self.storage.insert_one(document)
                self.pre_train.remove({'_id': doc_id})

                count += 1

            print(samples)
            print(labels)

            trainer.continue_training(game_name=game_name, samples=samples, labels=labels)

            if dump_after < 50:
                return 50
            else:
                return dump_after






