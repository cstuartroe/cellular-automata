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
from web.mongo_utils import Mongo_Utility


GAME_NAME = 'RedVsBlue'
EPSILON_START = 0.025
EPSILON_STEP = 0.005
INFO_LOGGER = logging.getLogger('info_logger')
ERROR_LOGGER = logging.getLogger('error_logger')
ERROR_LOGGER.isEnabledFor(ERROR)
FRAMES = 50


@app.route('/img/<gif_id>.gif')
def get_gif(gif_id):
    filepath = f'storage/images/{gif_id}.gif'
    return send_file(filepath, mimetype='image/gif')


@app.route('/static/img/<filename>')
def get_img(filename):
    filepath = f'web/static/img/{filename}'
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


# def random_string(stringLength=8):
#     letters = string.ascii_lowercase
#     return ''.join(random.choice(letters) for i in range(stringLength))
#
#
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
#                     level=INFO, filename='storage/logs/cellauto.log', filemode='w')
#
# if os.path.isfile(f'storage/static/{GAME_NAME}_learner.p'):
#     try:
#         r = pickle.load(open(f"storage/static/{GAME_NAME}_learner.p", "rb"))
#         INFO_LOGGER.info(f'Successfully loaded {GAME_NAME}_learner pickle.')
#     except Exception as e:
#         ERROR_LOGGER.exception(f'Could not load {GAME_NAME}_learner pickle.')
#
#     try:
#         with open('storage/static/epsilon_id.txt', 'r') as file:
#             ep_id = file.readline()
#         mu = Mongo_Utility(ep_id)
#     except FileNotFoundError:
#         ERROR_LOGGER.exception('Could not load epsilon id file.')
#
# else:
#     r = RL.RulesetLearner(RedVsBlue, sparse_change, game_args=None, game_kwargs=None, num_frames=40, num_trials=5)
#     mu = Mongo_Utility()
#     r.train_suggestion_model(init_only=True)
#     mu.initialize_epsilon(EPSILON_START)
#     with open('storage/static/epsilon_id.txt', 'w+') as file:
#         file.write(str(mu.ep_id))
#     INFO_LOGGER.info(f'Trained initial model and initialized epsilon to {mu.get_epsilon()}.')
#
#
# @app.route('/')
# def rate_ruleset():
#
#     epsilon = mu.get_epsilon()
#
#     if epsilon > 0.85:
#         epsilon = 0.85
#
#     INFO_LOGGER.info(f'Epsilon loaded as {epsilon}.')
#
#     sess_id = random_string()
#     file_name = f'storage/images/{GAME_NAME}_{sess_id}.gif'
#
#     INFO_LOGGER.info(f'Starting generation sequence for {sess_id}.')
#     model_load_from = f'storage/models/{GAME_NAME}_model.h5'
#
#     new_test, s, mngf, mxgf = r.training_sample(epsilon=epsilon, load_from=model_load_from, grad_step_scalar=100)
#
#     INFO_LOGGER.info(f'Finished generation sequence for {sess_id}')
#
#     epsilon += EPSILON_STEP
#
#     mu.set_epsilon(epsilon)
#
#     with open(f'storage/rulesets/{GAME_NAME}_{sess_id}.txt', 'w') as file:
#         file.write(str(list(new_test)))
#
#     rule_args, rule_kwargs = RedVsBlue.rulevector2args(new_test)
#
#     conway = RedVsBlue(**rule_kwargs, width=35, height=35, init_alive_prob=0.25)
#
#     con_graphs = RedVsBlueGraphics(conway, as_gif=True, gif_name=file_name)
#     con_graphs.run(FRAMES)
#     INFO_LOGGER.info(f'Successfully ran {FRAMES} iterations and generated gif.')
#
#     with open(f'storage/games/{GAME_NAME}_{sess_id}.p', 'wb') as file:
#         pickle.dump(conway, file)
#
#     if s > 0:
#         ai_message = f'This image was generated with artificial intelligence, using {s} gradient steps.'
#     else:
#         ai_message = 'This is a randomly generated image, out of an infinite number of possibilities.'
#
#     with open("web/rate_ruleset.html", "r") as fh:
#         return (fh.read().replace('###', sess_id)).replace('##MLS##', ai_message)\
#             .replace('##MXG##', str(mxgf)).replace('##MNG##', str(mngf))
#
#
# @app.route('/submit')
# def submit():
#     sess_id = request.args['id']
#     rating = int(request.args['rating'])
#     dec_rating = (rating - 1)/4
#
#     INFO_LOGGER.info(f'Starting submit sequence for {sess_id} with rating {rating}')
#
#     try:
#         with open(f'storage/rulesets/{GAME_NAME}_{sess_id}.txt', 'r') as file:
#             rule_set = eval(file.read())
#             rule_array = np.asarray(rule_set)
#             INFO_LOGGER.info(f'Successfully loaded {sess_id} txt file.')
#     except Exception as e:
#         ERROR_LOGGER.exception(f'Failed to load {sess_id} txt file.')
#
#     with open(f'storage/rulesets/{GAME_NAME}_{sess_id}.txt', 'a') as file:
#         file.write('\n')
#         file.write(str(dec_rating))
#
#     INFO_LOGGER.info('Starting continue training sequence...')
#     model_load_from = f'storage/models/{GAME_NAME}_model.h5'
#     INFO_LOGGER.info(f'If necessary, the model will be loaded from {model_load_from}')
#
#     r.continue_training(ruleset=rule_array, value=dec_rating, load_from=model_load_from)
#     INFO_LOGGER.info('Finished continued training sequence.')
#
#     with open(f'storage/static/{GAME_NAME}_learner.p', 'wb') as file:
#         pickle.dump(r, file)
#
#     INFO_LOGGER.info(f'Finished submission sequence for {sess_id}')
#
#     with open("web/thank_you.html", "r") as fh:
#         return fh.read()
#
#
# @app.route('/setep')
# def set_ep():
#     ep = request.args['epsilon']
#     mu.set_epsilon(ep)


if __name__ == '__main__':
    app.run()
