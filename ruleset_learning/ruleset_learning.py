class RulesetLearner:
    def __init__(self, game_class, objective_function, game_args, game_kwargs, num_frames, num_trials):
        self.game_class = game_class
        self.objective_function = objective_function
        self.game_args = game_args
        self.game_kwargs = game_kwargs
        self.num_frames = num_frames
        self.num_trials = num_trials

    def rulevector2args(self, rulevector):
        raise NotImplementedError("New game not yet implemented!")

    def monte_ruleset(self, rulevector):
        ruleargs, rulekwargs = self.rulevector2args(rulevector)
        outputs = []

        for i in range(self.num_trials):
            game = self.game_class(*self.game_args, *ruleargs, **self.game_kwargs, **rulekwargs)
            game.advances(self.num_frames)
            outputs.append(self.objective_function(game))

        return sum(outputs)/len(outputs)