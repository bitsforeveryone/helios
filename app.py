from flask import Flask, render_template, request

import json

import challenges.helloWorldC, challenges.calculatorC
from libhelios import heliosChallenge, heliosSubmission

from challenges import *

app = Flask(__name__)

# load challenges
heliosChallenge.heliosChallenge.loadChallenges()
# load secrets
secrets=open("secrets/misc")
SECRETS=json.load(secrets)
secrets.close()

#
# @app.route('/')
# def hello_world():
#     with open("meep.c","r") as book:
#         testSubmit= heliosSubmission.heliosSubmission("challenges",
#                                 heliosChallenge.heliosChallenge.challenges[1],
#                                 str(book.read()))
#
#     return str(testSubmit.check())

@app.route('/submit', methods=['POST'])
def challengeSubmit():
    # receive challenge submit, grade and return result
    if request.method=='POST':
        # find challenge
        thisChal=None
        for chal in heliosChallenge.heliosChallenge.challenges:
            if chal["name"] == request.form["challenge"]:
                thisChal=chal

        if(thisChal):
            testSubmit=heliosSubmission.heliosSubmission("challenges",
                                    thisChal,
                                    request.form["submission"])
            if(testSubmit.check()):
                return "Success"
        # default case is failure
        return "Failure"



@app.route('/')
def challenges():
    return render_template('challenges.html', challenges=heliosChallenge.heliosChallenge.challenges)


if __name__ == '__main__':
    app.run(ssl_context=('secrets/cert.pem', 'secrets/key.pem'),host="0.0.0.0",port="443")
