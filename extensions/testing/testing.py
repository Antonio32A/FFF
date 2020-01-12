import discord
from discord.ext import commands
import asyncio
import json
from datetime import datetime

from util import Handlers

class Testing(commands.Cog, name="Testing"):
    def __init__(self, fff):
        self.fff = fff
        self.api = Handlers.Skyblock(self.fff.config["key"])

    @commands.command()
    async def test(self, ctx, username: str, profile_name: str):
        message = await ctx.send("Loading...")
        uuid = await self.api.get_player_uuid(username)
        profile_ids = await self.api.get_skyblock_profile_ids(uuid)
        profile_id = profile_ids[profile_name]
        skin = f"https://minotar.net/helm/{uuid}/100.png"
        profile = await self.api.get_skyblock_profile(uuid, profile_id)
        player = profile["members"][uuid]

        total_slayer_xp = 0
        for slayer_boss in player["slayer_bosses"]:
            total_slayer_xp += player["slayer_bosses"][slayer_boss]["xp"]

        purse = round(float(player["coin_purse"]), 1)
        bank = round(float(profile["banking"]["balance"]), 1)

        skills = ["experience_skill_combat", "experience_skill_mining", "experience_skill_alchemy", "experience_skill_farming", "experience_skill_enchanting", "experience_skill_fishing", "experience_skill_foraging"]
        skill_levels = {}
        with open("skills.json") as file:
            skill_xp = json.load(file)

        for skill in skills:
            xp = player[skill]
            for i in range(50, 0, -1):
                required_xp = skill_xp[str(i)]
                if xp > required_xp:
                    skill_levels[skill] = i
                    break

        average_skill_level = 0.0
        for skill in skill_levels:
            average_skill_level += skill_levels[skill]
        average_skill_level = round(average_skill_level/7, 1)

        last_logged_in = datetime.fromtimestamp(player["last_save"]/1000)
        last_logged_in_diff = datetime.now() - last_logged_in
        embed = discord.Embed(color=ctx.author.color)
        embed.add_field(name=":knife: | Total Slayer XP", value=f"{total_slayer_xp:,}", inline=False)
        embed.add_field(name=":dollar: | Purse", value=f"{purse:,}", inline=False)
        embed.add_field(name=":moneybag: | Bank", value=f"{bank:,}", inline=False)
        embed.add_field(name=":person_juggling: | Average Skill Level", value=str(average_skill_level), inline=False)
        embed.add_field(name=":clock1: | Last logged in", value=f"{round(last_logged_in_diff.total_seconds()/60/60, 1)} hours ago")
        embed.set_thumbnail(url=skin)
        await ctx.send(embed=embed)
        await message.delete()
