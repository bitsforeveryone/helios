# examine helios database and apply definitions if none exist
import json

from flask_pymongo import PyMongo
import os

DEFINITIONS_ROOT=os.path.join("libhelios","definitions")

def populateDatabase(heliosDB : PyMongo):
    # retreive definitions
    defs=os.listdir(DEFINITIONS_ROOT)
    for item in defs:
        if item.endswith(".json"):
            # get full relative path
            fullPath=os.path.join(DEFINITIONS_ROOT,item)
            collectionName=item.replace(".json","")
            # check if definition already exists in db. If so, keep going
            if collectionName in heliosDB.db.list_collection_names():
                continue
            # if it isn't, populate with defaults
            # read template into dict
            with open(fullPath) as reader:
                contents=json.load(reader)
                # declare new collection in pyMongo
                heliosDB.db[collectionName]
                # insert contents item by item
                for entry in contents.keys():
                    heliosDB.db[collectionName].insert({entry:contents[entry]})
