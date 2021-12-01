import imghdr
import os
import random
import string
from hashlib import md5

from flask import Blueprint, render_template, abort, session, request, redirect, url_for
from flask_pymongo import PyMongo

# TODO: this is bad practice and I don't like it. Presently needed for DB connection.
from __main__ import app

# define blueprint for use by main app
from werkzeug.utils import secure_filename

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
    thisUser=USERS.find_one({'userID':userData['id']})
    if thisUser == None:
        # create copy from template
        newUser=USERS.find_one({'userID':'template'},{"_id":0})
        newUser['userID']=userData['id']
        newUser['profile']['handle']=userData['username']
        USERS.insert_one(newUser)
        session["userID"]=userData['id']
        session["name"]=userData['username']
    else:
        session["userID"]=userData['id']
        session["name"]=thisUser["profile"]["handle"]

    return redirect(url_for('helios.profile'))

@helios.route('/test')
def test():
    return session["userID"]

def getRankFacts():
    rankFacts={}
    for record in RANKFACTS.find({},{'_id': 0}):
        # print(record)
        factName=list(record.keys())[0]
        rankFacts[factName]=record[factName]
    # print(rankFacts)
    return rankFacts

# profile page
@helios.route('/profile',methods=["GET","POST"])
def profile():
    # block if not valid session
    heliosAuthenticate.validateUser(session)
    # if GET request, serve page
    if request.method=="GET":
        profileDict=USERS.find_one({'userID':session['userID']})
        rankFacts=getRankFacts()
        if profileDict==None:
            return redirect(url_for("helios.logout"))
        return render_template('profile.html',session=session, profile=profileDict, rankFacts=rankFacts)

# Takes in a flask uploaded file object and verifies if it is an image
# If not an image, returns None. If true, returns the format
def validateImage(image):
    fileStream=image.stream
    filename=secure_filename(image.filename)
    fileExt=filename.split('.')[1]
    if ('.'+fileExt) in app.config["UPLOAD_EXTENSIONS"]:
        imageFormat=imghdr.what(None,fileStream.read(512))
        # jpg has two extensions
        imageFormat=(imageFormat if imageFormat != 'jpeg' else 'jpg')
        if imageFormat==fileExt:
            fileStream.seek(0)
            return imageFormat
    return None



@helios.route('/profile/update', methods=["POST"])
def updateProfile():
    # block if not a valid session
    heliosAuthenticate.validateUser(session)
    # if not a valid user this is cause for concern but just error out for now TODO: Generate report
    thisUser=USERS.find_one({'userID':session['userID']})
    if thisUser == None:
        abort(403)
    # update user based on session
    # create dict for painless update
    newData={"profile":dict(request.form)}
    # get image if exists
    if len(request.files) > 0 and len(request.files['avatar'].filename)>0:
        thisImage=request.files['avatar']
        imageFormat=validateImage(thisImage)
        if imageFormat:
            # save to file
            newFilename='.'.join([session['userID'],imageFormat])
            newFilename=os.path.join(app.config['UPLOAD_IMAGE_PATH'],newFilename)
            thisImage.save(newFilename)
            newData["profile"]["avatar"]=newFilename
    else:
        newData["profile"]["avatar"]=thisUser["profile"]["avatar"]
    #mongo query
    newData={"$set": newData}
    #update
    USERS.update_one({'userID':session['userID']},newData)
    return redirect(url_for("helios.profile"))

@helios.route('/profile/reclass', methods=['GET'])
# take requested reclass, verify if it exists and user is eligible
# assign in database
def reclass():
    heliosAuthenticate.validateUser(session)
    reclassCategory=request.values["category"].lower()

    reclassRank=request.values["rank"].lower()
    # verify this exists
    rankfacts=getRankFacts()
    if reclassCategory in rankfacts["categories"].keys() and reclassRank in rankfacts["mastery"].keys():

        # check has enough points
        userXP=int(USERS.find_one({'userID': session['userID']},{"xp": 1})["xp"][reclassCategory])
        requiredXP=int(rankfacts["mastery"][reclassRank])
        if userXP>=requiredXP:
            # update user
            reclass={"specialization":reclassCategory,"mastery":reclassRank}
            # query
            reclass={"$set": reclass}
            USERS.update_one({'userID':session['userID']},reclass)
            print("reclass successful")

    return redirect(url_for("helios.profile"))

@helios.route('/writeups')
def writeups():
    return render_template('writeups.html',rankFacts=getRankFacts())

@helios.route('/writeups/submit',methods=["POST"])
# take a given writeup submission and commit to the database
def submitWriteup():
    heliosAuthenticate.validateUser(session)
    rankFacts=getRankFacts()
    if(len(request.form)>0):
        # validate contents
        try:
            requestName=(request.form["name"] if len(request.form["name"])>0 else None)
            requestCategory=(request.form["category"] if request.form["category"] in rankFacts["categories"] else None)
            requestDifficulty=(request.form["difficulty"] if request.form["difficulty"] < rankFacts["writeups"].keys()[-1] else None)
        except:
            # dip out
            abort(406)



@helios.route('/logout')
def logout():
    session.pop('userID', None)
    session.pop('username',None)
    return redirect(url_for('helios.login'))