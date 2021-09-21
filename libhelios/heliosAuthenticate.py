# authenticate using discord

import requests

USER_ENDPOINT="https://discordapp.com/api/users/@me"
REDIRECT_URL="https://helios.c3t.eecs.net/authenticate"


REQUEST_URL=f"https://discord.com/api/oauth2/authorize?client_id=889907808852656178&redirect_uri={REDIRECT_URL}&response_type=token&scope=identify%20email"



# given an access token, retrieve basic information
def getUser(accessToken):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {accessToken}'
    }

    userData=requests.get(USER_ENDPOINT, headers=headers)

    return userData