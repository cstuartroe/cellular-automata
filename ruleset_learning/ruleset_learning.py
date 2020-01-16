import numpy as np
import random
import operator
from tqdm import tqdm
import tensorflow as tf
from tensorflow.keras import models, layers
import datetime
import time
import os
import logging

INFO_LOGGER = logging.getLogger('info_logger')
ERROR_LOGGER = logging.getLogger('error_logger')

class RulesetLearner:
    def __init__(self, game_class, objective_function, game_args, game_kwargs, num_frames, num_trials):
        self.game_class = game_class
        self.objective_function = objective_function
        self.game_args = game_args
        self.game_kwargs = game_kwargs
        self.num_frames = num_frames
        self.num_trials = num_trials
        self.num_layers = 6
        self.packed_samples = np.zeros((100, self.game_class.RULE_SPEC.num_dimensions))
        self.packed_labels = np.zeros((100, 1))
        self.packed_count = 0
        self.best = []
        self.first_train = True


    def monte_ruleset(self, rulevector):
        ruleargs, rulekwargs = self.game_class.rulevector2args(rulevector)
        outputs = []

        for i in range(self.num_trials):
            game = self.game_class(*self.game_args, *ruleargs, **self.game_kwargs, **rulekwargs)
            game.advances(self.num_frames)
            outputs.append(self.objective_function(game))

        return sum(outputs)/len(outputs)

    def deep_explore(self, epsilon, lr=0.005, grad_step_scalar=10, init_on_first=True,
                     num_best=20, save_to='trained_model.h5', epsilon_increment=0.01,
                     train_samples=1000, validation_samples=100, cut_off_increment=0.05):

        its = abs((epsilon - 1)/epsilon_increment)
        step = 1

        print("Based on your parameters, explore will run approximately " + str(its) + " times.")
        time.sleep(5)

        if init_on_first:
            print('Training initial model...')
            self.train_suggestion_model(lr=lr, train_samples=train_samples,
                                        validation_samples=validation_samples, save_to=save_to)

        while epsilon <= 1:

            print('Starting step ' + str(step))
            self.deep_explore_iteration(epsilon=epsilon, grad_step_scalar=grad_step_scalar,
                                        num_best=num_best, cut_off_increment=cut_off_increment, save_to=save_to)
            step += 1
            epsilon += epsilon_increment

        return self.best

    def training_sample(self, epsilon, cut_off_increment=0.05, load_from='trained_model.h5', grad_step_scalar=10):

        INFO_LOGGER.info('Starting training sample process...')
        new_test = self.game_class.RULE_SPEC.generate()

        cut_off = random.uniform(0, 1)

        while cut_off < epsilon:
            gs = abs(epsilon - cut_off)
            INFO_LOGGER.info('Fetching gradient descent step...')
            new_test, og_loss, new_loss = self.deep_suggestion(ruleset=new_test, new_training=False,
                                                               grad_step_scalar=(grad_step_scalar * gs),
                                                               load_from=load_from)
            cut_off += cut_off_increment

        return new_test

    def deep_explore_iteration(self, epsilon, grad_step_scalar=10,
                               num_best=20, cut_off_increment=0.05, save_to='trained_model.h5'):

        new_test = self.training_sample(epsilon=epsilon, grad_step_scalar=grad_step_scalar, load_from=save_to,
                                        cut_off_increment=cut_off_increment)

        result = self.monte_ruleset(new_test)

        print("Pushing to continued training...")
        self.continue_training(new_test, result, load_from=save_to)

        if len(self.best) < num_best:
            self.best.append((new_test, result))
        else:
            min_of_best = min(self.best, key=lambda t: t[1])
            if result > min_of_best[1]:
                print('Deleting value...')
                self.best.sort(key=operator.itemgetter(1))
                del self.best[0]
                self.best.append((new_test, result))

        self.best.sort(key=operator.itemgetter(1))

    def deep_suggestion(self, ruleset, new_training=False, lr=0.005,
                        train_samples=1000, validation_samples=100, save_to='trained_model.h5',
                        load_from='trained_model.h5', target_value=1, grad_step_scalar=10):

        if new_training:
            self.train_suggestion_model(lr=lr, train_samples=train_samples,
                                        validation_samples=validation_samples, save_to=save_to)

            load_from = save_to

        model = tf.keras.models.load_model(load_from)
        ruleset_tensor = self.ruleset_to_tensor(ruleset)

        loss_func = tf.losses.MeanAbsoluteError()

        og_loss = loss_func(target_value, model(ruleset_tensor))

        with tf.GradientTape(persistent=True) as gt:
            result = model(ruleset_tensor)
            loss = loss_func(target_value, result)

        gradients = gt.gradient(loss, model.trainable_weights)

        sans_bias = [grad for grad in gradients if len(grad.shape) == 2]

        loss_over_in = sans_bias[0]

        for g in sans_bias[1:]:
            loss_over_in = tf.linalg.matmul(loss_over_in, g)

        input_gradient = loss_over_in.numpy()
        input_gradient = np.reshape(input_gradient, (self.game_class.RULE_SPEC.num_dimensions,))

        suggestion = ruleset + (input_gradient * grad_step_scalar)

        valid = self.is_valid_ruleset(suggestion)

        if isinstance(valid, list):
            for i in valid:
                dimensions = self.game_class.RULE_SPEC.dimensions
                if suggestion[i] < dimensions[i].start:
                    suggestion[i] = dimensions[i].start
                else:
                    suggestion[i] = dimensions[i].end

        new_loss = loss_func(target_value, model(self.ruleset_to_tensor(suggestion)))

        return suggestion, og_loss, new_loss

    def is_valid_ruleset(self, ruleset):
        dimensions = self.game_class.RULE_SPEC.dimensions
        faults = []

        for i in range(len(dimensions)):
            if ruleset[i] < dimensions[i].start or ruleset[i] > dimensions[i].end:
                faults.append(i)

        if not faults:
            return True
        else:
            return faults

    def ruleset_to_tensor(self, ruleset):

        num_dim= self.game_class.RULE_SPEC.num_dimensions
        rst = tf.convert_to_tensor(ruleset)
        rst = tf.reshape(rst, (1, num_dim))

        return rst

    def train_suggestion_model(self, lr=0.005, train_samples=1000, validation_samples=100,
                               save_to='trained_model.h5', init_only=False):

        dim = self.game_class.RULE_SPEC.num_dimensions

        model = models.Sequential()

        model.add(layers.Dense(64, activation='sigmoid', input_shape=(dim, )))
        model.add(layers.Dense(32, activation='sigmoid', use_bias=True))

        model.add(layers.Dense(1, activation='sigmoid', use_bias=True))

        opt = tf.optimizers.Adam(learning_rate=lr)
        met = tf.keras.metrics.MeanAbsoluteError()
        loss = tf.losses.MeanAbsoluteError()

        model.compile(optimizer=opt, loss=loss, metrics=[met])
        model.save('storage/models/untrained_model.h5')
        model.summary()

        if not init_only:
            print('Fetching training data...')
            train_data = self.get_samples(train_samples, verbose=True)
            print('Fetching validation data...')
            validation_data = self.get_samples(validation_samples, verbose=True)

            log_dir = "training_logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

            tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

            model.fit(train_data, epochs=10, verbose=1, validation_data=validation_data, callbacks=[tensorboard_callback])

            model.save(save_to)

    def get_samples(self, num=1000, verbose=False, round_to=3):

        samples = np.zeros((num, self.game_class.RULE_SPEC.num_dimensions))
        labels = np.zeros((num, 1))

        if verbose:
            iterator = tqdm(range(num))
        else:
            iterator = range(num)

        for i in iterator:
            rules = self.game_class.RULE_SPEC.generate()
            value = self.monte_ruleset(rules)

            samples[i] = rules
            value = round(value, round_to)
            labels[i] = value

            data = tf.data.Dataset.from_tensor_slices((samples, labels))

        return data.map(self.shape_tensor)

    def continue_training(self, ruleset, value, load_from='trained_model.h5'):

        ruleset = np.reshape(np.asarray(ruleset), (self.game_class.RULE_SPEC.num_dimensions, ))

        if self.first_train:
            train_thresh = 5
            self.first_train = False
        else:
            train_thresh = 25

        INFO_LOGGER.info(f'The current training threshold is {train_thresh} and there are {self.packed_count} stored samples.')

        if self.packed_count == train_thresh:
            INFO_LOGGER.info('Triggered new training sequence...')
            data = tf.data.Dataset.from_tensor_slices((self.packed_samples, self.packed_labels))
            self.packed_count = 0
            data = data.map(self.shape_tensor)

            INFO_LOGGER.info('Attempting to load model...')

            if os.path.isfile(load_from):
                try:
                    model = tf.keras.models.load_model(load_from)
                    INFO_LOGGER.info(f'Loaded model from {load_from}')
                except Exception as e:
                    ERROR_LOGGER.exception(f'Failed to load model from {load_from}')
            else:
                try:
                    model = tf.keras.models.load_model('storage/models/untrained_model.h5')
                    INFO_LOGGER.info(f'Loaded model from storage/models/untrained_model.h5')
                except Exception as e:
                    ERROR_LOGGER.exception(f'Failed to load model from storage/models/untrained_model.h5')

            try:
                model.fit(data, epochs=5, verbose=1)
                INFO_LOGGER.info('Model successfully fit!')
            except Exception as e:
                ERROR_LOGGER.exception(f'Failed to fit model...')

            model.save(load_from)

        else:
            self.packed_samples[self.packed_count] = ruleset
            self.packed_labels[self.packed_count] = value

            INFO_LOGGER.info(f'Successfully stored sample. There are now {self.packed_count+1} samples stored.')

        self.packed_count += 1

    def shape_tensor(self, sample, label):
        sample = tf.reshape(sample, (1, self.game_class.RULE_SPEC.num_dimensions))
        return sample, label

    def careful_explore(self, known_states, epsilon=0.3, steps=10,
                        verbose=False, write_to_file='tests/rule_set.txt', ep_decay_rate=0):
        dimensions = self.game_class.RULE_SPEC.dimensions

        iterator = range(steps)

        if verbose:
            iterator = tqdm(range(steps))

        if verbose:
            print('Now exploring...')

        for i in iterator:
            epsilon -= ep_decay_rate

            if random.uniform(0, 1) < epsilon:
                action = self.game_class.RULE_SPEC.generate()
            else:
                try:
                    action = np.asarray(max(known_states.items(), key=operator.itemgetter(1))[0])
                except ValueError:
                    action = self.game_class.RULE_SPEC.generate()

                num_dims = len(action)
                change = random.randint(0, num_dims-1)

                if dimensions[change].dtype == 'categorical':
                    action[change] = random.choice(list(dimensions[change].categories))
                elif dimensions[change].dtype == 'integer':
                    action[change] = random.randint(dimensions[change].start, dimensions[change].end)
                else:
                    first = True
                    while action[change] < dimensions[change].start or action[change] > dimensions[change].end or first:
                        action[change] += random.uniform(-1,1)
                        first = False

            reward = self.monte_ruleset(action)
            act_tup = tuple(action)
            known_states[act_tup] = reward

        max_info = max(known_states.items(), key=operator.itemgetter(1))

        rule_set = max_info[0]
        value = max_info[1]

        if write_to_file:
            with open(write_to_file, 'w') as file:
                file.write(str(rule_set) + '\n' + str('Objective function value: ' + str(value)))
                file.close()

        return known_states, rule_set, value

    """
    :param rulevector: Numeric vector of the rule space (tuple).
    :param Q: Dictionary {state:reward}
    :param epsilon: exploration rate
    :return: Q — state/action logs (dict) , sprime — the next step to take (tuple), reward — from previous step (float)
    """
    def q_learn(self, rulevector, Q, gamma=0.9, lr=0.75, epsilon=0.3):

        state = tuple(rulevector)

        if random.uniform(0,1) < epsilon:

            action = tuple(self.game_class.RULE_SPEC.generate())
            Q, reward = self.q_update(state, Q, action, gamma, lr)

        else:

            action = self.q_get_max(Q, state)
            Q, reward = self.q_update(state, Q, action, gamma, lr)

        sprime = action

        return Q, sprime, reward

    def q_get_max(self, Q, state):
        try:
            action = max(Q[state].items(), key=operator.itemgetter(1))[0]
        except ValueError:
            # This is the lower bound of the interesting scale.
            max_action = 0

            for state, act in Q.items():
                try:
                    maximum = max(Q[state].items(), key=operator.itemgetter(1))
                except ValueError:
                    maximum = ((1,), -1)
                if maximum[1] > max_action:
                    action = maximum[0]

        except KeyError:
            Q[state] = {}
            action = tuple(self.game_class.RULE_SPEC.generate())

        return action

    def q_update(self, state, Q, action, gamma, lr):
        reward = self.monte_ruleset(action)
        sprime = action

        try:
            maximum = max(Q[sprime].items(), key=operator.itemgetter(1))[1]
        except ValueError:
            maximum = 0
        except KeyError:
            Q[sprime] = {}
            maximum = 0

        try:
            Q[state][action] = Q[state][action] + lr * (reward + gamma * maximum - Q[state][action])
        except KeyError:
            Q[state] = {}
            Q[state][action] = lr * (reward + gamma * maximum)

        return Q, reward
