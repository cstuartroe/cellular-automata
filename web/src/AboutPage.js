import React, { Component } from "react";
import { Link } from "react-router-dom";
import ReactDOM from "react-dom";

const game_abouts = {
  Conway: <div className="col-12">
    Conway yo
  </div>,

  RedVsBlue: <div className="col-12">
    rvb is kool
  </div>,

  Rhomdos: <div className="col-12">
    swiggity swooty
  </div>,
}

class About extends Component {
    render() {
      return(
        <div className="container">
          <div className="row">
            <div className="col-12">
              <p>Want to help us out? <Link to={"/" + this.props.game_name + "/rate"}>Rate a few games!</Link></p>
            </div>

            {game_abouts[this.props.game_name]}
          </div>
        </div>
      )

    }
}

export default About;