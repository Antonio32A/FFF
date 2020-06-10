# FFF
[![discord](https://img.shields.io/discord/654847187305365515?logo=discord&style=for-the-badge)](https://discord.gg/uv7SGvz)

[![license](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![python](https://img.shields.io/badge/python-v3.8.2-blue?style=for-the-badge)](https://www.python.org/downloads/release/python-382/)
[![github commit activity](https://img.shields.io/github/commit-activity/y/Antonio32A/FFF?style=for-the-badge)](https://github.com/Antonio32A/FFF/commits)
[![code size](https://img.shields.io/github/languages/code-size/Antonio32A/FFF?style=for-the-badge)](https://github.com/Antonio32A/FFF)

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/uses-badges.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/gluten-free.svg)](https://forthebadge.com)

A simple Discord bot written in discord.py for a Discord guild of the Final Floor Frags guild on Hypixel.


### Features
- `profile <username>` - Shows somebody's Hypixel SkyBlock profile information such as:
    - fairy souls
    - bank
    - skills
    - skill average
    - slayers
    - pets
- `apply <username>` - Applies for the FFF Hypixel guild.
- `auction <username>` - Shows somebody's Hypixel SkyBlock auctions.
- `soups [amount=1]` - Calculates the average prices of Magical Soups. Defaults to 1 soup.
- automatic Discord sync based on Hypixel guild ranks
- a spreadsheet which is frequently updated and displays Hypixel guild members' SkyBlock profile information


### Running
Feel free to run a copy of this bot and modify it, credit is appreciated.


#### Requirements
- python3.8
- python3.8-venv (optional, but recommended)
- pip
- git


#### Getting started
To get started with running the bot simply clone the GitHub repository using git and `cd` into it:
```shell script
git clone https://github.com/Antonio32A/FFF.git
cd FFF
```

#### Config
Copy `example_config.json` and rename the copy to `config.json`.

Fill the config with your values, debug and production tokens and prefixes can be the same but not recommended if debugging

You can get your Discord tokens from [here](https://discordapp.com/developers/applications/) 
by creating a bot application.

You can get your google_service_account_secret.json by going [here](https://console.cloud.google.com/apis/credentials), 
[creating another project](http://antonio32a.tech/dOhR.png), [creating a service account](http://antonio32a.tech/LXcN.png) 
(name it whatever you want to), [giving it a role Project Editor](http://antonio32a.tech/rbbP.png), clicking on 
`CREATE` KEY and selecting `JSON`. It will download a JSON file which you rename and put in the bot files. Keep it secret!

To get your spreadsheet_key you need to go to [Google Sheets](https://docs.google.com/spreadsheets) and create a 
spreadsheet. Your spreadsheet URL will look like:

https://docs.google.com/spreadsheets/d/1QZQzAaZlXOGFM8IwFp03I7OouB-L83tT2OeyL3RxOik/edit#gid=0

The part between `spreadsheets/d/` and the last `/` is your spreadsheet_key.

Make sure to add your bot's Google service account email to the spreadsheet 
(you can find the email in the `google_service_account_secret.json` file)

You can get your Hypixel key by doing `/api new` in your game while on Hypixel and copying it. 
(You can also reuse a old one if you created a new one before)

The role config's order is important, the first one should be your lowest rank and the last one should be your highest rank.

Example of role config:
```json
"roles": {
  "non": 654848188250849303,
  "member": 654848188250849303,
  "veteran": 670244448969424949,
  "endgame": 692526910151983104,
  "kingotg": 692527077798445056,
  "staff": 720015297947369513
}
```

The names (non, member, veteran, endgame, kingotg and staff) are rank names in-game and the IDs are the Discord role IDs.

#### Installation
This step is optional but it's recommended. If `python3.8` doesn't work try `py` or `py3.8`.
```shell script
python3.8 -m venv venv
# On macOS and Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

Then install the requirements:
```shell script
pip install -r requirements.txt
```

### Starting the bot
To start the bot run:
```shell script
python main.py
```
If you made it this far, congratulations! You now have a running clone of the FFF bot!

If you have any questions, suggestions or issues please contact me by joining the Discord (link above).


### Credits
- [Marti157](https://github.com/marti157) for the help with the code and for the contest code.
- [Ben/correct](https://github.com/Drug) for the original bot concept and for the original application system.
- ComplexOrigin for the nice pet level calculation method and more.


### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.