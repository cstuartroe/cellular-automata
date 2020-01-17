import numpy as np
import glob
import pickle
import os
import logging
import argparse

parser = argparse.ArgumentParser(description='Controls whether to just prune, or to prune and train.')
parser.add_argument('function', choices=("p", "pt"), help='Whether to prune, or prune and train.')

if __name__ == '__main__':

    args = parser.parse_args()

    ERROR_LOGGER = logging.getLogger('error_logger')

    GAME_NAME = 'RedVsBlue'
    r = pickle.load(open(f"storage/pickles/{GAME_NAME}_learner.p", "rb"))

    file_names = glob.glob('storage/rulesets/*.txt')

    data = []
    offenders = []

    print('Executing!!!!')

    for path in file_names:
        with open(path, 'r') as file:
            try:
                ruleset = np.asarray(eval(file.readline()))
            except SyntaxError:
                os.remove(path)
            try:
                result = eval(file.readline())
                data.append((ruleset, result))
            except SyntaxError:
                os.remove(path)
                offenders.append(path.split('_')[1].split('.')[0])

    for bad in offenders:
        gme = f'storage/games/{GAME_NAME}_{bad}.p'
        img = f'storage/images/{GAME_NAME}_{bad}.gif'

        try:
            os.remove(gme)
        except Exception as e:
            ERROR_LOGGER.exception(f'Could not remove {gme}')

        try:
            os.remove(img)
        except Exception as e:
            ERROR_LOGGER.exception(f'Could not remove {img}')

    if args.function == 'pt':
        print('TRAINING')
        for d in data:
            r.continue_training(ruleset=d[0], value=d[1], load_from=f'storage/models/{GAME_NAME}_model.h5')

        with open(f'storage/pickles/{GAME_NAME}_learner.p', 'wb') as file:
            pickle.dump(r, file)