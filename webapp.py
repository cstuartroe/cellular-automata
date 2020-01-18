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
import logging
from logging import INFO, ERROR
from web.mongo_utils import MongoUtility

EPSILON_START = 0.025
EPSILON_STEP = 0.005
INFO_LOGGER = logging.getLogger('info_logger')
ERROR_LOGGER = logging.getLogger('error_logger')
ERROR_LOGGER.isEnabledFor(ERROR)
FRAMES = 50

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    level=INFO, filename='storage/logs/cellauto.log', filemode='w')


@app.route('/img/<gif_id>.gif')
def get_gif(gif_id):
    filepath = f'storage/images/{gif_id}.gif'
    return send_file(filepath, mimetype='image/gif')


@app.route('/static/img/<filename>')
def get_img(filename):
    try:
        filepath = f'web/static/img/{filename}'
    except FileNotFoundError:
        return 'File Not Found'

    return send_file(filepath, mimetype='image/gif')


@app.route('/static/js/<filename>')
def get_js(filename):
    filepath = f"web/static/js/{filename}"
    return send_file(filepath)


@app.route('/')
def index():
    return send_file("web/index.html")


@app.route('/<anything>')
def react_page(path):
    return send_file("web/index.html")


@app.route('/api/generate_game')
def generate():

    arguments = request.args

    game_name = arguments['game_name']
    r, mu = initialize_game(game_name)

    epsilon = mu.get_epsilon()

    if epsilon > 0.85:
        epsilon = 0.85

    INFO_LOGGER.info(f'Epsilon loaded as {epsilon}.')

    sess_id = random_string()
    file_name = f'storage/images/{game_name}_{sess_id}.gif'

    INFO_LOGGER.info(f'Starting generation sequence for {sess_id}.')
    model_load_from = f'storage/models/{game_name}_model.h5'

    new_test, s, mngf, mxgf = r.training_sample(epsilon=epsilon, load_from=model_load_from, grad_step_scalar=100)

    INFO_LOGGER.info(f'Finished generation sequence for {sess_id}')

    epsilon += EPSILON_STEP

    mu.set_epsilon(epsilon)

    mu.send_sample(mu.sample_to_json(sess_id, game_name=game_name, ruleset=new_test,
                                     grad_steps=s, grad_max=mxgf, grad_min=mngf))

    rule_args, rule_kwargs = RedVsBlue.rulevector2args(new_test)

    conway = RedVsBlue(**rule_kwargs, width=35, height=35, init_alive_prob=0.25)

    con_graphs = RedVsBlueGraphics(conway, as_gif=True, gif_name=file_name)
    con_graphs.run(FRAMES)

    mu.add_game(rule_id=sess_id, game=conway)

    INFO_LOGGER.info(f'Successfully ran {FRAMES} iterations and generated gif.')

    return {'game_id': sess_id, 'grad_steps': s, 'grad_max': mxgf, 'grad_min': mngf}


def random_string(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def initialize_game(game_name):
    if os.path.isfile(f'storage/static/{game_name}_learner.p'):
        try:
            r = pickle.load(open(f"storage/static/{game_name}_learner.p", "rb"))
            INFO_LOGGER.info(f'Successfully loaded {game_name}_learner pickle.')
        except Exception as e:
            ERROR_LOGGER.exception(f'Could not load {game_name}_learner pickle.')

        try:
            with open('storage/static/epsilon_id.txt', 'r') as file:
                ep_id = file.readline()
            mu = MongoUtility(ep_id)
        except FileNotFoundError:
            ERROR_LOGGER.exception('Could not load epsilon id file.')

    else:
        r = RL.RulesetLearner(game_name, sparse_change, game_args=None, game_kwargs=None, num_frames=40, num_trials=5)
        mu = MongoUtility()
        r.train_suggestion_model(init_only=True)
        mu.initialize_epsilon(EPSILON_START)
        with open('storage/static/epsilon_id.txt', 'w+') as file:
            file.write(str(mu.ep_id))
        INFO_LOGGER.info(f'Trained initial model and initialized epsilon to {mu.get_epsilon()}.')

    return r, mu


@app.route('/setep')
def set_ep():
    ep = request.args['epsilon']
    mu = MongoUtility()
    mu.initialize_epsilon(ep)

#
# @app.route('/submit')
# def submit():
#     sess_id = request.args['game_id']
#     game_name = request.args['game_name']
#     rating = int(request.args['rating'])
#     dec_rating = (rating - 1)/4
#
#     mu = MongoUtility()
#
#     num_untrained_samples = mu.get_doc_count(mu.pre_sample_col)
#
#     if num_untrained_samples ==
#
#     INFO_LOGGER.info(f'Starting submit sequence for {sess_id} with rating {rating}')
#
#     try:
#         with open(f'storage/rulesets/{game_name}_{sess_id}.txt', 'r') as file:
#             rule_set = eval(file.read())
#             rule_array = np.asarray(rule_set)
#             INFO_LOGGER.info(f'Successfully loaded {sess_id} txt file.')
#     except Exception as e:
#         ERROR_LOGGER.exception(f'Failed to load {sess_id} txt file.')
#
#     with open(f'storage/rulesets/{game_name}_{sess_id}.txt', 'a') as file:
#         file.write('\n')
#         file.write(str(dec_rating))
#
#     INFO_LOGGER.info('Starting continue training sequence...')
#     model_load_from = f'storage/models/{game_name}_model.h5'
#     INFO_LOGGER.info(f'If necessary, the model will be loaded from {model_load_from}')
#
#     INFO_LOGGER.info('Finished continued training sequence.')
#
#     with open(f'storage/static/{game_name}_learner.p', 'wb') as file:
#         pickle.dump(r, file)
#
#     INFO_LOGGER.info(f'Finished submission sequence for {sess_id}')
#
#     with open("web/thank_you.html", "r") as fh:
#         return fh.read()
# #
#


if __name__ == '__main__':
    app.run()
