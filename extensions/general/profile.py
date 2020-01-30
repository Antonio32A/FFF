import discord
from discord.ext import commands
import asyncio
import json
from datetime import datetime

from disputils import BotEmbedPaginator
from util import Handlers

class Profile(commands.Cog, name="Profile"):
    def __init__(self, fff):
        self.fff = fff
        self.api = Handlers.Skyblock(self.fff.config["key"])
        with open("skills.json") as file:
            self.skill_xp = json.load(file)
        self.emojis = self.fff.config["emojis"]


    @commands.command()
    async def profile(self, ctx, username: str=None, profile_name: str=None):
        if username == None:
            return await ctx.send("Invalid arguments. Please specify your username.")

        message = await ctx.send("Loading... This might take a few seconds.")
        try:
            uuid = await self.api.get_player_uuid(username)
            profile_ids = await self.api.get_skyblock_profile_ids(uuid)
            embeds = []
        except:
            return await ctx.send("An error has occured!\nYour API might be off, Hypixel/Mojang API might be down or your username is incorrect.")

        if profile_name == None:
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
            return await ctx.send("An error has occured!\nYour API might be off or the profile name/username might be incorrect.")

        # Bank Balance and Fairy Souls
        try:
            bank = round(float(profile["banking"]["balance"]), 1)
        except:
            return await ctx.send("An error has occured!\nPlease turn `Bank` API ON and try again...")

        fairy_souls = player["fairy_souls_collected"]
        bank = f"{self.emojis['bank']} | **Bank Balance:** `{bank:,.0f}`"
        fairy_souls = f"{self.emojis['fairysouls']} | **Fairy Souls:** `{fairy_souls}/190`"

        last_logged_in = datetime.fromtimestamp(player["last_save"]/1000)
        last_logged_in_diff = datetime.now() - last_logged_in
        last_logged_in = f":clock1: | Last logged in {round(last_logged_in_diff.total_seconds()/60/60, 1)} hours ago"

        main = discord.Embed(title=f"{self.emojis['profile']} {username}'s Skyblock Profile.", description=fairy_souls + "\n" + bank + "\n" + last_logged_in, color=ctx.author.color)
        embeds.append(main)

        # Skills
        skills_embed = discord.Embed(title=f"{self.emojis['combat']} {username}'s Skyblock Skills.", color=ctx.author.color)
        skills = ["experience_skill_combat", "experience_skill_mining", "experience_skill_alchemy", "experience_skill_farming", "experience_skill_enchanting", "experience_skill_fishing", "experience_skill_foraging"]
        skill_names = [f"{self.emojis['combat']} | Combat", f"{self.emojis['mining']} | Mining", f"{self.emojis['alchemy']} | Alchemy", f"{self.emojis['farming']} | Farming", f"{self.emojis['enchanting']} | Enchanting", f"{self.emojis['fishing']} | Fishing", f"{self.emojis['foraging']} | Foraging"]
        skill_levels = {}

        for skill in skills:
            xp = player[skill]
            for i in range(50, 0, -1):
                required_xp = self.skill_xp[str(i)]
                if xp > required_xp:
                    skill_levels[skill] = i
                    break

        # Average Skill Level
        average_skill_level = 0.0
        for skill, skill_name in zip(skill_levels, skill_names):
            average_skill_level += skill_levels[skill]
            skills_embed.add_field(name=str(skill_name), value=f"`{str(skill_levels[skill])}`", inline=True)

        skills_embed.add_field(name="\u200B\nTotal Average:", value=f"**{round(average_skill_level/7, 1)}**", inline=False)
        embeds.append(skills_embed)

        # Slayers
        total_slayer_xp = 0
        slayer_bosses = {}
        for slayer_boss in player["slayer_bosses"]:
            money_spent = 0
            tiers = [0, 1, 2, 3]
            tier_money = [100, 2000, 10000, 50000]
            for tier in tiers:
                try:
                    money_spent += player["slayer_bosses"][slayer_boss][f"boss_kills_tier_{tier}"]*tier_money[tier]
                except:
                    pass
            slayer_bosses[slayer_boss] = {"xp": player["slayer_bosses"][slayer_boss]["xp"],
                                            "money_spent": money_spent}
            total_slayer_xp += player["slayer_bosses"][slayer_boss]["xp"]
        slayers = discord.Embed(title=f"{self.emojis['slayer']} {username}'s Skyblock Slayers.", color=ctx.author.color)

        def format_slayer_info(slayer_name: str):
            info = f"XP: {slayer_bosses[slayer_name]['xp']:,.0f}\n" + f"Money Spent: {slayer_bosses[slayer_name]['money_spent']:,.0f}"
            return info

        slayers.add_field(name=f"{self.emojis['zombie']} | Reventant Horror", value=format_slayer_info("zombie"), inline=False)
        slayers.add_field(name=f"{self.emojis['spider']} | Tarantula Broodfather", value=format_slayer_info("spider"), inline=False)
        slayers.add_field(name=f"{self.emojis['wolf']} | Sven Packmaster", value=format_slayer_info("wolf"), inline=False)
        embeds.append(slayers)

        await message.delete()
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()
