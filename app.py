from flask import Flask, render_template

import challenges.helloWorldC, challenges.calculatorC
from libhelios import heliosChallenge, heliosSubmission

from challenges import *

app = Flask(__name__)


@app.route('/')
def hello_world():
    with open("meep.c","r") as book:
        testSubmit= heliosSubmission.heliosSubmission("challenges",
                                heliosChallenge.heliosChallenge.challenges[1],
                                str(book.read()))

    return str(testSubmit.check())

@app.route('/challenges')
def challenges():
    heliosChallenge.heliosChallenge.loadChallenges()
    return render_template('challenges.html', challenges=heliosChallenge.heliosChallenge.challenges)


if __name__ == '__main__':
    heliosChallenge.heliosChallenge.loadChallenges()
    app.run()
