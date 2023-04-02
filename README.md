# Discord Notifications for Tesla
Receive alerts from your Tesla and control your Tesla using Discord.

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
```

3. Run the bot
```
python app.py
```
