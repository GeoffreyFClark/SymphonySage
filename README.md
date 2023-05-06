# 💯 Discord-Music-Bot 💯

🔥💪 Discord bot that plays free music for your server! 🎷🚀 </b>
### Commands:
- $help [command name]
- $play [song name]
- $splay [spotify playlist url] 
- $resume 
- $skip 
- $pause 
- $clear 
- $help
- $disconnect

## ✅ How to run the bot ✅
1. Make sure you have `Python` + a Python package installer like `Pip`.
     - Check by running in your terminal `python --version` and `pip --version` (Pre-installed on Macs).
2. Run `git clone https://github.com/GeoffreyFClark/Discord-Music-Bot.git` in your terminal.
     - Be sure to navigate to wherever you want the repository saved. 
     - Alternatively you can download this repository in a .zip by clicking code --> Download ZIP.
3. Open repository folder in terminal, run `pip install -r requirements.txt` to install the 2 required libraries.
     - Alternatively run `pip install nextcord nextwave`
4. Input your discord token, spotify_client_id, and spotify_client_secret in lines 7-9 and save. 
     - You can obtain the spotify client id + secret from the [spotify developer portal.](https://developer.spotify.com/dashboard)
          - Create App (Put <i>anything</i> for name, description, redirect URI).
          - App --> Settings --> View Basic Information --> Client ID + View Secret.
     - You can obtain a discord token from [the discord developer portal.](https://discord.com/developers/applications)<br>
          - Create a Discord App --> Bot sidetab --> configure settings --> click <i>Add Bot</i> --> Copy Discord Token<br>
5. Add the bot to your server via the discord developer portal.</br>
    - OAuth2 sidetab --> URL Generator --> Scopes: bot --> Select permissions --> URL to add bot to servers.<br>
    - Run Script and enjoy!
