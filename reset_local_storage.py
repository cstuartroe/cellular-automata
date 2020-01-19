import os

game_names = ['Conway', 'Rhomdos', 'RedVsBlue']

for directory in os.listdir('storage'):
    if '.DS' not in directory and 'images' not in directory:
        for file in os.listdir(f'storage/{directory}'):
            os.remove(f'storage/{directory}/{file}')

for directory in os.listdir('storage/images'):
    if '.DS' not in directory:
        for file in os.listdir(f'storage/images/{directory}'):
            if 'none' not in file:
                os.remove(f'storage/images/{directory}/{file}')