import argparse
import numpy as np

from games import Conway, ProbabilisticConway, Rhomdos
from graphics import ConwayGraphics, RhomdosRender

parser = argparse.ArgumentParser(description='Demonstrate some cellular automata rulesets.')
parser.add_argument('ruleset', choices=("deterministic", "probabilistic"),
                    help='Which type of ruleset to use')
parser.add_argument('dimensionality', choices=("conway", "rhomdos"),
                    help='Which type of game grid to use')

if __name__ == "__main__":
    args = parser.parse_args()

    if args.dimensionality == "conway":
        if args.ruleset == "deterministic":
            game = Conway(width=100, height=80, init_alive_prob=.25)
        else:
            game = ProbabilisticConway(width=100, height=80, init_alive_prob=0,
                                       survive=np.array([.01, .01, .99, .99, .01, .01, .01, .01, .01]),
                                       spawn=np.array([.01, .01, .01, .99, .01, .01, .01, .01, .01]))
        app = ConwayGraphics(game)

    else:
        if args.ruleset == "deterministic":
            game = Rhomdos(15, 15, 15, survive=[2, 3, 4], spawn=[4], init_alive_prob=.25)
        else:
            raise NotImplementedError("Probabilistic rhomdos not yet implemented!")
        app = RhomdosRender(game)

    app.run()
