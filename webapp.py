from flask import Flask, request, send_file
import random
import string
import ruleset_learning as RL
import os
import logging
from logging import INFO, ERROR
from web.mongo_utils import MongoUtility
from games import name_to_class


app = Flask(__name__)

EPSILON_START = -3
EPSILON_STEP = 0.005
INFO_LOGGER = logging.getLogger('info_logger')
ERROR_LOGGER = logging.getLogger('error_logger')
ERROR_LOGGER.isEnabledFor(ERROR)
FRAMES = 50

DUMP_AFTER = {'Conway': 5, 'RedVsBlue': 5, 'Rhomdos': 5}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    level=INFO, filename='storage/logs/cellauto.log', filemode='w')


@app.route('/img/<gif_id>.gif')
def get_gif(gif_id):
    game_name = gif_id.split('_')[0]
    filepath = f'storage/images/{game_name}/{gif_id}.gif'
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


@app.route('/api/generate_game')
def generate():

    arguments = request.args

    game_name = arguments['game_name']
    game_classes = name_to_class(game_name)

    main_game_class = game_classes[0]
    graphics_class = game_classes[1]

    r, mu = initialize_game(game_name)

    epsilon = float(mu.get_epsilon(game_name))

    if epsilon > 0.85:
        epsilon = 0.85

    INFO_LOGGER.info(f'Epsilon loaded as {epsilon}.')

    sess_id = random_string()
    file_name = f'storage/images/{game_name}/{game_name}_{sess_id}.gif'

    INFO_LOGGER.info(f'Starting generation sequence for {sess_id}.')
    model_load_from = f'storage/models/{game_name}_model.h5'

    new_test, s, mngf, mxgf = r.training_sample(epsilon=epsilon, load_from=model_load_from, grad_step_scalar=100)

    INFO_LOGGER.info(f'Finished generation sequence for {sess_id}')

    epsilon += EPSILON_STEP

    mu.set_epsilon(epsilon, game_name)

    mu.send_sample(mu.sample_to_json(sess_id, game_name=game_name, ruleset=new_test,
                                     grad_steps=s, grad_max=mxgf, grad_min=mngf))

    rule_args, rule_kwargs = main_game_class.rulevector2args(new_test)

    if game_name == 'RedVsBlue':
        game_render = main_game_class(**rule_kwargs, width=35, height=35, init_alive_prob=0.25)
        graphs = graphics_class(game_render, as_gif=True, gif_name=file_name)
        graphs.run(FRAMES)
        mu.add_game(rule_id=sess_id, game=game_render)

    elif game_name == 'Conway':
        game_render = main_game_class(**rule_kwargs, width=35, height=35, init_alive_prob=0.25)
        graphs = graphics_class(game_render, as_gif=True, gif_name=file_name)
        graphs.run(FRAMES)
        mu.add_game(rule_id=sess_id, game=game_render)

    elif game_name == 'Rhomdos':

        count = 0
        unique = False
        image_files = os.listdir('storage/images/Rhomdos')
        file_path = 'none'

        if len(image_files) <= 1:
            unique = True
            sess_id = 'none'
            s = 0
            mxgf = 0
            mngf = 0

        else:
            while not unique and count < 50:

                while 'none' in file_path:
                    file_path = random.choice(image_files)
                    count += 1

                sess_id = file_path.split('_')[1].split('.')[0]

                try:
                    info = mu.get_rhomdos_info(sess_id)
                    if info[3] < 0:
                        unique = True

                    s = info[0]
                    mxgf = info[1]
                    mngf = info[2]
                    count += 1
                except TypeError:
                    s = 0
                    mxgf = 0
                    mngf = 0
                    unique = True

        if count >= 40:
            sess_id = 'none'
            s = 0
            mxgf = 0
            mngf = 0

    INFO_LOGGER.info(f'Successfully ran {FRAMES} iterations and generated gif.')

    return {'game_id': sess_id, 'grad_steps': s, 'grad_max': mxgf, 'grad_min': mngf}


def random_string(string_length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def initialize_game(game_name, game_kwargs=None):

    game_classes = name_to_class(game_name)
    r = RL.RulesetLearner(game_classes[0], '', game_args=None, game_kwargs=game_kwargs, num_frames=40, num_trials=5)
    mu = MongoUtility()

    if os.path.isfile(f'storage/static/{game_name}_ep_id.txt'):
        try:
            with open(f'storage/static/{game_name}_ep_id.txt', 'r') as file:
                ep_id = file.readline()
            mu = MongoUtility(game_name, ep_id)
        except FileNotFoundError:
            ERROR_LOGGER.exception('Could not load epsilon id file.')

    else:
        mu.initialize_epsilon(EPSILON_START, game_name)
        with open(f'storage/static/{game_name}_ep_id.txt', 'w+') as file:
            file.write(str(mu.ep_id[game_name]))

        r.train_suggestion_model(init_only=True)
        INFO_LOGGER.info(f'Trained initial model and initialized epsilon to {mu.get_epsilon(game_name)}.')

    return r, mu


@app.route('/setep')
def set_ep():
    ep = request.args['epsilon']
    name = request.args['game_name']
    mu = MongoUtility()
    mu.initialize_epsilon(ep, game_name=name)

    return 'True'


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return send_file("web/index.html")


@app.route('/submit', methods=['GET', 'POST'])
def submit():

    INFO_LOGGER.info('The incoming string!!: ' + str(request.form))

    sess_id = request.form['game_id']
    game_name = request.form['game_name']
    rating = int(request.form['rating'])

    dec_rating = (rating)/4

    INFO_LOGGER.info(f'Starting submit sequence for {sess_id} with rating {rating}')

    mu = MongoUtility()

    mu.update_rating(sess_id, dec_rating)
    mu.prune_samples()

    num_untrained_samples = mu.count_by_name(game_name)

    if num_untrained_samples >= DUMP_AFTER[game_name]:
        INFO_LOGGER.info(f'New training started for {game_name} on {num_untrained_samples} samples...')
        DUMP_AFTER[game_name] = mu.dump_and_train(game_name, DUMP_AFTER[game_name])

    INFO_LOGGER.info(f'Finished submission sequence for {sess_id}')

    return ''


if __name__ == '__main__':
    app.run()
