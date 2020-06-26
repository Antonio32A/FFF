import json
import os
import random
from datetime import datetime

import discord
import matplotlib.pyplot as plt
from discord.ext import commands

from util import Handlers, Embed


def find_by_uuid(_list: list, uuid: str):
    """
    Finds a user in a leaderboard by their uuid
    :param (list) _list: The leaderboard list
    :param (str) uuid: Player's UUID
    :returns (int) i: Placing of a user in the leaderboard
    """
    for i, dic in enumerate(_list):
        if dic['uuid'] == uuid:
            return i
    return -1


class Contest(commands.Cog, name="Contest"):
    """
    Contest leaderboards, graphs and more
    """

    def __init__(self, fff):
        self.fff = fff
        self.mojang = Handlers.Mojang(self.fff.session)
        self.skills = self.fff.config['contest']['enabled_skills']
        self.slayer_enabled = self.fff.config['contest']['slayer_enabled']
        self.emojis = self.fff.config['discord_guild']['emojis']
        self.matplotlib_colors = [
            "springgreen",
            "tomato",
            "gold",
            "royalblue",
            "darkviolet",
            "magenta",
            "saddlebrown",
            "red",
            "orangered",
            "black"
        ]

    def get_player_history(self, uuid: str, cute_name: str):
        """
        Gets somebody player data history from the guild_data_history cache
        :param (str) uuid: Player's UUID
        :param (str) cute_name: Player's Hypixel SkyBlock profile cute name
        :returns (dict) player_history: Player's history data
        """
        guild_history_data = self.fff.cache.get()['guild_data_history']
        player_history = {}
        for timestamp, guild_data in guild_history_data.items():
            try:
                if guild_data[uuid]['cute_name'] == cute_name:
                    player_history[timestamp] = guild_data[uuid]
            except KeyError:
                pass

        return player_history

    @staticmethod
    def sort_player_history(player_history: dict):
        """
        Sorts the player history data which you can get from get_player_history
        :param (dict) player_history: Player history data to sort
        :returns (list) sorted_player_history: A sorted list based on the timestamps from newest to oldest
        """
        sorted_player_history = []
        timestamps = list(player_history.keys())
        for _, timestamp in enumerate(timestamps):
            if type(timestamp) == "str":
                timestamps[_] = round(timestamp)

        timestamps.sort(reverse=True)
        for timestamp in timestamps:
            sorted_player_history.append(player_history[timestamp])
        return sorted_player_history

    def get_leaderboard_for_skill(self, skill: str):
        """
        Gets a leaderboard for a single skill or all
        :param (str) skill: The skill name, specify "all" to get all skills
        :returns (list) leaderboard: A list containing their UUID, cute_name, xp_gained, timestamps,
                                     skill_history and skill_gained_history
        """
        uuids = []
        leaderboard = []
        guild_data = self.fff.cache.get()['guild_data']
        for uuid, data in guild_data.items():
            uuids.append(
                {
                    "uuid": uuid,
                    "cute_name": data['cute_name']
                }
            )

        for data in uuids:
            uuid = data['uuid']
            cute_name = data['cute_name']
            history = self.get_player_history(uuid, cute_name)
            history = self.sort_player_history(history)

            skills = []
            timestamps = []
            skill_gained_history = []
            for historic_data in history:
                if historic_data['skill_level_xp'] is not None:
                    skills.append(historic_data['skill_level_xp'])
                    timestamps.append(historic_data['timestamp'])

            if not skills:
                continue

            xp_gained = 0
            if skill == "all":
                for skill_name in self.skills:
                    xp_gained += skills[0][skill_name] - skills[-1][skill_name]
            else:
                xp_gained = skills[0][skill] - skills[-1][skill]

            for skill_data in skills:
                _xp_gained = 0
                for skill_name in self.skills:
                    _xp_gained += skills[0][skill_name] - skill_data[skill_name]
                skill_gained_history.append(_xp_gained)

            leaderboard.append(
                {
                    "uuid": uuid,
                    "cute_name": data['cute_name'],
                    "xp_gained": xp_gained,
                    "timestamps": timestamps,
                    "skill_history": skills,
                    "skill_gained_history": skill_gained_history
                }
            )

        leaderboard = sorted(leaderboard, key=lambda k: k['xp_gained'], reverse=True)
        return leaderboard

    def get_slayer_leaderboard(self):
        """
        Gets the whole slayer leaderboard
        :returns (list) leaderboard: A list containing all UUIDs, cute_names, xp_gained, timestamps and slayer_histories
        """
        uuids = []
        leaderboard = []
        guild_data = self.fff.cache.get()['guild_data']
        for uuid, data in guild_data.items():
            uuids.append(
                {
                    "uuid": uuid,
                    "cute_name": data['cute_name']
                }
            )

        for data in uuids:
            uuid = data['uuid']
            cute_name = data['cute_name']
            history = self.get_player_history(uuid, cute_name)
            history = self.sort_player_history(history)

            slayer = []
            timestamps = []
            for historic_data in history:
                if historic_data['slayer_xp']:
                    slayer.append(historic_data['slayer_xp'])
                    timestamps.append(historic_data['timestamp'])

            if not slayer:
                continue
            xp_gained = slayer[0] - slayer[-1]

            leaderboard.append(
                {
                    "uuid": uuid,
                    "cute_name": data['cute_name'],
                    "xp_gained": xp_gained,
                    "timestamps": timestamps,
                    "slayer_history": slayer
                }
            )

        leaderboard = sorted(leaderboard, key=lambda k: k['xp_gained'], reverse=True)
        return leaderboard

    @commands.group()
    async def contest(self, ctx):
        """
        The contest command group, if no subcommand is provided, the command help will be sent
        """
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @contest.command()
    async def player(self, ctx, username: str):
        """
        Gets somebody's contest ranking from their username
        """
        guild_data = self.fff.cache.get()['guild_data']
        try:
            uuid = await self.mojang.get_player_uuid(username)
        except json.decoder.JSONDecodeError:
            return await ctx.send("That player doesn't exist!")

        try:
            cute_name = guild_data[uuid]['cute_name']
        except KeyError:
            return await ctx.send("No data available for this player. (The player is probably not in the guild)")
        history = self.get_player_history(uuid, cute_name)
        history = self.sort_player_history(history)

        skills = []
        slayer = []
        for historic_data in history:
            if historic_data['skill_level_xp'] is not None:
                skills.append(historic_data['skill_level_xp'])
            if historic_data['slayer_xp'] is not None:
                slayer.append(historic_data['slayer_xp'])

        embed = Embed(title="Contest player stats", color=ctx.author.color)
        if slayer and self.slayer_enabled:
            xp_gained = slayer[0] - slayer[-1]
            placing = find_by_uuid(self.get_slayer_leaderboard(), uuid)
            embed.add_field(name="Slayer", value=f"{xp_gained:,} XP (#{placing + 1})", inline=False)
        else:
            embed.add_field(
                name="No slayer data",
                value="No slayer data available for this player or slayer isn't counted this contest.",
                inline=False
            )

        if skills and self.skills:
            skill_names = {
                "experience_skill_combat": f"{self.emojis['combat']} | Combat",
                "experience_skill_mining": f"{self.emojis['mining']} | Mining",
                "experience_skill_alchemy": f"{self.emojis['alchemy']} | Alchemy",
                "experience_skill_farming": f"{self.emojis['farming']} | Farming",
                "experience_skill_enchanting": f"{self.emojis['enchanting']} | Enchanting",
                "experience_skill_fishing": f"{self.emojis['fishing']} | Fishing",
                "experience_skill_foraging": f"{self.emojis['foraging']} | Foraging",
                "experience_skill_taming": f"{self.emojis['taming']} | Taming"
            }

            for skill in self.skills:
                name = skill_names[skill]
                xp_gained = skills[0][skill] - skills[-1][skill]
                placing = find_by_uuid(self.get_leaderboard_for_skill(skill), uuid)
                embed.add_field(
                    name=name,
                    value=f"{xp_gained:,} XP (#{placing + 1})",
                    inline=False
                )

            xp_gained = 0
            for skill_name in self.skills:
                xp_gained += skills[0][skill_name] - skills[-1][skill_name]

            placing = find_by_uuid(self.get_leaderboard_for_skill("all"), uuid)

            embed.add_field(
                name="Total XP",
                value=f"{xp_gained:,} XP (#{placing + 1})",
                inline=False
            )
        else:
            embed.add_field(
                name="Skill API OFF",
                value="Please enable the skill API so we can track your stats or skills aren't counted this contest.",
                inline=False
            )
        await ctx.send(embed=embed)

    @contest.group(aliases=["lb"])
    async def leaderboard(self, ctx):
        """
        Multiple leaderboard commands
        """
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @leaderboard.command()
    async def skill(self, ctx, skill: str = "all"):
        """
        Shows the skill leaderboard for a skill, specify "all" for all skills
        """
        if not self.skills:
            return await ctx.send("Skills aren't counted this contest.")

        if skill == "all":
            embed = Embed(title=f"Skill Leaderboard (Top 10)", color=ctx.author.color)
        else:
            embed = Embed(title=f"Top 10 players in skill {skill}", color=ctx.author.color)
            skill = "experience_skill_" + skill
            if skill not in self.skills:
                return await ctx.send("That skill doesn't exist or it is not counted this contest.")

        guild_data = self.fff.cache.get()['guild_data']
        data = self.get_leaderboard_for_skill(skill)
        embed.description = ""

        for place in range(10):
            uuid = data[place]['uuid']
            username = guild_data[uuid]['username']
            embed.description += f"{place + 1}. {username} - {data[place]['xp_gained']:,} XP\n"

        await ctx.send(embed=embed)

    @leaderboard.command()
    async def slayer(self, ctx):
        """
        Shows the slayer leaderboard
        """
        if not self.slayer_enabled:
            return await ctx.send("Slayer isn't counted in this contest.")
        embed = Embed(title=f"Slayer Leaderboard (Top 10)", color=ctx.author.color)
        guild_data = self.fff.cache.get()['guild_data']
        data = self.get_slayer_leaderboard()
        embed.description = ""

        for place in range(10):
            uuid = data[place]['uuid']
            username = guild_data[uuid]['username']
            embed.description += f"{place + 1}. {username} - {data[place]['xp_gained']:,} XP\n"

        await ctx.send(embed=embed)

    @contest.group()
    async def graph(self, ctx):
        """
        Multiple graph commands
        """
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @graph.command(name="slayer")
    async def _slayer(self, ctx, username: str = "top"):
        """
        Shows a slayer graph for a player, defaults to "top" which shows the top 10 people's slayer in a graph
        """
        if not self.slayer_enabled:
            return await ctx.send("Slayer isn't counted in this contest.")

        fig, ax = plt.subplots()
        guild_data = self.fff.cache.get()['guild_data']

        if username == "top":
            data = self.get_slayer_leaderboard()[:10]
            message = ""

            place = 0
            for player in data:
                uuid = player['uuid']
                try:
                    username = guild_data[uuid]['username']
                except KeyError:
                    username = "Player left the guild"

                color = self.matplotlib_colors[place]

                timestamps = []
                for timestamp in player['timestamps']:
                    timestamps.append(datetime.fromtimestamp(timestamp))

                xp_gained_history = []
                for xp in player['slayer_history']:
                    xp_gained_history.append(player['slayer_history'][0] - xp)
                xp_gained_history.reverse()

                message += f"{place + 1}. {username} - {data[place]['xp_gained']:,} XP (`{color}`)\n"
                plt.plot(timestamps, xp_gained_history, linestyle="-", color=color)
                place += 1
        else:
            try:
                uuid = await self.mojang.get_player_uuid(username)
            except json.decoder.JSONDecodeError:
                return await ctx.send("That player doesn't exist!")

            try:
                cute_name = guild_data[uuid]['cute_name']
            except KeyError:
                return await ctx.send("No data available for this player. (The player is probably not in the guild)")
            history = self.get_player_history(uuid, cute_name)
            history = self.sort_player_history(history)

            xp_gained_history = []
            timestamps = []
            for historic_data in history:
                if historic_data['slayer_xp'] is not None:
                    xp_gained_history.append(
                        history[0]['slayer_xp'] - historic_data['slayer_xp']
                    )
                    timestamps.append(datetime.fromtimestamp(historic_data['timestamp']))

            xp_gained_history.reverse()

            if xp_gained_history and self.slayer_enabled:
                plt.plot(timestamps, xp_gained_history, linestyle="-", color=random.choice(self.matplotlib_colors))
            else:
                return await ctx.send("No slayer data available for this player or slayer isn't counted this contest.")
            message = f"{username} - {xp_gained_history[0]:,} XP"

        plt.setp(ax.xaxis.get_majorticklabels(), rotation=90)
        plt.title("Slayer XP Gained Graph")
        plt.gcf().subplots_adjust(bottom=0.30)
        plt.savefig("graph.png")

        await ctx.channel.send(content=message, file=discord.File("graph.png"))
        os.remove("graph.png")

    @graph.command(name="skill")
    async def _skill(self, ctx, username: str = "top"):
        """
        Shows a skill graph for a player, defaults to "top" which shows the top 10 people's skills in a graph
        """
        if not self.skills:
            return await ctx.send("Skills aren't counted in this contest.")

        fig, ax = plt.subplots()
        guild_data = self.fff.cache.get()['guild_data']

        if username == "top":
            data = self.get_leaderboard_for_skill("all")[:10]
            message = ""

            place = 0
            for player in data:
                uuid = player['uuid']
                try:
                    username = guild_data[uuid]['username']
                except KeyError:
                    username = "Player left the guild"

                color = self.matplotlib_colors[place]

                timestamps = []
                for timestamp in player['timestamps']:
                    timestamps.append(datetime.fromtimestamp(timestamp))

                xp_gained_history = []
                for xp in player['skill_gained_history']:
                    xp_gained_history.append(xp - player['skill_gained_history'][0])
                xp_gained_history.reverse()

                message += f"{place + 1}. {username} - {data[place]['xp_gained']:,} XP (`{color}`)\n"
                plt.plot(timestamps, xp_gained_history, linestyle="-", color=color)
                place += 1
        else:
            try:
                uuid = await self.mojang.get_player_uuid(username)
            except json.decoder.JSONDecodeError:
                return await ctx.send("That player doesn't exist!")

            try:
                cute_name = guild_data[uuid]['cute_name']
            except KeyError:
                return await ctx.send("No data available for this player. (The player is probably not in the guild)")
            history = self.get_player_history(uuid, cute_name)
            history = self.sort_player_history(history)

            timestamps = []
            for historic_data in history:
                if historic_data['skill_level_xp'] is not None:
                    timestamps.append(datetime.fromtimestamp(historic_data['timestamp']))

            message = ""
            for skill in self.skills:
                xp_gained_history = []
                for historic_data in history:
                    if historic_data['skill_level_xp'] is None:
                        continue
                    xp_gained = history[0]['skill_level_xp'][skill] - historic_data['skill_level_xp'][skill]
                    xp_gained_history.append(xp_gained)

                xp_gained_history.reverse()
                if list(set(xp_gained_history)) == [0]:
                    continue

                color = random.choice(self.matplotlib_colors)
                plt.plot(timestamps, xp_gained_history, linestyle="-", color=color)
                skill_name = skill.split("experience_skill_")[1].title()
                message += f"{skill_name} - {xp_gained_history[0]:,} ({color}) \n"

        plt.setp(ax.xaxis.get_majorticklabels(), rotation=90)
        plt.title("Skill XP Gained Graph")
        plt.gcf().subplots_adjust(bottom=0.30)
        plt.savefig("graph.png")

        await ctx.channel.send(content=message, file=discord.File("graph.png"))
        os.remove("graph.png")
