import React, { Component } from "react";
import ReactDOM from "react-dom";

class App extends Component {
  state = {
    username: null,
    screen_name: null,
    game: null,
    gameTitle: null,
    gameInstance: null
  };

  setUser(username, screen_name) {
    this.setState({
      username: username,
      screen_name: screen_name
    });
  }

  setGame(gameSlug, gameTitle) {
    this.setState({
      game: gameSlug,
      gameTitle: gameTitle
    });
  }

  setGameInstance(gameInstanceId) {
    this.setState({
      gameInstance: gameInstanceId
    });
  }

  render() {
    const { username, screen_name, game, gameTitle, gameInstance } = this.state;

    var bodyElem;
    if (username == null) {
      bodyElem = <UserLogin setUser={this.setUser.bind(this)} />;
    } else if (game == null) {
      bodyElem = <GamePicker setGame={this.setGame.bind(this)} />;
    } else if (gameInstance == null) {
      bodyElem = <GameRoomPicker username={username} game={game} setGameInstance={this.setGameInstance.bind(this)} />;
    } else if (game == "feelin-lucky") {
      bodyElem = <FeelinLucky username={username} gameInstance={gameInstance}/>;
    } else {
      bodyElem = <p>Unknown game.</p>;
    }

    return (
      <div className="container">
        <TopMenu screen_name={screen_name} gameTitle={gameTitle} gameInstance={gameInstance}/>
        { bodyElem }
      </div>
    );
  }
}

const wrapper = document.getElementById("app");
wrapper ? ReactDOM.render(<App />, wrapper) : null;