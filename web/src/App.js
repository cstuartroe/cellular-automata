import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link, Switch } from "react-router-dom";
import ReactDOM from "react-dom";

import MainPage from "./MainPage.js";
import RatePage from "./RatePage.js";
import ThankYouPage from "./ThankYouPage.js";

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import "../static/scss/main.scss";

const games = ["Conway", "RedVsBlue", "Rhomdos"];


class App extends Component {
  render() {
    return (
      <Router>
        <div style={{position: "absolute", right: 0, top: 0}}>
          <a><FontAwesomeIcon icon="fab-github" /></a>
        </div>

        <p>You've heard of Hot or Not, now get ready for...</p>
        <Link to="/"><h1>Biota or Nada?</h1></Link>

        <div className="container header">
          <div className="row">
            {games.map((game, index) => (
              <div className="col-4" key={index}>
                <Link to={"/" + game}><h3>{game}</h3></Link>
              </div>
            ))}
          </div>
        </div>

        <Switch>
          <Route exact={true} path="/" render={() => (
            <MainPage/>
          )} />

          <Route exact={true} path="/:game_name/rate" render={({match}) => (
            <RatePage game_name={match.params.game_name}/>
          )} />

          <Route exact={true} path="/:game_name/thanks" render={({match}) => (
            <ThankYouPage game_name={match.params.game_name}/>
          )} />

          <Route exact={false} path="" render={() => (
            <p>Unknown page.</p>
          )} />
        </Switch>

        <hr/>
        <p>Created by Conor Stuart-Roe and Kristian Gaylord</p>
      </Router>
    );
  }
}

const wrapper = document.getElementById("app");
wrapper ? ReactDOM.render(<App />, wrapper) : null;