# Tesla Over Discord
Control your Tesla through your Discord application.

## Installation
This project is possible with [`discord.py`](https://github.com/Rapptz/discord.py) and the [TeslaPy (by tdorssers)](https://github.com/tdorssers/TeslaPy)
It has been tested on versions >= Python 3.7.

1. Install the requirements
```
pip install -r requirements.txt
```

2. Create a `.env` file and make sure to input your Tesla credentials.
```
DISCORD_TOKEN=<your Discord bot token>
TESLA_EMAIL=elon@tesla.com
ALLOWED_USERIDS=100000000000,200000000000
```
Make sure to replace the values with your parameters.

3. Run the bot
```
python app.py
```

# Important Notice
Your session will be saved into a `cache.json` file. Even tho it is not a secure way to save a session token, I cannot modify that, so please make sure that you don't share your `cache.json` file with anyone.
