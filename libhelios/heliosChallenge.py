# individual challenges are defined in a configurable folder
# challenges must have:
# Prompt, Points, Language, Output, userin, cmdline_in
import json
import os

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
    def loadChallenges():
        # change dir
        programDir=os.getcwd()
        os.chdir(CHALLENGES_DIR)
        for file in os.listdir():
            if file.endswith(".json"):
                fp=open(file)
                heliosChallenge.challenges.append(json.load(fp))
                fp.close()
        os.chdir(programDir)