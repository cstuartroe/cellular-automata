import numpy as np
import random
import operator


class RulesetLearner:
    def __init__(self, game_class, objective_function, game_args, game_kwargs, num_frames, num_trials):
        self.game_class = game_class
        self.objective_function = objective_function
        self.game_args = game_args
        self.game_kwargs = game_kwargs
        self.num_frames = num_frames
        self.num_trials = num_trials

    def monte_ruleset(self, rulevector):
        ruleargs, rulekwargs = self.game_class.rulevector2args(rulevector)
        outputs = []

        for i in range(self.num_trials):
            game = self.game_class(*self.game_args, *ruleargs, **self.game_kwargs, **rulekwargs)
            game.advances(self.num_frames)
            outputs.append(self.objective_function(game))

        return sum(outputs)/len(outputs)

    def careful_explore(self, known_states, epsilon=0.3, steps=10):

        dimensions = self.game_class.RULE_SPEC.dimensions

        for i in range(steps):
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
                    while action[change] < dimensions[change].start or action[change] > dimensions[change].end:
                        action[change] += random.uniform(-1,1)

            reward = self.monte_ruleset(action)
            act_tup = tuple(action)
            known_states[act_tup] = reward

        return known_states

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
