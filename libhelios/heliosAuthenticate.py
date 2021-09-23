# authenticate using discord

import requests

GET_USER="/users/@me"
GET_USER_GUILDS="/users/@me/guilds"

DISCORD_API="https://discordapp.com/api"

# given a request object, return a token after verifying request is legitimate
def getToken(request, requestArray):
    # request security using state param
    state = request.args.get("state")
    print(state,requestArray)
    if (state not in requestArray):
        return False
    # remove now, invalid
    requestArray.remove(state)
    code= request.args.get("code")
    data = {
        'client_id': SECRETS['DISCORD_CLIENT_ID'],
        'client_secret': SECRETS['DISCORD_CLIENT_SECRETS'],
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': request.base_url
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % DISCORD_API, data=data, headers=headers)
    r.raise_for_status()

    return (r.json()["access_token"], r.json()["token_type"])

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