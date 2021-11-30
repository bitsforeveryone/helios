import imghdr
import random
import string
from flask import Blueprint, render_template, abort, session, request, redirect, url_for
from flask_pymongo import PyMongo

# TODO: this is bad practice and I don't like it. Presently needed for DB connection.

# define blueprint for use by main app
helios = Blueprint('helios', __name__, template_folder='templates')
# import global settings
from settings import settings
# package imports
from libhelios import heliosAuthenticate, heliosDatabase
# database
mongoHelios=settings.mongoHelios
# load/update libhelios database definitions with spec from file
heliosDatabase.populateDatabase(mongoHelios)
# alias common db endpoints
USERS=mongoHelios.db.users
RANKFACTS=mongoHelios.db.rankFacts
COMPETITIONS=mongoHelios.db.competitions

for object in mongoHelios.db.users.find({}):
    print(object)

@helios.route('/')
def login():
    if "userID" in session:
        # TODO: This should go somewhere else
        return redirect(url_for('helios.profile'))
    # otherwise need to actually login. Generate a state string
    # this is used to ensure login returns are actually those requested by app
    # note that these don't persist in the database so user sessions are technically invalidated every restart
    # however as of 30NOV there is no check to verify whether existing sessions have a corresponding Discord State (api does not allow)
    state=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
    settings.DISCORD_REQUESTS.append(state)

    thisEndpoint=settings.DISCORD_ENDPOINT+"&state=%s"%state
    return render_template('login.html',endpoint=thisEndpoint)

@helios.route('/auth')
def authDiscord():
    authtoken=""
    try:
        authtoken,authtokentype=heliosAuthenticate.getToken(request, settings.DISCORD_REQUESTS, settings.SECRETS)
    except Exception as e:
        return str(e)
    if not authtoken:
        abort(403)

    userData=heliosAuthenticate.getUser(authtoken)
    userGuilds=heliosAuthenticate.getGuilds(authtoken)

    # iterate over guilds and ensure they belong to C3T guild
    inGuild=False
    for guild in userGuilds:
        if guild["id"] == settings.C3T_DISCORD_ID:
            inGuild=True
    if not inGuild:
        # TODO: Need to generate report if this happens
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

    return redirect(url_for('helios.profile'))

@helios.route('/test')
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
@helios.route('/profile',methods=["GET","POST"])
def profile():
    # block if not valid session
    if 'userID' not in session:
        abort(403)
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

@helios.route('/profile/update', methods=["POST"])
def updateProfile():
    # block if not a valid session
    if 'userID' not in session:
        abort(403)
    # if not a valid user this is cause for concern but just error out for now TODO: Generate report
    if USERS.find_one({'userID':session['userID']}) == None:
        abort(403)
    # update user based on session
    # create dict for painless update
    newData={"profile":dict(request.form)}
    #mongo query
    newData={"$set": newData}
    #update
    USERS.update_one({'userID':session['userID']},newData)
    return redirect(url_for("helios.profile"))


@helios.route('/logout')
def logout():
    session.pop('userID', None)
    session.pop('username',None)
    return redirect(url_for('helios.login'))