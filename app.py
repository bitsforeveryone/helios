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
            checkTuple=testSubmit.check()
            return {"result":checkTuple[0],"response":{"expected":checkTuple[1][0],"received":checkTuple[1][1]}}
        return {"result":"Failure","response":"Failure"}


@app.route('/')
def challenges():
    return render_template('challenges.html', challenges=heliosChallenge.heliosChallenge.challenges)


if __name__ == '__main__':
    app.run(ssl_context=('secrets/cert.pem', 'secrets/key.pem'),host="0.0.0.0",port="443")
