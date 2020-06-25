import asyncio
import json
from datetime import datetime

from discord.ext import commands, tasks

from util import Handlers


class Tasks(commands.Cog, name="Tasks"):
    """
    This cog handles all the tasks which are executed every x time and stores the data in the database.
    """
    def __init__(self, fff):
        self.fff = fff
        self.skyblock = Handlers.SkyBlock(self.fff.config['hypixel']['key'], self.fff.session)
        self.mojang = Handlers.Mojang(self.fff.session)
        self.spreadsheet = Handlers.Spreadsheet(self.fff.bot_config['spreadsheet_key'])

        self.hypixel_guild_id = self.fff.config['hypixel']['guild_id']
        self.min_total_slayer_xp = self.fff.config['requirements']['min_total_slayer_xp']
        self.min_average_skill_level = self.fff.config['requirements']['min_average_skill_level']
        self.guild_loop.start()

    def cog_unload(self):
        """
        Cancel the loop when the cog unloads
        """
        self.guild_loop.cancel()

    @tasks.loop(minutes=20.0)
    async def guild_loop(self):
        """
        Automatically updates the cache and the database every 20 minutes
        """
        self.fff.logger.info("Caching data and updating the database...")
        await self.spreadsheet.auth()
        users = self.spreadsheet.get_all_users()

        hypixel_guild = await self.skyblock.get_guild(self.hypixel_guild_id)
        data = {}

        for member in hypixel_guild['members']:
            uuid = member['uuid']
            rank = member['rank'].lower()

            try:
                username = await self.mojang.get_player_username(uuid)
            except json.decoder.JSONDecodeError:
                # I honestly have no idea why this even happens, but it might just be Mojang rateliminting us
                username = "<UNKNOWN>"

            try:
                hypixel_profile = await self.skyblock.get_hypixel_profile(uuid)
            except TypeError:
                # I have no idea why this error happens, but if it does I'll just give it the Jayevarmen stats
                hypixel_profile = await self.skyblock.get_hypixel_profile("fb768d64953945d495f32691adbb27c5")

            try:
                profiles = await self.skyblock.get_profiles(uuid)
            except Exception as error:
                self.fff.logger.error(error)
                profiles = await self.skyblock.get_profiles("fb768d64953945d495f32691adbb27c5")  # Jayevarmen

            try:
                profile = self.skyblock.calculate_latest_profile(profiles, uuid)
                cute_name = self.skyblock.get_profile_name(profile)
                average_skill_level = self.skyblock.calculate_profile_skills(
                    profile,
                    hypixel_profile,
                    uuid
                )['average_skill_level']
                skill_level_xp = self.skyblock.calculate_profile_skill_xp(profile, uuid)
                skill_average = round(float(average_skill_level), 1)
                slayer_xp = self.skyblock.calculate_profile_slayers(profile, uuid)['total']

                if skill_average >= self.min_average_skill_level and slayer_xp >= self.min_total_slayer_xp:
                    passes_reqs = True
                else:
                    passes_reqs = False
            except (KeyError, TypeError, ValueError):
                skill_average = None
                slayer_xp = None
                passes_reqs = False
                skill_level_xp = None
                cute_name = None

            try:
                discord_connection = hypixel_profile['socialMedia']['links']['DISCORD']
            except KeyError:
                discord_connection = None

            try:
                paid = users[uuid]['paid']
                paid_to = users[uuid]['paid_to']
            except (TypeError, KeyError):
                paid = False
                paid_to = None

            await asyncio.sleep(2.5)  # Max 120 requests per minute, so we should send less than 2 per second
            data[uuid] = {
                "username": username,
                "discord_connection": discord_connection,
                "rank": rank,
                "paid": paid,
                "paid_to": paid_to,
                "skill_average": skill_average,
                "skill_level_xp": skill_level_xp,
                "slayer_xp": slayer_xp,
                "passes_reqs": passes_reqs,
                "cute_name": cute_name
            }
            if skill_level_xp is not None:
                skill_level_xp = "{...}"

            self.fff.logger.debug(
                f"{username} | {uuid} | {discord_connection} | {rank} | {paid} | "
                f"{paid_to} | {skill_average} | {skill_level_xp} | {slayer_xp} | {passes_reqs}"
            )
        cache = self.fff.cache.get()
        cache['guild_data'] = data

        history_data = data.copy()
        timestamp = datetime.now().timestamp()
        for member in history_data.keys():
            history_data[member]['timestamp'] = int(timestamp)

        try:
            cache['guild_data_history'][str(timestamp)] = history_data
        except KeyError:
            cache['guild_data_history'] = {str(timestamp): history_data}

        async with self.fff.pool.acquire() as conn:
            await self.fff.database.set_guild_data(conn, cache['guild_data'])
            await self.fff.database.set_guild_data_history(conn, cache['guild_data_history'])

            # this formats the data correctly
            guild_data = await self.fff.database.get_guild_data(conn)
            guild_data_history = await self.fff.database.get_guild_data_history(conn)
            self.fff.cache.set(
                {
                    "guild_data": guild_data,
                    "guild_data_history": guild_data_history
                }
            )

        self.fff.logger.info("Successfully updated the cache and the database!")
