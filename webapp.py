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


GAME_NAME = 'RedVsBlue'
EPSILON_START = 0.025
EPSILON_STEP = 0.005
INFO_LOGGER = logging.getLogger('info_logger')
ERROR_LOGGER = logging.getLogger('error_logger')
ERROR_LOGGER.isEnabledFor(ERROR)
FRAMES = 50

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    level=INFO, filename='storage/logs/cellauto.log', filemode='w')


def random_string(stringLength=5):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


if os.path.isfile(f'storage/pickles/{GAME_NAME}_learner.p'):
    try:
        r = pickle.load(open(f"storage/pickles/{GAME_NAME}_learner.p", "rb"))
        INFO_LOGGER.info(f'Successfully loaded {GAME_NAME}_learner pickle.')
    except Exception as e:
        ERROR_LOGGER.exception(f'Could not load {GAME_NAME}_learner pickle.')

else:
    r = RL.RulesetLearner(RedVsBlue, sparse_change, game_args=None, game_kwargs=None, num_frames=40, num_trials=5)
    r.train_suggestion_model(init_only=True)
    with open('storage/epsilon.txt', 'w+') as file:
        file.write(str(EPSILON_START))
    INFO_LOGGER.info(f'Trained initial model and initialized epsilon to {EPSILON_START}.')

@app.route('/')
def rate_ruleset():

    with open('storage/epsilon.txt', 'r') as file:
        epsilon = eval(file.read())
        INFO_LOGGER.info(f'Epsilon loaded as {epsilon}.')

    sess_id = random_string()
    file_name = f'storage/images/{GAME_NAME}_{sess_id}.gif'

    INFO_LOGGER.info(f'Starting generation sequence for {sess_id}.')
    model_load_from = f'storage/models/{GAME_NAME}_model.h5'

    new_test, s, mngf, mxgf = r.training_sample(epsilon=epsilon, load_from=model_load_from)

    INFO_LOGGER.info(f'Finished generation sequence for {sess_id}')

    epsilon += EPSILON_STEP

    with open('storage/epsilon.txt', 'w') as file:
        file.write(str(epsilon))

    with open(f'storage/rulesets/{GAME_NAME}_{sess_id}.txt', 'w') as file:
        file.write(str(list(new_test)))

    rule_args, rule_kwargs = RedVsBlue.rulevector2args(new_test)

    conway = RedVsBlue(**rule_kwargs, width=35, height=35, init_alive_prob=0.25)

    con_graphs = RedVsBlueGraphics(conway, as_gif=True, gif_name=file_name)
    con_graphs.run(FRAMES)
    INFO_LOGGER.info(f'Successfully ran {FRAMES} iterations and generated gif.')

    with open(f'storage/games/{GAME_NAME}_{sess_id}.p', 'wb') as file:
        pickle.dump(conway, file)

    if s > 0:
        ai_message = f'This image was generated with artificial intelligence, using {s} gradient steps.'
    else:
        ai_message = 'This is a randomly generated image, out of an infinite number of possibilities.'

    with open("web/rate_ruleset.html", "r") as fh:
        return (fh.read().replace('###', sess_id)).replace('##MLS##', ai_message)\
            .replace('##MXG##', str(mxgf)).replace('##MNG##', str(mngf))


@app.route('/submit')
def submit():
    sess_id = request.args['id']
    rating = int(request.args['rating'])

    INFO_LOGGER.info(f'Starting submit sequence for {sess_id} with rating {rating}')

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

    try:
        with open(f'storage/rulesets/{GAME_NAME}_{sess_id}.txt', 'r') as file:
            rule_set = eval(file.read())
            rule_array = np.asarray(rule_set)
            INFO_LOGGER.info(f'Successfully loaded {sess_id} txt file.')
    except Exception as e:
        ERROR_LOGGER.exception(f'Failed to load {sess_id} txt file.')

    with open(f'storage/rulesets/{GAME_NAME}_{sess_id}.txt', 'a') as file:
        file.write('\n')
        file.write(str(dec_rating))

    INFO_LOGGER.info('Starting continue training sequence...')
    model_load_from = f'storage/models/{GAME_NAME}_model.h5'
    INFO_LOGGER.info(f'If necessary, the model will be loaded from {model_load_from}')

    r.continue_training(ruleset=rule_array, value=dec_rating, load_from=model_load_from)
    INFO_LOGGER.info('Finished continued training sequence.')

    with open(f'storage/pickles/{GAME_NAME}_learner.p', 'wb') as file:
        pickle.dump(r, file)

    INFO_LOGGER.info(f'Finished submission sequence for {sess_id}')

    return 'Thank you! <a href="/">Do another?</a>'


@app.route('/img/<gif_id>.gif')
def get_gif(gif_id):
    file_name = f'storage/images/{GAME_NAME}_{gif_id}.gif'
    return send_file(file_name, mimetype='image/gif')


if __name__ == '__main__':
    app.run()
