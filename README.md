# Cellular Automata

This project was developed to crowdsourced reinforcement learning to identify cellular automata rulesets that appear 
to mimic organic growth. We currently have three families of cellular automaton games - Conway, RedVsBlue, and Rhomdos - each 
of which has a corresponding space of rulesets that determines how the states of cells interact. For each game, volunteers 
can rate generated rulesets (www.biotaornada.com) to help inform our machine learning model about what types of rulesets 
look interesting or organic.

## Humans Wanted

Our machine learning models (found in the `ruleset_learning.py` python file) are continuously trained by human feedback on our
website (linked above). Eventually, once we have aggregated enough data to be effective, we will be adding a convolutional
neural network which we hope to use for the purpose of automatically scoring rulsets as "interesting" or not. This step of 
automation will allow for drastic acceleration in our ability to develop, test, and search for optimal rulesets in a variety
of cellular automata games. 

## Run 

We don't currently have a simple, well documented way to run our code locally on your own machine. We're working on tidying
up some of our core classes and wrapping them into simple examples that can be continued to be developed by others. In the 
meantime, we recommend interacting with the experiment on our website. 
