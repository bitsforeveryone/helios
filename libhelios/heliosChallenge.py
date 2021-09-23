# individual challenges are defined in a configurable folder
# challenges must have:
# Prompt, Points, Language, Output, userin, cmdline_in
import json
import os

from bson import ObjectId

CHALLENGES_DIR="challenges"

class heliosChallenge:
    challenges=[]
    # get vars prepared for follow on use
    def __init__(self):
        self.name=None
        self.prompt=None
        self.language=None
        self.output=None
        self.userin=""
        self.cmdline_in=""
        self.points=0


    # load challenges from challenges folder
    @staticmethod
    def loadChallenges(db):
        # change dir
        programDir=os.getcwd()
        os.chdir(CHALLENGES_DIR)
        for file in os.listdir():
            if file.endswith(".json"):
                # check if in database
                chal=None
                try:
                    with open(file) as fp:
                        chal=json.load(fp)
                except:
                    print("Could not load %s"%file)
                    continue
                # thisChal=db.challenges.find({"name":chal["name"]})
                newChal=db.challenges.update_one({"name":chal["name"]},{"$set":chal},upsert=True)
                # if(thisChal!=None) {
                #     db.challenges.update({"name":chal["name"]},{"$set":{"_id":ObjectId(thisChal["_id"])}})
                # }
        os.chdir(programDir)