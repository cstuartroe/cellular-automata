import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link, Switch } from "react-router-dom";
import ReactDOM from "react-dom";

import "../static/scss/main.scss";

class App extends Component {
  state = {
  };

  render() {
    return (
      <Router>
          <Switch>
            <Route exact={true} path="/thank_you" render={() => (
              <div className="main">
                <h1>Thank you!</h1>
                <a id="another" href="/">Do another?</a>
                <br/>
                <br/>
                <img src="/static/img/thankyou.jpg" alt="Thanks" height="500" width="700"/>
              </div>
            )} />

            <Route exact={true} path="/" render={() => (
              <div>
                <p>You've heard of Hot or Not, now get ready for...</p>
                <h1>Biota or Nada?</h1>
                <h2>Does this gif look more like structured life or a staticky TV?</h2>
                <img src="/img/###.gif"/>
                <p>##MLS##</p>

                <form action="/submit" id="rate">
                    <input type="hidden" name="id" value="###"/>
                    <input type="radio" name="rating" value="1"/> 0% interesting (aka 100% LAME)
                    <br/>
                    <input type="radio" name="rating" value="2"/> 25% interesting
                    <br/>
                    <input type="radio" name="rating" value="3"/> 50% interesting
                    <br/>
                    <input type="radio" name="rating" value="4"/> 75% interesting
                    <br/>
                    <input type="radio" name="rating" value="5"/> 100% interesting &#x1F3C4; &#x1F3B8;
                </form>

                <br/>
                <button className="rate_button" type="submit" form="rate" value="Submit">Submit</button>
                <br/>
                <br/>
                <p>Created by Conor Stuart-Roe and Kristian Gaylord</p>
                <p id="grad_scale">The maximum gradient scalar was ##MXG##, and the minimum ##MNG##</p>
              </div>
            )} />

            <Route exact={false} path="" render={() => (
              <p>Unknown page.</p>
            )} />
          </Switch>
      </Router>
    );
  }
}

const wrapper = document.getElementById("app");
wrapper ? ReactDOM.render(<App />, wrapper) : null;