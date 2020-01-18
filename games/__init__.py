from .game import Spec, Game
from .conway import Conway, ProbabilisticConway
from .red_vs_blue import RedVsBlue
from .rhomdos import Rhomdos
from graphics import ConwayGraphics, RedVsBlueGraphics, RhomdosRender


def name_to_class(game_name):
    class_mapping = {'Conway': ProbabilisticConway, 'RedVsBlue': RedVsBlue, 'Rhomdos': Rhomdos}
    graphics_mapping = {'Conway': ConwayGraphics, 'RedVsBlue': RedVsBlueGraphics, 'Rhomdos': RhomdosRender}
    return class_mapping[game_name], graphics_mapping[game_name]
