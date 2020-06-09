import json
from datetime import datetime

import discord
from discord.ext import commands

from util import Handlers, Embed


class Applications(commands.Cog, name="Applications"):
    """
    This cog adds Hypixel SkyBlock guild apply commands
    """
    def __init__(self, fff):
        self.fff = fff
        self.skyblock = Handlers.SkyBlock(self.fff.config['hypixel']['key'], self.fff.session)
        self.mojang = Handlers.Mojang(self.fff.session)
        self.applicant_category = self.fff.config['discord_guild']['applicant_category']
        self.apply_channel = self.fff.config['discord_guild']['apply_channel']
        self.staff_role = self.fff.config['discord_guild']['staff_role']
        self.min_total_slayer_xp = self.fff.config['requirements']['min_total_slayer_xp']
        self.min_bank = self.fff.config['requirements']['min_bank']
        self.min_average_skill_level = self.fff.config['requirements']['min_average_skill_level']

    @commands.command()
    async def apply(self, ctx, username: str = None):
        """
        Apply to the FinalFloorFrags guild
        """
        if not ctx.channel.id == self.apply_channel:
            return

        if username is None:
            return await ctx.send("Invalid arguments. Please specify your username")
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
        total_slayer_xp = self.skyblock.calculate_profile_slayers(profile, uuid)['total']
        average_skill_level = self.skyblock.calculate_profile_skills(
            profile,
            hypixel_profile,
            uuid
        )['average_skill_level']
        average_skill_level = round(float(average_skill_level), 1)

        try:
            bank = round(float(profile['banking']['balance']), 1)
        except KeyError:
            embed = Embed(
                title=":no_entry_sign: Bank API turned OFF.",
                description="Please turn your Bank API **ON** and retry...",
                color=ctx.author.color
            )
            await ctx.send(embed=embed)
            return await message.delete()

        last_logged_in = datetime.fromtimestamp(profile['members'][uuid]['last_save'] / 1000)
        last_logged_in_diff = datetime.now() - last_logged_in
        embed = Embed(color=ctx.author.color)

        embed.add_field(name=":knife: | Total Slayer XP", value=f"{total_slayer_xp:,}", inline=False)
        embed.add_field(name=":moneybag: | Bank", value=f"{bank:,}", inline=False)
        embed.add_field(name=":person_juggling: | Average Skill Level", value=str(average_skill_level), inline=False)
        embed.add_field(
            name=":clock1: | Last logged in",
            value=f"{round(last_logged_in_diff.total_seconds() / 60 / 60, 1)} hours ago",
            inline=False)
        embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/100.png")
        await ctx.send(embed=embed)
        await message.delete()

        results = await ctx.send("Please wait, checking requirements...")
        if (total_slayer_xp >= self.min_total_slayer_xp
                and bank >= self.min_bank
                and average_skill_level >= self.min_average_skill_level):
            embed = Embed(
                title=":white_check_mark: Requirement Check **PASSED**!",
                description="You're eligible to join FinalFloorFrags!\n"
                            "You've been added to a wait list queue and will be notified when there is a space.\n\n"
                            "Thanks for applying and have a great day! :heart:",
                color=ctx.author.color
            )

            category = ctx.guild.get_channel(self.applicant_category)
            role = ctx.guild.get_role(self.staff_role)
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            for channel in category.channels:
                if f"applicant-{username}" == channel.name:
                    return await ctx.send(
                        "You have already applied. If this is incorrect please contact the developers."
                    )
            send_results = await ctx.guild.create_text_channel(
                category=category,
                name=f"applicant-{username}",
                overwrites=overwrites
            )

            send_applicant = Embed(title=f"FinalFloorFrags Applicant -> {username} {profile['cute_name']}")
            send_applicant.add_field(name=":knife: | Total Slayer XP", value=f"{total_slayer_xp:,}", inline=False)
            send_applicant.add_field(name=":moneybag: | Bank", value=f"{bank:,}", inline=False)
            send_applicant.add_field(
                name=":person_juggling: | Average Skill Level",
                value=str(average_skill_level),
                inline=False
            )
            embed.add_field(
                name=":clock1: | Last logged in",
                value=f"{round(last_logged_in_diff.total_seconds() / 60 / 60, 1)} hours ago",
                inline=False
            )

            send_applicant.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/100.png")
            await send_results.send(
                f"Welcome {ctx.author.mention} to the application process. Here we will ask you a few questions.\n"
                "**1.** What is your SkyBlock networth?\n"
                "**2.** How much do you play daily?\n"
                "**3.** Why should we pick you instead of other people?",
                embed=send_applicant
            )

        else:
            embed = Embed(
                title=":x: Requirement Check FAILED!",
                description="Unfortunately at this current moment you don't meet the requirements to join"
                            " the wait list for FinalFloorFrags, please try again in the future!\n"
                            "Check the #next-purge channel for the requirements!",
                color=ctx.author.color
            )

        await ctx.send(embed=embed)
        await results.delete()
