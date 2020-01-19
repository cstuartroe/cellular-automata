import React, { Component } from "react";
import ReactDOM from "react-dom";

class ThankYouPage extends Component{
  render(){
    return(
      <div className="main">
        <h1>Thank you!</h1>
        <a id="another" href={"/" + this.props.game_name + "/rate"}>Do another?</a>
        <br/>
        <br/>
        <img src="/static/img/thankyou.jpg" alt="Thanks"/>
      </div>
    )
  }
}

export default ThankYouPage;