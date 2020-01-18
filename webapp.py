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
DUMP_AFTER = 50

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


@app.route('/api/generate_game')
def generate():

    arguments = request.args

    game_name = arguments['game_name']
    game_classes = name_to_class(game_name)

    main_game_class = game_classes[0]
    graphics_class = game_classes[1]

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

    rule_args, rule_kwargs = main_game_class.rulevector2args(new_test)

    conway = main_game_class(**rule_kwargs, width=35, height=35, init_alive_prob=0.25)

    con_graphs = graphics_class(conway, as_gif=True, gif_name=file_name)
    con_graphs.run(FRAMES)

    # mu.add_game(rule_id=sess_id, game=conway)

    INFO_LOGGER.info(f'Successfully ran {FRAMES} iterations and generated gif.')

    return {'game_id': sess_id, 'grad_steps': s, 'grad_max': mxgf, 'grad_min': mngf}


def random_string(string_length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def initialize_game(game_name):

    game_classes = name_to_class(game_name)
    r = RL.RulesetLearner(game_classes[0], '', game_args=None, game_kwargs=None, num_frames=40, num_trials=5)
    mu = MongoUtility()

    if os.path.isfile('storage/static/epsilon_id.txt'):
        try:
            with open('storage/static/epsilon_id.txt', 'r') as file:
                ep_id = file.readline()
            mu = MongoUtility(ep_id)
        except FileNotFoundError:
            ERROR_LOGGER.exception('Could not load epsilon id file.')

    else:
        mu.initialize_epsilon(EPSILON_START)
        with open('storage/static/epsilon_id.txt', 'w+') as file:
            file.write(str(mu.ep_id))

        r.train_suggestion_model(init_only=True)
        INFO_LOGGER.info(f'Trained initial model and initialized epsilon to {mu.get_epsilon()}.')

    return r, mu


@app.route('/setep')
def set_ep():
    ep = request.args['epsilon']
    mu = MongoUtility()
    mu.initialize_epsilon(ep)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return send_file("web/index.html")


@app.route('/submit', methods=['GET', 'POST'])
def submit():

    INFO_LOGGER.info(str(request.args))

    sess_id = request.args['game_id']
    game_name = request.args['game_name']
    rating = int(request.args['rating'])

    dec_rating = (rating - 1)/4

    INFO_LOGGER.info(f'Starting submit sequence for {sess_id} with rating {rating}')

    mu = MongoUtility()

    num_untrained_samples = mu.count_by_name(game_name)

    if num_untrained_samples >= DUMP_AFTER:
        INFO_LOGGER.info(f'New training started for {game_name} on {num_untrained_samples} samples...')
        mu.dump_and_train(game_name)

    mu.update_rating(sess_id, dec_rating)

    INFO_LOGGER.info(f'Finished submission sequence for {sess_id}')

    return ''


if __name__ == '__main__':
    app.run()
