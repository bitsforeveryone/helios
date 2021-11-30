from flask_pymongo import PyMongo
from __main__ import app
import json

# global definitions across the application
# just a class used to store static variables
class settings():
    # load secrets from file
    secrets = open("secrets/misc")
    SECRETS = json.load(secrets)
    secrets.close()

    # DISCORD_ENDPOINT=f"https://discord.com/api/oauth2/authorize?client_id={SECRETS['DISCORD_CLIENT_ID']}&redirect_uri=https%3A%2F%2Fhelios.c3t.eecs.net%2Fauth&response_type=code&scope=identify%20guilds"
    DISCORD_ENDPOINT = f"https://discord.com/api/oauth2/authorize?client_id={SECRETS['DISCORD_CLIENT_ID']}&redirect_uri=https%3A%2F%2Fhelios.bfe.one%2Fauth&response_type=code&scope=identify%20guilds"

    DISCORD_REQUESTS = []
    DISCORD_API = "https://discordapp.com/api"
    C3T_DISCORD_ID = "675737159717617666"

    # database connections
    mongoArtemis = PyMongo(app, uri="mongodb://localhost:27017/artemis")
    # define DB connection #TODO: shared file
    mongoHelios = PyMongo(app, uri="mongodb://localhost:27017/libhelios")
