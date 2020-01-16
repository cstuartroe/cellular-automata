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


def random_string(stringLength=5):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


if os.path.isfile('storage/pickles/web_learner.p'):
    r = pickle.load(open("storage/pickles/web_learner.p", "rb"))
else:
    r = RL.RulesetLearner(RedVsBlue, sparse_change, game_args=None, game_kwargs=None, num_frames=40, num_trials=5)

class StoreID():
    def __init__(self, id):
        self.id = ''

@app.route('/')
def rate_ruleset():
    id = random_string()
    file_name = f'storage/images/{id}.gif'
    new_test = r.training_sample(epsilon=-2)

    with open(f'storage/rulesets/{id}.txt', 'w') as file:
        file.write(str(list(new_test)))

    rule_args, rule_kwargs = RedVsBlue.rulevector2args(new_test)

    conway = RedVsBlue(**rule_kwargs, width=50, height=50, init_alive_prob=0.25)
    con_graphs = RedVsBlueGraphics(conway, as_gif=True, gif_name=file_name)
    con_graphs.run(5)

    with open("web/rate_ruleset.html", "r") as fh:
        return fh.read().replace('###', id)


@app.route('/submit')
def submit():
    id = request.args['id']
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

    with open(f'storage/rulesets/{id}.txt', 'r') as file:
        rule_set = eval(file.read())
        rule_array = np.asarray(rule_set)

    r.continue_training(ruleset=rule_array, value=dec_rating, load_from='storage/models/prob_conway_web.h5')

    with open('storage/pickles/web_learner.p', 'wb') as file:
        pickle.dump(r, file)

    return 'Thank you! <a href="/">Do another?</a>'


@app.route('/img/<gif_id>.gif')
def get_gif(gif_id):
    file_name = f'storage/images/{gif_id}.gif'
    return send_file(file_name, mimetype='image/gif')


if __name__ == '__main__':
    app.run()
