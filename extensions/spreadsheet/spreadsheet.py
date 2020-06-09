import asyncio
import json
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
        if type(row[index]) != str:
            total += row[index]

    result = total / len(rows)
    return str(round(float(result), 1))


class Spreadsheet(commands.Cog, name="Spreadsheet"):
    """
    This cog manages the spreadsheet
    """
    def __init__(self, fff):
        self.fff = fff
        self.skyblock = Handlers.SkyBlock(self.fff.config['key'], self.fff.session)
        self.mojang = Handlers.Mojang(self.fff.session)
        self.spreadsheet = Handlers.Spreadsheet(self.fff.config['spreadsheet_key'])

        self.hypixel_guild_id = self.fff.config['hypixel_guild_id']
        self.min_total_slayer_xp = self.fff.config['min_total_slayer_xp']
        self.min_average_skill_level = self.fff.config['min_average_skill_level']
        self.spreadsheet_loop.start()

    def cog_unload(self):
        """
        Cancel the loop when the cog unloads
        """
        self.spreadsheet_loop.cancel()

    @tasks.loop(minutes=30.0)
    async def spreadsheet_loop(self):
        """
        Automatically gets the guild and player stats and updates them on the spreadsheet
        """
        self.fff.logger.info("Updating spreadsheet information...")
        await self.spreadsheet.auth()
        users = self.spreadsheet.get_all_users()
        self.spreadsheet.append_row(
            [
                "don't edit",
                "the spreadsheet",
                "right now",
                "or your",
                "changes will",
                "be overwritten",
                "by the",
                "bot -Antonio32A"
            ]
        )

        hypixel_guild = await self.skyblock.get_guild(self.hypixel_guild_id)
        rows = []

        for member in hypixel_guild['members']:
            uuid = member['uuid']
            try:
                username = await self.mojang.get_player_username(uuid)
            except json.decoder.JSONDecodeError:
                # I honestly have no idea why this even happens, but it might just be Mojang rateliminting us
                username = "<UNKNOWN>"

            hypixel_profile = await self.skyblock.get_hypixel_profile(uuid)
            try:
                profiles = await self.skyblock.get_profiles(uuid)
            except Exception as error:
                self.fff.logger.error(error)
                profiles = await self.skyblock.get_profiles("fb768d64953945d495f32691adbb27c5")  # Jayevarmen

            try:
                profile = self.skyblock.calculate_latest_profile(profiles, uuid)
                average_skill_level = self.skyblock.calculate_profile_skills(
                    profile,
                    hypixel_profile,
                    uuid
                )['average_skill_level']
                skill_average = round(float(average_skill_level), 1)
                slayer_xp = self.skyblock.calculate_profile_slayers(profile, uuid)['total']

                if skill_average >= self.min_average_skill_level and slayer_xp >= self.min_total_slayer_xp:
                    passes_reqs = True
                else:
                    passes_reqs = False
            except (KeyError, TypeError, ValueError):
                skill_average = "something"
                slayer_xp = "went"
                passes_reqs = "wrong"

            try:
                discord_connection = hypixel_profile['socialMedia']['links']['DISCORD']
            except KeyError:
                discord_connection = ""

            try:
                paid = users[uuid]['paid']
                paid_to = users[uuid]['paid_to']
            except (TypeError, KeyError):
                paid = False
                paid_to = ""

            await asyncio.sleep(2.5)  # Max 120 requests per minute, so we should send less than 2 per second
            rows.append([uuid, username, discord_connection, paid, paid_to, skill_average, slayer_xp, passes_reqs])
            self.fff.logger.debug(
                f"[{str(len(rows))}] {username} | {uuid} | {discord_connection} | {paid} | {paid_to} | "
                f"{skill_average} | {slayer_xp} | {passes_reqs}"
            )

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
