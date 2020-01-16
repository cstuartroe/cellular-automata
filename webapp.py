from flask import Flask, request, send_file
app = Flask(__name__)
import random
import string
import ruleset_learning as RL
from games import RedVsBlue
from metrics.game_metrics import *
import os
import pickle
from graphics import RedVsBlueGraphics
import numpy as np

GAME_NAME = 'RedVsBlue'
EPSILON_START = -1
EPSILON_STEP = 0.005


def random_string(stringLength=5):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


if os.path.isfile(f'storage/pickles/{GAME_NAME}_learner.p'):
    r = pickle.load(open(f"storage/pickles/{GAME_NAME}_learner.p", "rb"))
else:
    r = RL.RulesetLearner(RedVsBlue, sparse_change, game_args=None, game_kwargs=None, num_frames=40, num_trials=5)
    r.train_suggestion_model(init_only=True)
    with open('storage/epsilon.txt', 'w+') as file:
        file.write(str(EPSILON_START))

@app.route('/')
def rate_ruleset():

    with open('storage/epsilon.txt', 'r') as file:
        epsilon = eval(file.read())

    sess_id = random_string()
    file_name = f'storage/images/{GAME_NAME}_{sess_id}.gif'
    new_test = r.training_sample(epsilon=epsilon)

    epsilon += EPSILON_STEP

    with open('storage/epsilon.txt', 'w') as file:
        file.write(str(epsilon))

    with open(f'storage/rulesets/{GAME_NAME}_{sess_id}.txt', 'w') as file:
        file.write(str(list(new_test)))

    rule_args, rule_kwargs = RedVsBlue.rulevector2args(new_test)

    conway = RedVsBlue(**rule_kwargs, width=35, height=35, init_alive_prob=0.25)

    con_graphs = RedVsBlueGraphics(conway, as_gif=True, gif_name=file_name)
    con_graphs.run(5)

    with open(f'storage/games/{GAME_NAME}_{sess_id}.p', 'wb') as file:
        pickle.dump(conway, file)

    with open("web/rate_ruleset.html", "r") as fh:
        return fh.read().replace('###', sess_id)


@app.route('/submit')
def submit():
    sess_id = request.args['id']
    rating = int(request.args['rating'])

    if rating == 1:
        dec_rating = 0.
    elif rating == 2:
        dec_rating = 0.25
    elif rating == 3:
        dec_rating = 0.5
    elif rating == 4:
        dec_rating = 0.75
    elif rating == 5:
        dec_rating = 1.

    with open(f'storage/rulesets/{GAME_NAME}_{sess_id}.txt', 'r') as file:
        rule_set = eval(file.read())
        rule_array = np.asarray(rule_set)

    with open(f'storage/rulesets/{GAME_NAME}_{sess_id}.txt', 'a') as file:
        file.write('\n')
        file.write(str(dec_rating))

    r.continue_training(ruleset=rule_array, value=dec_rating, load_from=f'storage/models/{GAME_NAME}_model.h5')

    with open(f'storage/pickles/{GAME_NAME}_learner.p', 'wb') as file:
        pickle.dump(r, file)

    return 'Thank you! <a href="/">Do another?</a>'


@app.route('/img/<gif_id>.gif')
def get_gif(gif_id):
    file_name = f'storage/images/{GAME_NAME}_{gif_id}.gif'
    return send_file(file_name, mimetype='image/gif')


if __name__ == '__main__':
    app.run()
