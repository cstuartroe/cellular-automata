import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link, Switch } from "react-router-dom";
import ReactDOM from "react-dom";

import "../static/scss/main.scss";

const generate_url = '/api/generate_game'
const base_img_url = '/img/'

class MainPage extends Component {

    constructor(props) {
      super(props);

      this.state = {
        game_name: props.game_name,
        game_id: '',
      };
    }

    componentDidMount(){
      this.generate_new_id();
    }

    generate_new_id() {
      fetch(generate_url)
        .then(response => response.json())
        .then(data => {
          this.setState({'game_id':data.game_id});
          console.log(this.state.game_id);
        });
    }

    render() {

      var gif = base_img_url.concat(this.state.game_name, '_', this.state.game_id, '.gif')

      return(
        <div>
                <p>You've heard of Hot or Not, now get ready for...</p>
                <h1>Biota or Nada?</h1>
                <h2>Does this gif look more like structured life or a staticky TV?</h2>
                <img src={gif}/>
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
      )

    }
}

class ThankYouPage extends Component{
  render(){
    return(
      <div className="main">
                <h1>Thank you!</h1>
                <a id="another" href="/">Do another?</a>
                <br/>
                <br/>
                <img src="/static/img/thankyou.jpg" alt="Thanks" height="500" width="700"/>
        </div>
    )
  }
}

class App extends Component {
  render() {
    return (
      <Router>
          <Switch>
            <Route exact={true} path="/thank_you" render={() => (
              <ThankYouPage></ThankYouPage>
            )} />

            <Route exact={true} path="/" render={() => (
              <MainPage game_name='RedVsBlue'></MainPage>
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