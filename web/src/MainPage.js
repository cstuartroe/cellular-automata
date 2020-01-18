import React, { Component } from "react";
import ReactDOM from "react-dom";

class MainPage extends Component {
    render() {
      return(
        <div className="container">
          <div className="row">
            <p style={{padding: "5vh"}}>Biota or Nada is a project kicked off in early 2020 to use crowdsourced
              reinforcement learning to identify cellular automata rulesets that appear to mimic organic growth.</p>
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
        </div>
      )

    }
}

export default MainPage;