# authenticate using discord

import requests

GET_USER="/users/@me"
GET_USER_GUILDS="/users/@me/guilds"

DISCORD_ENDPOINT = "https://discord.com/api/oauth2/authorize?client_id=889907808852656178&redirect_uri=https%3A%2F%2Fhelios.c3t.eecs.net%2Fauth&response_type=token&scope=identify%20guilds"
DISCORD_REQUESTS=[]
DISCORD_API="https://discordapp.com/api"

# given a request object, return a token after verifying request is legitimate
def getToken(request, requestArray):
    # request security using state param
    state = request.args.get("state")
    print(state,requestArray)
    if (state not in requestArray):
        return False
    requestArray.remove(state)
    # now request username, id, and servers
    tokenType = request.args.get("token_type")
    token = request.args.get("access_token")

    return (token, tokenType)

# given an access token, retrieve basic information
def getUser(accessToken, accessTokenType="Bearer"):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'{accessTokenType} {accessToken}'
    }

    userData=requests.get(DISCORD_ENDPOINT+GET_USER, headers=headers)
    userGuilds=requests.get(DISCORD_ENDPOINT+GET_USER_GUILDS, headers=headers)

    print(userGuilds)
    print(userData)
    return userData