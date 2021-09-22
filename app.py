from flask import Flask, render_template, request, redirect, url_for

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
DISCORD_ENDPOINT = "https://discord.com/api/oauth2/authorize?client_id=889907808852656178&redirect_uri=https%3A%2F%2Fhelios.c3t.eecs.net%2Fauth&response_type=token&scope=identify%20guilds"
secrets.close()

@app.route('/')
def landingPage():
    return render_template('login.html',endpoint=DISCORD_ENDPOINT)

@app.route('/artemis/submit', methods=['POST'])
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


@app.route('/artemis')
def artemis():
    return render_template('challenges.html', challenges=heliosChallenge.heliosChallenge.challenges)

@app.route('/auth')
def authDiscord():
    tokenType=request.args.get("token_type")
    token=request.args.get("access_token")
    return redirect(url_for('artemis'))

@app.route('/test')
def test():
    return str(request.remote_addr)
if __name__ == '__main__':
    app.run(ssl_context=('secrets/cert.pem', 'secrets/key.pem'),host="0.0.0.0",port="443")
