# helios

C3T statistics and training platform.

Purpose: Provide a controlled and stable environment to practice competitive cyber skills and enable tracking of member progress in each CTF category to allow for individual development and informed role assignments.

Helios is a combined system spanning multiple packages. By itself, Helios tracks writeups in a local mongoDB installation, allows grading, profile updates, etc.
This repository (currently) also includes the Artemis package, a custom dockerized code learning web app for the team. More documentation to follow, system is at `/artemis` when loaded.

Another part of the Helios system can be found at https://github.com/bitsforeveryone/helios-bot

Helios Bot is a simple NodeJS REST api for operations on C3T's Discord server using the Emissary bot. Running this part of the system on the same machine allows Helios to modify usernames, set roles, and create channels.

Installation:

1. Download Helios and Helios-Bot repositories to a folder
```
git clone git@github.com:bitsforeveryone/helios-bot.git && git clone git@github.com:bitsforeveryone/helios.git
```
2. Install python/nodeJS dependencies (can create virtualenv, up to you)
```
pip install -r helios/requirements.txt
npm install discord.js
npm install bodyParser
npm install express
```
3. Create a MongoDB installation. Currently Helios assumes a default port of `27017` and no password authentication (for now)
https://docs.mongodb.com/manual/installation/
4. Copy `secrets` folder to this directory to store credentials, create an rsa key pair
```
cp -R helios/install/secrets . && cd "$_"
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -subj "/C=US/ST=New York/L=West Point/O=C3T/OU=Org/CN=helios.bfe.one" -nodes && cd ..
```
5. Populate `misc.json` with Discord API data (some help here https://www.writebots.com/discord-bot-token/)
```
nano secrets/misc.json
```
6. (Optional) Create systemd service files for easy startup/shutdown. Note that some modification will be needed here depending what directory your files are in.
```
cp helios/install/{helios.service,heliosbot.service} /etc/systemd/system
```

If using systemd, start services with `systemctl helios start && systemctl heliosbot start`. Otherwise, it is possible to use `launch.sh` in each directory to launch servicces in terminal.
