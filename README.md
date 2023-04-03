# Tesla Over Discord
Control your Tesla through your Discord application.
**Do not host your project on websites such as Glitch or Replit (where the source code is public). [See more here.](#using-public-hosting-services-such-as-glitch-or-replit)**

## Installation
This project is possible with [`discord.py`](https://github.com/Rapptz/discord.py) and the [`TeslaPy`](https://github.com/tdorssers/TeslaPy)
It has been tested on versions **>= Python 3.7**.

### Create the Discord bot
- Make sure that you've made a Discord bot in the [Discord Developer Portal](https://discord.com/developers/applications), retrieved the bot's token.
- Get the **Application ID** (found in *General Information*, and then click *Copy*)
- Then replace *BOTID* by your **bot's ID** in the link, and invite this bot in a server.  
https://discord.com/api/oauth2/authorize?client_id=BOTID&permissions=8&scope=bot%20applications.commands  
⚠️ **For safety reasons, it is recommended to invite in a server that nobody and no bots has access to, and make sure there is no existing invites in the server.**


### Run the code
1. **Install the requirements**
```
pip install -r requirements.txt
```

2. **Create a `.env` file and replace the dummy values your Tesla Account e-mail, Discord token and the User IDs that are allowed to use the bot.**
```
DISCORD_TOKEN=<your Discord bot token>
TESLA_EMAIL=elon@tesla.com
ALLOWED_USERIDS=100000000000,200000000000
```
*User IDs are a way to recognize the different Discord accounts. If you don't know how to get yours, [check this tutorial made by Discord.](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)*  

3. **Run the bot**
```
python app.py
```

# Security Advices
## Important Note about how your credentials are stored
Your session will be saved into a `cache.json` file. Even tho it is not a secure way to save a session token, I cannot modify that, so please make sure that you don't share your `cache.json` file with anyone.

### Do not share your code to anyone, or make sure to exclude `logs/`, **`.env`** and **`cache.json`**
The logs folder, the environment file and the cache file may contain private informations such as your Discord token, your Tesla account e-mail, and more importantly, the access to your Tesla account. See below if you accidentally sent these files.

### What to do if your `cache.json` or token is leaked
Immediately change your **Tesla account password**. If anyone gets access to your Tesla account, they will be able to remote start your car and unlock it, and execute a bunch of different actions.  
To change your Tesla password, **[follow this link](https://auth.tesla.com/user/password/forgot)**. You will be asked to reauthenticate on every of your devices, and the tokens will expire.

### Self-hosting this project
If you self-host this bot on a server, make sure that only trusted persons can access it.

### Using public hosting services such as **Glitch** or **Replit**
**Do not host your bot on Glitch or Replit**. The `cache.json` is, once again, public and will not be hidden from people visiting your project on these services.  
If you have a premium subscription on one of these services, you may be able to make your project private. However, it is still not recommended to publish your private token on one of these websites.