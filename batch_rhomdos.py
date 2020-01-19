from webapp import random_string, initialize_game, EPSILON_STEP
import logging
from logging import ERROR
from games import Rhomdos, RhomdosRender
import os

INFO_LOGGER = logging.getLogger('info_logger')
ERROR_LOGGER = logging.getLogger('error_logger')
ERROR_LOGGER.isEnabledFor(ERROR)

game_kwargs = {'width': 12, 'height': 12, 'depth': 12, 'init_alive_prob': 0.25}
r, mu = initialize_game('Rhomdos', game_kwargs=game_kwargs)
game_name = 'Rhomdos'
model_load_from = f'storage/models/{game_name}_model.h5'


if __name__ == '__main__':

    image_files = os.listdir('storage/3D')

    for file in image_files:
        os.remove(f'storage/3D/{file}')

    epsilon = float(mu.get_epsilon(game_name))

    if epsilon > 0.85:
        epsilon = 0.85

    sess_id = random_string()

    new_test, s, mngf, mxgf = r.training_sample(epsilon=epsilon, load_from=model_load_from, grad_step_scalar=100)

    epsilon += EPSILON_STEP

    mu.set_epsilon(epsilon, game_name)

    mu.send_sample(mu.sample_to_json(sess_id, game_name=game_name, ruleset=new_test,
                                     grad_steps=s, grad_max=mxgf, grad_min=mngf))

    rule_args, rule_kwargs = Rhomdos.rulevector2args(new_test)
    game_render = Rhomdos(**rule_kwargs, width=12, height=12, depth=12, init_alive_prob=0.25)
    app = RhomdosRender(game_render, storage_path=f'storage/3D/{sess_id}', duration=10, as_gif=True,
                           gif_name=f'storage/images/Rhomdos_{sess_id}.gif')
    app.run()

    mu.add_game(sess_id, game_render)




