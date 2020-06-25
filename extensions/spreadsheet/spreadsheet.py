from datetime import datetime

from discord.ext import commands, tasks

from util import Handlers


def avg(rows: list, index: int):
    """
    This is used to calculate the skill average and the slayer average of the whole guild
    :param (list) rows: A list containing more lists which are used to calculate the average
    :param (index) index: The index in the list of the value to calculate
    :returns (str): The rounded guild average
    """
    total = 0
    for row in rows:
        if type(row[index]) in (int, float):
            total += row[index]

    result = total / len(rows)
    return str(round(float(result), 1))


class Spreadsheet(commands.Cog, name="Spreadsheet"):
    """
    This cog manages the spreadsheet
    """
    def __init__(self, fff):
        self.fff = fff
        self.spreadsheet = Handlers.Spreadsheet(self.fff.bot_config['spreadsheet_key'])

        self.spreadsheet_loop.start()

    def cog_unload(self):
        """
        Cancel the loop when the cog unloads
        """
        self.spreadsheet_loop.cancel()

    @tasks.loop(minutes=15.0)
    async def spreadsheet_loop(self):
        """
        Automatically gets the guild and player stats and updates them on the spreadsheet
        """
        try:
            guild_data = self.fff.cache.get()['guild_data']
        except KeyError:
            return  # This only happens when the bot starts since the data isn't cached yet

        rows = []
        self.fff.logger.info("Updating spreadsheet information...")
        await self.spreadsheet.auth()

        for member in guild_data.keys():
            uuid = member
            member = guild_data[uuid]
            username = member['username']
            discord_connection = member['discord_connection']
            paid = member['paid']
            paid_to = member['paid_to']
            skill_average = member['skill_average']
            slayer_xp = member['slayer_xp']
            passes_reqs = member['passes_reqs']
            rows.append([uuid, username, discord_connection, paid, paid_to, skill_average, slayer_xp, passes_reqs])

        self.spreadsheet.clear()
        self.spreadsheet.append_row(
            [
                "uuid",
                "username",
                "discord",
                "paid",
                "paid_to",
                "skill_average",
                "slayer_xp",
                "passes_reqs"
            ]
        )
        self.spreadsheet.insert_rows(rows, 2)
        self.spreadsheet.append_row(
            [
                "skill",
                "level",
                "average:",
                avg(rows, 5),
                "slayer",
                "xp",
                "average:",
                avg(rows, 6)
            ]
        )
        now = datetime.now()
        self.spreadsheet.append_row(
            [
                "last",
                "updated",
                "at",
                now.strftime("%H"),
                now.strftime("%M"),
                now.strftime("%S"),
                "utc",
                "(cet-2)"
            ]
        )
        self.fff.logger.info("Successfully updated the spreadsheet information.")

    @spreadsheet_loop.before_loop
    async def before_tasks(self):
        """
        This starts the loop when the bot is ready to work
        """
        await self.fff.wait_until_ready()
