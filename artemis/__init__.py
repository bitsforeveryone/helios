from flask import Blueprint, render_template, abort, session, request
from flask_pymongo import PyMongo

# TODO: this is bad practice and I don't like it. Presently needed for DB connection.
from __main__ import app


artemis = Blueprint('artemis', __name__, template_folder='templates')
# global settings
from settings import settings
# import local packages
from artemis.artemisChallenge import artemisChallenge
from artemis.artemisSubmission import artemisSubmission
# database loading
mongoArtemis=settings.mongoArtemis
mongoHelios=settings.mongoHelios
# alias database endpoints
ARTEMIS_SUBMISSIONS=mongoArtemis.db.submissions
# load/update challenges into DB
artemisChallenge.loadChallenges(mongoArtemis.db)

# for object in mongoArtemis.db.submissions.find({}):
#     print(object)

@artemis.route('/artemis/submit', methods=['POST'])
# TODO: Move somewhere else
def challengeSubmit():
    # receive challenge submit, grade and return result
    if request.method=='POST':
        # find challenge

        thisChal=mongoArtemis.db.challenges.find_one({"_id":ObjectId(request.form["challenge"])})
        print(thisChal["_id"])
        # create submission obj with user, challenge, and the code given and check
        if(thisChal):
            testSubmit=artemisSubmission(session["userID"],
                                    thisChal,
                                    request.form["submission"])
            checkTuple=testSubmit.check(mongoArtemis.db)
            return {"result":checkTuple[0],"response":{"expected":checkTuple[1][0],"received":checkTuple[1][1]}}
        return {"result":"Failure","response":"Failure"}


@artemis.route('/artemis')
def main():
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

@artemis.route('/artemis/scoreboard')
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