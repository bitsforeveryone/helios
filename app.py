import random
import string

from flask import Flask, render_template, request, redirect, url_for, session, abort

import json

import challenges.helloWorldC, challenges.calculatorC
from libhelios import heliosChallenge, heliosSubmission, heliosAuthenticate

from challenges import *

app = Flask(__name__)

# load challenges
heliosChallenge.heliosChallenge.loadChallenges()
# load secrets from file
secrets=open("secrets/misc")
SECRETS=json.load(secrets)
secrets.close()

DISCORD_ENDPOINT = f"https://discord.com/api/oauth2/authorize?client_id={SECRETS['DISCORD_CLIENT_ID']}&redirect_uri=https%3A%2F%2Fhelios.c3t.eecs.net%2Fauth&response_type=code&scope=identify%20guilds"
DISCORD_REQUESTS=[]
DISCORD_API="https://discordapp.com/api"

@app.route('/')
def landingPage():
    if "user" in session:
        # TODO: This should go somewhere else
        return redirect(url_for('artemis'))
    # otherwise need to actually login. Generate a state string
    # this is used to ensure login returns are actually those requested by app
    state=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
    DISCORD_REQUESTS.append(state)

    thisEndpoint=DISCORD_ENDPOINT+"&state=%s"%state
    return render_template('login.html',endpoint=thisEndpoint)

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
    authtoken=""
    try:
        authtoken,authtokentype=heliosAuthenticate.getToken(request, DISCORD_REQUESTS)
    except:
        abort(405)
    if not authtoken:
        abort(405)
        
    print(heliosAuthenticate.getUser(authtoken))
    return redirect(url_for('artemis'))

@app.route('/test')
def test():
    return session["user"]


if __name__ == '__main__':
    app.run(ssl_context=('secrets/cert.pem', 'secrets/key.pem'),host="0.0.0.0",port="443")


