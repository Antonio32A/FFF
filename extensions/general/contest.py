import discord
from discord.ext import commands
import asyncio
import json
from datetime import datetime
import pytz
import mysql.connector

from util import Handlers

class Contest(commands.Cog, name="Contest"):
    def __init__(self, fff):
        self.fff = fff
        self.api = Handlers.Skyblock(self.fff.config["key"])

    @commands.command(hidden=True, aliases=["competition"])
    async def contest(self, ctx, arg1: str=None, arg2: str=None):
        data = Handlers.JSON.read("config")
        table = self.fff.config["contest_table"]

        if data["contest_active"] != True:
            return await ctx.send("There is no FFF contest active at the moment.")

        if arg1 == None or arg1.lower() == "help":
            description = "**f!contest help:** Show the available contest commands\n\n"
            description += "**f!contest leaderboard:** Show a leaderboard all player's xp gained\n\n"
            description += "**f!contest top <farming/foraging/mining/combat/fishing>:** Show a leaderboard of players according to skill type\n\n"
            description += "**f!contest player <ign>:** Show a player's progress for the active contest"
            embed = discord.Embed(title="Available Contest Commands", description=description, color=ctx.author.color)
            embed.set_footer(text="FinalFloorFrags © 2020")
            return await ctx.send(embed=embed)

        arg1 = arg1.lower()

        if arg1 not in ["top", "player", "leaderboard"]:
            description = "**f!contest help:** Show the available contest commands\n\n"
            description += "**f!contest leaderboard:** Show a leaderboard all player's xp gained\n\n"
            description += "**f!contest top <farming/foraging/mining/combat/fishing>:** Show a leaderboard of players according to skill type\n\n"
            description += "**f!contest player <ign>:** Show a player's progress for the active contest"
            embed = discord.Embed(title=":x: Invalid Contest Command!", description="Please refer to the valid commands below.\n\n" + description, color=ctx.author.color)
            embed.set_footer(text="FinalFloorFrags © 2020")
            return await ctx.send(embed=embed)

        message = await ctx.send("Loading...")

        db = mysql.connector.connect(
            host="localhost",
            port="8889",
            user="root",
            passwd="root",
            database="contest"
        )

        cursor = db.cursor()

        ends_object = datetime.strptime(data["contest_ends"], '%d/%m/%y %H:%M:%S')
        now_object = datetime.utcnow().replace(tzinfo=pytz.timezone("Europe/Madrid"))
        diff = str(ends_object.replace(tzinfo=pytz.timezone("Europe/Madrid")) - now_object).split(".")[0] + " remaining"

        if arg1 == "player":
            if arg2 == None:
                embed = discord.Embed(title="Please use the correct command syntax!", description="f!contest player <ign>", color=ctx.author.color)
                embed.set_footer(text="FinalFloorFrags © 2020")
                db.close()
                return await message.edit(content=str(ctx.author.mention), embed=embed)
            cursor.execute("SELECT * FROM %s WHERE username = '%s'" % (table, arg2))
            result = cursor.fetchall()
            if len(result) < 1:
                embed = discord.Embed(title="Error", description="This player is not participating in the active contest.", color=ctx.author.color)
                embed.set_footer(text="FinalFloorFrags © 2020")
                db.close()
                return await message.edit(content=str(ctx.author.mention), embed=embed)
            name = result[0][4]
            uuid = result[0][1]
            profile = result[0][3]
            totalxp = result[0][15]
            farming = result[0][10] - result[0][5]
            foraging = result[0][11] - result[0][6]
            mining = result[0][12] - result[0][7]
            combat = result[0][13] - result[0][8]
            fishing = result[0][14] - result[0][9]
            position = result[0][16]

            embed = discord.Embed(title="%s's contest stats on %s" % (name, profile), description=diff, color=ctx.author.color)
            embed.add_field(name="Global position", value="**#%s**" % position, inline=False)
            embed.add_field(name="Total xp gained", value=f"{totalxp:,.0f}", inline=False)
            embed.add_field(name="Farming xp gained", value=f"{farming:,.0f}", inline=True)
            embed.add_field(name="Foraging xp gained", value=f"{foraging:,.0f}", inline=True)
            embed.add_field(name="Mining xp gained", value=f"{mining:,.0f}", inline=True)
            embed.add_field(name="Combat xp gained", value=f"{combat:,.0f}", inline=True)
            embed.add_field(name="Fishing xp gained", value=f"{fishing:,.0f}", inline=True)
            embed.set_footer(text="FinalFloorFrags © 2020")
            embed.set_thumbnail(url="https://minotar.net/cube/" + uuid)
            db.close()
            return await message.edit(content=str(ctx.author.mention), embed=embed)

        elif arg1 == "top":
            if arg2 == None or arg2.lower() not in ["farming", "foraging", "mining", "combat", "fishing"]:
                embed = discord.Embed(title="Please use the correct command syntax!", description="f!contest top <farming/foraging/mining/combat/fishing>", color=ctx.author.color)
                embed.set_footer(text="FinalFloorFrags © 2020")
                db.close()
                return await ctx.send(content=str(ctx.author.mention), embed=embed)
            skill = arg2.lower()
            cursor.execute("SELECT *, current_%s - start_%s as difference FROM %s ORDER BY difference DESC" % (skill, skill, table))
            result = cursor.fetchall()
            content = "\n\n```"
            i = 0
            for player in result:
                if player[17] == 0:
                    continue
                i += 1
                name = player[4]
                xp = player[17]
                content += "\n#%s: %s (%s xp)" % (i, name, f"{xp:,.0f}")
            embed = discord.Embed(title="%s XP Leaderboard" % skill.capitalize(), description=diff + content + "\n```\n\n", color=ctx.author.color)
            embed.set_footer(text="FinalFloorFrags © 2020")
            embed.set_thumbnail(url="https://image.flaticon.com/icons/png/512/199/199774.png")
            db.close()
            return await message.edit(content=str(ctx.author.mention), embed=embed)

        elif arg1 == "leaderboard":
            embed = discord.Embed(title="Total Event XP Leaderboard", description=diff, color=ctx.author.color)
            cursor.execute("SELECT * FROM %s ORDER BY total_increment DESC" % table)
            result = cursor.fetchall()
            content = "\n"
            if len(result) != 0:
                content += "\n**TOP 3**\n```fix"
                for i in range(3):
                    player = result[i]
                    position = player[16]
                    name = player[4]
                    xp = player[15]
                    content += "\n#%s: %s (%s xp)" % (position, name, f"{xp:,.0f}")
                content += "```"
            if len(result) > 3:
                content += "\n**TOP 5**\n```glsl"
                for i in range(3, 5):
                    player = result[i]
                    position = player[16]
                    name = player[4]
                    xp = player[15]
                    content += "\n#%s: %s (%s xp)" % (position, name, f"{xp:,.0f}")
                content += "```"
            if len(result) > 5:
                content += "\n**TOP 10**\n```md"
                for i in range(5, 10):
                    player = result[i]
                    position = player[16]
                    name = player[4]
                    xp = player[15]
                    content += "\n#%s: %s (%s xp)" % (position, name, f"{xp:,.0f}")
                content += "```"
            if len(result) > 10:
                content += "\n```"
                for i in range(10, len(result) - 1):
                    player = result[i]
                    position = player[16]
                    name = player[4]
                    xp = player[15]
                    if xp == 0:
                        continue
                    content += "\n#%s: %s (%s xp)" % (position, name, f"{xp:,.0f}")
                content += "```"
            embed = discord.Embed(title="Total Event XP Leaderboard", description=diff + content + "\n\n", color=ctx.author.color)
            embed.set_footer(text="FinalFloorFrags © 2020")
            embed.set_thumbnail(url="https://image.flaticon.com/icons/png/512/199/199774.png")
            db.close()
            return await message.edit(content=str(ctx.author.mention), embed=embed)
