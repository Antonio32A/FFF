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
        with open("skills.json") as file:
            self.skill_xp = json.load(file)

    @commands.command()
    async def help(self, ctx):
        """
            TODO: Complete "help" command
        """
        embed = discord.Embed(title="FinalFloorFrags Help Commands!", color=ctx.author.color)
        embed.add_field(name="General Commands:", value="• f!help | Help Command List.\n• f!about | About FFF.\n• f!members | Lists current members.\n", inline=False)
        embed.set_footer(text="FinalFloorFrags © 2020")
        await ctx.send(embed=embed)

    @commands.command()
    async def apply(self, ctx, username: str=None, profile_name: str=None):
        if username == None or profile_name == None:
            return await ctx.send("Invalid arguments. Please specify your username and your profile name.")
        message = await ctx.send("Loading...")
        try:
            profile_name = profile_name.capitalize()
            uuid = await self.api.get_player_uuid(username)
            profile_ids = await self.api.get_skyblock_profile_ids(uuid)
            profile_id = profile_ids[profile_name]
            skin = f"https://minotar.net/helm/{uuid}/100.png"
            profile = await self.api.get_skyblock_profile(uuid, profile_id)
            player = profile["members"][uuid]
        except:
            embed_err = discord.Embed(title=":x: An error has occured!", description="**Your API might be off or the profile name/username might be incorrect**.\nIf the issue presists please contact the developers.", color=ctx.author.color)
            embed_err.set_footer(text="FinalFloorFrags © 2020")
            return await ctx.send(embed=embed_err)

        total_slayer_xp = 0
        try:
            for slayer_boss in player["slayer_bosses"]:
                total_slayer_xp += player["slayer_bosses"][slayer_boss]["xp"]
            slayer_xp_pass = True
        except:
            slayer_xp_pass = False

        try:
            bank = round(float(profile["banking"]["balance"]), 1)
        except:
            embed = discord.Embed(title=":no_entry_sign: Bank API turned OFF.", description="Please turn your Bank API **ON** and retry...", color=ctx.author.color)
            embed.set_footer(text="FinalFloorFrags © 2020")
            await ctx.send(embed=embed)
            return await message.delete()

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
            embed = discord.Embed(title=":no_entry_sign: Skill API turned OFF.", description="Please turn your Skill API **ON** and retry...", color=ctx.author.color)
            embed.set_footer(text="FinalFloorFrags © 2020")
            return await ctx.send(embed=embed)

        last_logged_in = datetime.fromtimestamp(player["last_save"]/1000)
        last_logged_in_diff = datetime.now() - last_logged_in
        embed = discord.Embed(color=ctx.author.color)

        if (slayer_xp_pass == True):
            embed.add_field(name=":knife: | Total Slayer XP", value=f"{total_slayer_xp:,}", inline=False)
        else:
            embed.add_field(name=":knife: | Total Slayer XP", value=total_slayer_xp, inline=False)

        embed.add_field(name=":moneybag: | Bank", value=f"{bank:,}", inline=False)
        embed.add_field(name=":person_juggling: | Average Skill Level", value=str(average_skill_level), inline=False)
        embed.add_field(name=":clock1: | Last logged in", value=f"{round(last_logged_in_diff.total_seconds()/60/60, 1)} hours ago", inline=False)
        embed.set_footer(text="FinalFloorFrags © 2020")
        embed.set_thumbnail(url=skin)
        await ctx.send(embed=embed)
        await message.delete()

        results = await ctx.send("Please wait, checking requirements...")
        if (total_slayer_xp > 100000 and bank > 5000000 and average_skill_level > 20):
            embed = discord.Embed(title=":white_check_mark: Requirement Check **PASSED**!", description="You're eligible to join FinalFloorFrags!\nYou've been added to a wait list queue and will be notified when there is a space.\n\nThanks for applying and have a great day! :heart:", color=ctx.author.color)
            embed.set_footer(text="FinalFloorFrags © 2020")

            category = ctx.guild.get_channel(665859638545219586)
            role = ctx.guild.get_role(654847635118620691)
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            for channel in category.channels:
                if f"applicant-{username}" == channel.name:
                    return await ctx.send("You have already applied. If this is incorrect please contact the developers.")
            send_results = await ctx.guild.create_text_channel(category=category, name=f"applicant-{username}", overwrites=overwrites)
            send_applicant = discord.Embed(title=f"FinalFloorFrags Applicant -> {username} {profile_name}")
            send_applicant.add_field(name=":knife: | Total Slayer XP", value=f"{total_slayer_xp:,}", inline=False)
            send_applicant.add_field(name=":moneybag: | Bank", value=f"{bank:,}", inline=False)
            send_applicant.add_field(name=":person_juggling: | Average Skill Level", value=str(average_skill_level), inline=False)
            embed.add_field(name=":clock1: | Last logged in", value=f"{round(last_logged_in_diff.total_seconds()/60/60, 1)} hours ago", inline=False)
            send_applicant.set_footer(text="FinalFloorFrags © 2020")
            send_applicant.set_thumbnail(url=skin)
            await send_results.send(f"Welcome {ctx.author.mention} to the application process. Here we will ask you a few questions.\n**1.** What is your Skyblock net worth?\n**2.** How much do you play daily?\n**3.** Why should we pick you instead of other people?",
                                    embed=send_applicant)

        else:
            embed = discord.Embed(title=":x: Requirement Check FAILED!", description="Unfortunately at this current moment you dont meet the requirements to join the wait list for FinalFloorFrags, please try again in the future!", color=ctx.author.color)
            embed.add_field(name="Requirements:", value="• 100K+ Slayer XP\n• 5M+ Coins in Bank\n• Average Skill lvl 20^", inline=False)
            embed.set_footer(text="FinalFloorFrags © 2020")

        await ctx.send(embed=embed)
        await results.delete()
