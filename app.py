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

DISCORD_ENDPOINT=f"https://discord.com/api/oauth2/authorize?client_id={SECRETS['DISCORD_CLIENT_ID']}&redirect_uri=https%3A%2F%2Fhelios.c3t.eecs.net%2Fauth&response_type=code&scope=identify%20guilds"

DISCORD_REQUESTS=[]
DISCORD_API="https://discordapp.com/api"
C3T_DISCORD_ID="675737159717617666"

USERS={}

@app.route('/')
def landingPage():
    if "userID" in session:
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
        authtoken,authtokentype=heliosAuthenticate.getToken(request, DISCORD_REQUESTS, SECRETS)
    except Exception as e:
        return str(e)
    if not authtoken:
        abort(403)

    userData=heliosAuthenticate.getUser(authtoken)
    userGuilds=heliosAuthenticate.getGuilds(authtoken)

    # iterate over guilds and ensure they belong to C3T guild
    inGuild=False
    for guild in userGuilds:
        if guild["id"] == C3T_DISCORD_ID:
            inGuild=True
    if not inGuild:
        abort(403)

    # now check if user in DB
    if userData['id'] not in USERS.keys():
        USERS[userData['id']]={
            "name":userData['name'],
            "artemis":{
                "C":0,
                "ASM":0
            },
            "xp":{
                "binex": 0,
                "crypto": 0,
                "web": 0,
                "blue": 0,
                "red": 0,
            },
            "competitions":[],
            "assignment":""
        }
    else:
        session["userID"]=userData['id']
        session["name"]=userData['name']

    return redirect(url_for('artemis'))

@app.route('/test')
def test():
    return session["userID"]


if __name__ == '__main__':
    app.run(ssl_context=('secrets/cert.pem', 'secrets/key.pem'),host="0.0.0.0",port="443")


