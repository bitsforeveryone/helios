import random
import string
import imghdr

from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, abort

import json

from flask_pymongo import PyMongo

from libhelios import heliosChallenge, heliosSubmission, heliosAuthenticate, heliosDatabase

app = Flask(__name__)

mongoHelios = PyMongo(app, uri="mongodb://localhost:27017/helios")
mongoArtemis = PyMongo(app, uri="mongodb://localhost:27017/artemis")

# load/update helios database definitions with spec from file
heliosDatabase.populateDatabase(mongoHelios)


# load/update challenges into DB
heliosChallenge.heliosChallenge.loadChallenges(mongoArtemis.db)


for object in mongoArtemis.db.submissions.find({}):
    print(object)

for object in mongoHelios.db.users.find({}):
    print(object)

# load secrets from file
secrets=open("secrets/misc")
SECRETS=json.load(secrets)
secrets.close()

app.secret_key=SECRETS["FLASK_KEY"]

#DISCORD_ENDPOINT=f"https://discord.com/api/oauth2/authorize?client_id={SECRETS['DISCORD_CLIENT_ID']}&redirect_uri=https%3A%2F%2Fhelios.c3t.eecs.net%2Fauth&response_type=code&scope=identify%20guilds"
DISCORD_ENDPOINT=f"https://discord.com/api/oauth2/authorize?client_id={SECRETS['DISCORD_CLIENT_ID']}&redirect_uri=https%3A%2F%2Fhelios.bfe.one%2Fauth&response_type=code&scope=identify%20guilds"

DISCORD_REQUESTS=[]
DISCORD_API="https://discordapp.com/api"
C3T_DISCORD_ID="675737159717617666"

USERS=mongoHelios.db.users
RANKFACTS=mongoHelios.db.rankFacts
COMPETITIONS=mongoHelios.db.competitions
ARTEMIS_SUBMISSIONS=mongoArtemis.db.submissions

@app.route('/')
def login():
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
# TODO: Move somewhere else
def challengeSubmit():
    # receive challenge submit, grade and return result
    if request.method=='POST':
        # find challenge

        thisChal=mongoArtemis.db.challenges.find_one({"_id":ObjectId(request.form["challenge"])})
        print(thisChal["_id"])
        # create submission obj with user, challenge, and the code given and check
        if(thisChal):
            testSubmit=heliosSubmission.heliosSubmission(session["userID"],
                                    thisChal,
                                    request.form["submission"])
            checkTuple=testSubmit.check(mongoArtemis.db)
            return {"result":checkTuple[0],"response":{"expected":checkTuple[1][0],"received":checkTuple[1][1]}}
        return {"result":"Failure","response":"Failure"}


@app.route('/artemis')
def artemis():
    if 'userID' not in session:
        abort(403)
    # get challenges applicable to context
    language=request.args.get("language")
    langChallenges=[ chal for chal in mongoArtemis.db.challenges.find({"language":language})]
    # sort challenges
    langChallenges=sorted(langChallenges,key=lambda challenge: int(challenge["points"]))
    langSubmissions={}
    for sub in mongoArtemis.db.submissions.find({"userID": session["userID"], "language": language}):
        langSubmissions[sub["challenge"]]=sub

    return render_template('challenges.html', session=session, challenges=langChallenges, submissions=langSubmissions)

@app.route('/artemis/scoreboard')
def artemisScore():
    # get all current users, calculate score, plug into dictionary, render scoreboard
    boardDict={}
    for submission in mongoArtemis.db.submissions.find({}):
        user=mongoHelios.db.users.find_one({"userID":submission["userID"]})
        if(user):
            if user["name"] not in boardDict.keys():
                boardDict[user["name"]]=0
            challenge=mongoArtemis.db.challenges.find_one({"_id":submission["challenge"]})
            if(challenge):
                boardDict[user["name"]]+=int(challenge["points"])
        else:
            continue
        # sort
        boardDict=dict(sorted(boardDict.items(), key=lambda x: x[1], reverse=True))
    return render_template('scoreboard.html',boardDict=boardDict)

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
        print("User not in C3T Discord tried to join.")
        abort(403)

    # now check if user in DB

    if USERS.find_one({'userID':userData['id']}) == None:
        USERS.insert_one({
            'userID': userData['id'],
            "name":userData['username'],
            "xp":{
                "binex": 0,
                "crypto": 0,
                "web": 0,
                "blue": 0,
                "red": 0,
            },
            "competitions":[],
            "specialization": "",
            "seniority": "member",
            "profile": {
                "age":"",
                "class":"",
                "email":"",
                "summary":"",
                "realname":"",
                "avatar":""
            }
        })
        session["userID"]=userData['id']
        session["name"]=userData['username']
    else:
        session["userID"]=userData['id']
        session["name"]=userData['username']

    return redirect(url_for('artemis'))

@app.route('/test')
def test():
    return session["userID"]

def getRankFacts():
    rankFacts={}
    for record in RANKFACTS.find({},{'_id': 0}):
        print(record)
        factName=list(record.keys())[0]
        rankFacts[factName]=record[factName]
    print(rankFacts)
    return rankFacts

# profile page
@app.route('/profile',methods=["GET","POST"])
def profile():
    # if GET request, serve page
    if request.method=="GET":
        profileDict=USERS.find_one({'userID':session['userID']})
        rankFacts=getRankFacts()
        if profileDict==None:
            abort(403)
        return render_template('profile.html',session=session, profile=profileDict, rankFacts=rankFacts)
    if request.method=="POST":
        print(request.data)

        if len(request.files)>0:
            avatarFile=request.files.values()[0]
            print(imghdr.what(request.files.values()[0]))
        return "safafs"

@app.route('/profile/update', methods=["POST"])
def updateProfile():
    print(dict(request.form))
    return "safasf"


@app.route('/logout')
def logout():
    session.pop('userID', None)
    session.pop('username',None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True,ssl_context=('secrets/cert.pem', 'secrets/key.pem'),host="0.0.0.0",port="443")


