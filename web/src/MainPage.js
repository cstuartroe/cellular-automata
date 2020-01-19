import React, { Component } from "react";
import ReactDOM from "react-dom";

class MainPage extends Component {
    render() {
      return(
        <div className="container">
          <div className="row">
            <p>Biota or Nada is a project kicked off in early 2020 to use crowdsourced
              reinforcement learning to identify cellular automata rulesets that appear to mimic organic growth.
              We currently have three families of cellular automaton games - Conway, RedVsBlue, and Rhomdos -
              each of which has a corresponding space of rulesets that determines how the states of cells interact.
              For each game, volunteers can rate generated rulesets to help inform our machine learning model
              about what types of rulesets look interesting or organic.
            </p>
          </div>

          <div className="row gif-row">
            <div className="col-12 col-md-6">
              <img src="/static/img/rhomdos.gif"/>
            </div>
            <div className="col-6 col-md-3">
              <img src="/static/img/bars.gif"/>
              <br/>
              <img src="/static/img/drip.gif"/>
            </div>
            <div className="col-6 col-md-3">
              <img src="/static/img/grill.gif"/>
              <br/>
              <img src="/static/img/solid.gif"/>
            </div>
          </div>

          <div className="row">
            <p>
              To explore ruleset spaces, we developed an algorithm we call DeepExplore, which uses a feed-forward
              neural network to learn correspondences between high-dimensional rulesets and an objective function,
              such as volunteer ratings. To generate new rulesets, a random point in the ruleset space is initially
              chosen, followed by zero or more steps of gradient descent over the input, in which the input is altered
              according to what the current model believes will maximize the objective function, before the actual output
              is collected and used to train the model. A variable {"\u03F5"}, that gradually increases as the model
              improves, determines the likelihood that more steps of gradient descent are applied to the input; for the
              first several hundred inputs collected, gradient descent will never be applied. We believe that DeepExplore
              is well-suited to machine learning problems with a sparse, non-monotonic input space and a significant
              cost for collecting supervised input-output pairs.
            </p>
          </div>
        </div>
      )

    }
}

export default MainPage;