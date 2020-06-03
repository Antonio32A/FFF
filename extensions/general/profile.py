import discord
from discord.ext import commands
from datetime import datetime
import json

from disputils import BotEmbedPaginator
from util import Handlers


def insert(source_str: str, insert_str: str, pos: int):
    return source_str[:pos] + insert_str + source_str[pos:]


class Profile(commands.Cog, name="Profile"):
    """
    This cog adds a profile command which shows your SkyBlock stats
    """

    def __init__(self, fff):
        self.fff = fff
        self.skyblock = Handlers.SkyBlock(self.fff.config['key'])
        self.mojang = Handlers.Mojang()
        self.emojis = self.fff.config['emojis']

    @commands.command()
    async def profile(self, ctx, username: str = None):
        """
        Display information about somebody's Hypixel SkyBlock profile
        """
        if username is None:
            return await ctx.send("Invalid arguments. Please specify the argument username.")

        embeds = []
        message = await ctx.send("Loading... Fetching UUID and profiles...")

        try:
            uuid = await self.mojang.get_player_uuid(username)
        except json.decoder.JSONDecodeError:
            await message.delete()
            return await ctx.send("That username doesn't exist!")

        profiles = await self.skyblock.get_profiles(uuid)
        hypixel_profile = await self.skyblock.get_hypixel_profile(uuid)
        if not profiles:
            await message.delete()
            return await ctx.send("That person doesn't have any profiles!")
        await message.edit(content="Loading... Fetched UUID and profiles, calculating...")

        profile = self.skyblock.calculate_latest_profile(profiles, uuid)
        player_profile = profile['members'][uuid]

        skills_data = self.skyblock.calculate_profile_skills(profile, hypixel_profile, uuid)
        slayers_data = self.skyblock.calculate_profile_slayers(profile, uuid)
        pets_data = self.skyblock.calculate_profile_pets(profile, uuid)
        await message.edit(content="Loading... Successfully calculated the data, creating embeds...")

        main_text = ""
        try:
            bank_data = round(float(profile['banking']['balance']), 1)
            main_text += f"{self.emojis['bank']} | **Bank Balance:** `{bank_data:,.0f}`\n"
        except KeyError:
            pass

        try:
            fairy_souls_data = player_profile['fairy_souls_collected']
        except KeyError:
            fairy_souls_data = 0
        main_text += f"{self.emojis['fairysouls']} | **Fairy Souls:** `{fairy_souls_data}/194`\n"

        last_logged_in = datetime.fromtimestamp(player_profile['last_save'] / 1000)
        last_logged_in_diff = datetime.now() - last_logged_in
        main_text += f":clock1: | Last logged in {round(last_logged_in_diff.total_seconds() / 3600, 1)} hours ago"

        main = discord.Embed(
            title=f"{self.emojis['profile']} {username}'s Skyblock Profile.",
            description=main_text,
            color=ctx.author.color
        )
        embeds.append(main)

        skills_embed = discord.Embed(
            title=f"{self.emojis['combat']} {username}'s Skyblock Skills.",
            color=ctx.author.color
        )

        skill_names = {
            "experience_skill_combat": f"{self.emojis['combat']} | Combat",
            "experience_skill_mining": f"{self.emojis['mining']} | Mining",
            "experience_skill_alchemy": f"{self.emojis['alchemy']} | Alchemy",
            "experience_skill_farming": f"{self.emojis['farming']} | Farming",
            "experience_skill_enchanting": f"{self.emojis['enchanting']} | Enchanting",
            "experience_skill_fishing": f"{self.emojis['fishing']} | Fishing",
            "experience_skill_foraging": f"{self.emojis['foraging']} | Foraging"
        }

        for skill in skills_data.keys():
            if not skill == "average_skill_level":
                skill_name = skill_names[skill]
                skill_level = skills_data[skill]
                skills_embed.add_field(name=skill_name, value=f"`{str(skill_level)}`", inline=True)

        skills_embed.add_field(
            name="\u200B\nTotal Average:",
            value=f"**{round(skills_data['average_skill_level'], 1)}**\n\n"
                  "Note: If the person has the skill API off, the skills will be calculated based on achievements.",
            inline=False
        )
        embeds.append(skills_embed)

        slayers = discord.Embed(title=f"{self.emojis['slayer']} {username}'s Skyblock Slayers.", color=ctx.author.color)

        def format_slayer_info(slayer_name: str):
            info = f"XP: {slayers_data[slayer_name]['xp']:,.0f}\n" \
                   f"Money Spent: {slayers_data[slayer_name]['money_spent']:,.0f}"
            return info

        slayers.add_field(
            name=f"{self.emojis['zombie']} | Reventant Horror", value=format_slayer_info("zombie"),
            inline=False
        )
        slayers.add_field(
            name=f"{self.emojis['spider']} | Tarantula Broodfather", value=format_slayer_info("spider"),
            inline=False
        )
        slayers.add_field(
            name=f"{self.emojis['wolf']} | Sven Packmaster", value=format_slayer_info("wolf"),
            inline=False
        )
        slayers.add_field(name=f"{self.emojis['slayer']} | Total Slayer XP", value=f"{slayers_data['total']:,.0f}")
        embeds.append(slayers)

        pet_text = ""
        for pet in pets_data.keys():
            name = pet
            pet = pets_data[pet]
            text = f"[{str(pet['level'])}] {name} - {pet['rarity']}"
            if pet['held_item']:
                text += f" - {pet['held_item']}"
            if pet['active']:
                text = "**" + text + "**"
            pet_text += text + "\n"

        pet_embed = discord.Embed(title=f"{username}'s Pets", color=ctx.author.color)
        pet_embed.description = pet_text
        embeds.append(pet_embed)

        await message.delete()
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()
