import React, { Component } from "react";
import { Redirect } from "react-router-dom";
import ReactDOM from "react-dom";
const qs = require('querystring');

const generate_url = '/api/generate_game';
const base_img_url = '/img/';
const submit_url = "/submit";

class RatePage extends Component {
    constructor(props) {
      super(props);

      this.state = {
        game_id: '',
        grad_steps: 0,
        grad_max: 0,
        grad_min: 0,
        rating: -1,
        submitted: false
      };
    }

    componentDidMount(){
      this.generate_new_id();
    }

    generate_new_id() {
      fetch(generate_url + "?game_name=" + this.props.game_name)
        .then(response => response.json())
        .then(data => {
          this.setState(data);
          console.log(data);
        });
    }

    submit() {
      console.log('Submit click')
      const body = qs.stringify({
            game_name: this.props.game_name,
            game_id: this.state.game_id,
            rating: this.state.rating
       });

      if (this.state.rating != -1 && this.state.game_id != '') {
        fetch(submit_url, {
          method: "POST",
          body: body,
          headers: {
             'Content-Type': 'application/x-www-form-urlencoded',
          }
        }).then(response => {
            if (response.status == 200) {
              this.setState({submitted: true});
            }
          })
      }

      console.log(body)
    }

    render() {
      if (this.state.submitted) {
        return <Redirect to={"/" + this.props.game_name + "/thanks"} />
      }

      var gif = base_img_url + this.props.game_name + '_' + this.state.game_id + '.gif';
      var ai_message = this.state.grad_steps === 0 ?
                       'This is a randomly generated image, out of an infinite number of possibilities.'
                       :
                       'This image was generated with artificial intelligence, using ' + this.state.grad_steps + ' gradient steps.';

      var img = this.state.game_id == "" ?
                <img src="/static/img/spinner.gif" style={{padding: "75px"}} />
                :
                <img src={gif}/>;

      var rating_messages = [
        "0% interesting (aka 100% LAME)",
        "25% interesting",
        "50% interesting",
        "75% interesting",
        "100% interesting \u{1F3C4} \u{1F3B8}"
      ];

      return(
        <div className="container constrained" style={{padding: "2vh"}}>
          <div className="row">
            <div className="col-12 col-md-6">
              <p>Does this gif look more like structured life or a staticky TV?</p>
              {img}
              <p>{ai_message}</p>
            </div>
            <div className="col-12 col-md-6 rating-box">
              <form style={{padding: "2vh"}}>
                {rating_messages.map((message, index) => (
                  <div key={index} style={{padding: ".5vw"}}>
                    <p className={"radio-p " + (this.state.rating === index ? "radio-p-selected" : "")}
                      onClick={() => this.setState({rating: index})}>
                      {" " + message}
                    </p>
                  </div>
                ))}
              </form>

              <br/>

              <button className="rate_button" onClick={this.submit.bind(this)}>Submit</button>
            </div>
          </div>
        </div>
      )

    }
}

export default RatePage;