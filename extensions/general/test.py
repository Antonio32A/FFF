import discord
from discord.ext import commands
import asyncio
import json
from datetime import datetime

from util import Handlers

class Test(commands.Cog, name="General"):
    def __init__(self, fff):
        self.fff = fff
        self.api = Handlers.Skyblock(self.fff.config["key"])
        with open("skills.json") as file:
            self.skill_xp = json.load(file)


    @commands.command()
    async def test(self, ctx):
        final = "results:\n\t"
        usernames = (await self.api.get_guild("5def87fe8ea8c92086b0f96a"))["members"]
        for username in usernames:
            username = username["uuid"]
            await ctx.send("checking " + username)
            try:
                #uuid = await self.api.get_player_uuid(username)
                uuid = username
                profile_ids = await self.api.get_skyblock_profile_ids(uuid)
            except:
                await ctx.send(f"{username} - api off")
                final += f"{username} - api off\n\t"
                continue

            profile_timestamps = {}
            for profile_id in profile_ids:
                profile = await self.api.get_skyblock_profile(uuid, profile_ids[profile_id])
                last_save = profile["members"][uuid]["last_save"]
                last_save = datetime.fromtimestamp(last_save/1000)
                last_save_diff = (datetime.now() - last_save).total_seconds()
                profile_timestamps[profile_id] = last_save_diff
            profile_name = min(profile_timestamps, key=profile_timestamps.get)

            try:
                profile_name = profile_name.capitalize()
                profile_id = profile_ids[profile_name]
                profile = await self.api.get_skyblock_profile(uuid, profile_id)
                player = profile["members"][uuid]
            except:
                await ctx.send(f"{username} - api off")
                final += f"{username} - api off\n\t"
                continue

            try:
                skills = ["experience_skill_combat", "experience_skill_mining", "experience_skill_alchemy", "experience_skill_farming", "experience_skill_enchanting", "experience_skill_fishing", "experience_skill_foraging"]
                skill_levels = {}
                for skill in skills:
                    xp = player[skill]
                    for i in range(50, 0, -1):
                        required_xp = self.skill_xp[str(i)]
                        if xp > required_xp:
                            skill_levels[skill] = i
                            break

                average_skill_level = 0.0
                for skill in skill_levels:
                    average_skill_level += skill_levels[skill]

                average_skill_level = round(average_skill_level/7, 1)
            except:
                await ctx.send(f"{username} - api off")
                final += f"{username} - api off\n\t"
                continue

            total_slayer_xp = 0
            slayer_bosses = {}
            for slayer_boss in player["slayer_bosses"]:
                total_slayer_xp += player["slayer_bosses"][slayer_boss]["xp"]

            if (average_skill_level < 23.0) or (total_slayer_xp < 400000):
                await ctx.send(f"{username} -> Skills: {str(average_skill_level)} Slayer: {str(total_slayer_xp)}")
                final += f"{username} -> Skills: {str(average_skill_level)} Slayer: {str(total_slayer_xp)}\n\t"
        print("done")
        await ctx.send(final)
