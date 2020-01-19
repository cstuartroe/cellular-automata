import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link, Switch } from "react-router-dom";
import ReactDOM from "react-dom";

import MainPage from "./MainPage.js";
import AboutPage from "./AboutPage.js";
import RatePage from "./RatePage.js";
import ThankYouPage from "./ThankYouPage.js";

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGithub } from "@fortawesome/free-brands-svg-icons";

import "../static/scss/main.scss";

const games = ["Conway", "RedVsBlue", "Rhomdos"];
const git_link = "https://github.com/cstuartroe/cellular-automata";


class App extends Component {
  render() {
    return (
      <Router>
        <div className="container header">
          <div className="row">
            <div className="col-12">
                <p>You've heard of Hot or Not, now get ready for...</p>
                <Link to="/"><h1>Biota or Nada?</h1></Link>
            </div>
            {games.map((game, index) => (
              <div className="col-4" key={index}>
                <Link to={"/" + game}><h3>{game}</h3></Link>
              </div>
            ))}
          </div>
        </div>

        <div style={{paddingBottom: "20vh"}}>
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

            <Route exact={true} path="/:game_name" render={({match}) => (
              <AboutPage game_name={match.params.game_name}/>
            )} />

            <Route exact={false} path="" render={() => (
              <p>Unknown page.</p>
            )} />
          </Switch>
        </div>

        <div style={{
          width: "100%",
          position: "fixed",
          bottom: 0,
          backgroundColor: "white",
          borderTop: "1px solid #aaaaaa"
        }}>
          <p style={{margin: 0, paddingTop: ".5vh"}}>Created by Conor Stuart-Roe and Kristian Gaylord</p>
          <a href={git_link}>
            <FontAwesomeIcon icon={faGithub} style={{margin: ".5vh", fontSize: "3vh", color: "black"}} />
          </a>
        </div>
      </Router>
    );
  }
}

const wrapper = document.getElementById("app");
wrapper ? ReactDOM.render(<App />, wrapper) : null;