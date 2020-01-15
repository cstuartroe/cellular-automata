from flask import Flask, request
app = Flask(__name__)


@app.route('/')
def rate_ruleset():
    with open("web/rate_ruleset.html", "r") as fh:
        return fh.read()


@app.route('/submit')
def submit():
    print(request.args)
    return 'Thank you! <a href="/">Do another?</a>'


if __name__ == '__main__':
    app.run()
