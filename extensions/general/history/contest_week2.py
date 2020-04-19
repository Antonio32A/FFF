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
            description += "**f!contest top <combat/slayer/wolf/zombie/spider>:** Show a leaderboard of players according to skill/slayer type\n\n"
            description += "**f!contest player <ign>:** Show a player's progress for the active contest"
            embed = discord.Embed(title="Available Contest Commands", description=description, color=ctx.author.color)
            embed.set_footer(text="FinalFloorFrags © 2020")
            return await ctx.send(embed=embed)

        arg1 = arg1.lower()

        if arg1 not in ["top", "player", "leaderboard"]:
            description = "**f!contest help:** Show the available contest commands\n\n"
            description += "**f!contest leaderboard:** Show a leaderboard all player's xp gained\n\n"
            description += "**f!contest top <combat/slayer/wolf/zombie/spider>:** Show a leaderboard of players according to skill/slayer type\n\n"
            description += "**f!contest player <ign>:** Show a player's progress for the active contest"
            embed = discord.Embed(title=":x: Invalid Contest Command!", description="Please refer to the valid commands below.\n\n" + description, color=ctx.author.color)
            embed.set_footer(text="FinalFloorFrags © 2020")
            return await ctx.send(embed=embed)

        message = await ctx.send("Loading...")

        db = mysql.connector.connect(
            host="localhost",
            port="3306",
            user="USER",
            passwd="PASS",
            database="DB"
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
            slayerxp = result[0][13]
            combat = result[0][9] - result[0][5]
            wolf = result[0][10] - result[0][6]
            zombie = result[0][11] - result[0][7]
            spider = result[0][12] - result[0][8]

            embed = discord.Embed(title="%s's contest stats on %s" % (name, profile), description=diff, color=ctx.author.color)
            embed.add_field(name="Global position:", value="**#%s**" % result[0][14], inline=True)
            embed.add_field(name="<:combat:666805818645282858> Combat XP gained:", value=f"{combat:,.0f}", inline=True)
            embed.add_field(name="<:slayer:667945901305626643> Slayer XP gained:", value=f"{slayerxp:,.0f}", inline=True)
            embed.add_field(name="<:revenant:670393710193672192> Revenant slayer XP gained:", value=f"{zombie:,.0f}", inline=True)
            embed.add_field(name="<:sven:670391996401188897> Sven slayer XP gained:", value=f"{wolf:,.0f}", inline=True)
            embed.add_field(name="<:tarantula:670392898856026115> Tarantula slayer XP gained:", value=f"{spider:,.0f}", inline=True)
            embed.set_footer(text="FinalFloorFrags © 2020")
            embed.set_thumbnail(url="https://minotar.net/cube/" + uuid)
            db.close()
            return await message.edit(content=str(ctx.author.mention), embed=embed)

        elif arg1 == "top":
            if arg2 == None or arg2.lower() not in ["wolf", "sven", "zombie", "rev", "revenant", "tara", "spider", "tarantula", "combat", "slayer"]:
                embed = discord.Embed(title="Please use the correct command syntax!", description="f!contest top <combat/slayer/wolf/zombie/spider>", color=ctx.author.color)
                embed.set_footer(text="FinalFloorFrags © 2020")
                db.close()
                return await ctx.send(content=str(ctx.author.mention), embed=embed)
            top_type = arg2.lower()
            if top_type != "slayer":
                if top_type in ["wolf", "sven"]:
                    skill = "wolf"
                    top_icon = "<:sven:670391996401188897>"
                    top_string = "Wolf Slayer"
                elif top_type in ["zombie", "rev", "revenant"]:
                    skill = "zombie"
                    top_icon = "<:revenant:670393710193672192>"
                    top_string = "Revenant Slayer"
                elif top_type in ["tara", "spider", "tarantula"]:
                    skill = "spider"
                    top_icon = "<:tarantula:670392898856026115>"
                    top_string = "Spider Slayer"
                else:
                    skill = "combat"
                    top_icon = "<:combat:666805818645282858>"
                    top_string = "Combat"
                cursor.execute("SELECT *, current_%s - start_%s as difference FROM %s ORDER BY difference DESC" % (skill, skill, table))
                result = cursor.fetchall()
                content = "\n\n**%s Top 70 players in %s**\n```" % (top_icon, top_string)
                i = 0
                for player in result:
                    if player[15] == 0:
                        continue
                    i += 1
                    if i > 70:
                        break
                    name = player[4]
                    xp = player[15]
                    content += "\n#%s: %s (%s xp)" % (i, name, f"{xp:,.0f}")
            else:
                top_string = "Total Slayer"
                cursor.execute("SELECT * FROM %s ORDER BY slayerxp DESC" % table)
                result = cursor.fetchall()
                content = "\n\n<:slayer:667945901305626643> **Top 70 players for total Slayer XP**\n```"
                i = 0
                for player in result:
                    if player[13] == 0:
                        continue
                    i += 1
                    if i > 70:
                        break
                    name = player[4]
                    xp = player[13]
                    content += "\n#%s: %s (%s xp)" % (i, name, f"{xp:,.0f}")
            embed = discord.Embed(title="%s XP Leaderboard" % top_string, description=diff + content + "\n```\n\n", color=ctx.author.color)
            embed.set_footer(text="FinalFloorFrags © 2020")
            embed.set_thumbnail(url="https://image.flaticon.com/icons/png/512/199/199774.png")
            db.close()
            return await message.edit(content=str(ctx.author.mention), embed=embed)

        elif arg1 == "leaderboard":
            embed = discord.Embed(title="Total Event XP Leaderboard", description=diff, color=ctx.author.color)
            cursor.execute("SELECT * FROM %s ORDER BY position ASC" % table)
            result = cursor.fetchall()
            embed = discord.Embed(title="Total Event XP Leaderboard", description=diff, color=ctx.author.color)
            if len(result) != 0:
                content = "```fix"
                for i in range(3):
                    player = result[i]
                    position = player[14]
                    name = player[4]
                    slayerxp = player[13]
                    combatxp = player[9] - player[5]
                    content += "\n#%s: %s\n(%s Slayer XP | %s Combat XP)" % (position, name, f"{slayerxp:,.0f}", f"{combatxp:,.0f}")
                content += "```"
                embed.add_field(name="**TOP 3**", value=content, inline=False)
            if len(result) > 3:
                content = "```glsl"
                for i in range(3, 5):
                    player = result[i]
                    position = player[14]
                    name = player[4]
                    slayerxp = player[13]
                    combatxp = player[9] - player[5]
                    content += "\n#%s: %s\n(%s Slayer XP | %s Combat XP)" % (position, name, f"{slayerxp:,.0f}", f"{combatxp:,.0f}")
                content += "```"
                embed.add_field(name="**TOP 5**", value=content, inline=False)
            if len(result) > 5:
                content = "```md"
                for i in range(5, 10):
                    player = result[i]
                    position = player[14]
                    name = player[4]
                    slayerxp = player[13]
                    combatxp = player[9] - player[5]
                    content += "\n#%s: %s\n(%s Slayer XP | %s Combat XP)" % (position, name, f"{slayerxp:,.0f}", f"{combatxp:,.0f}")
                content += "```"
                embed.add_field(name="**TOP 10**", value=content, inline=False)
            if len(result) > 10:
                content = "```"
                for i in range(10, len(result) - 1):
                    if i == 25:
                        break
                    player = result[i]
                    position = player[14]
                    name = player[4]
                    slayerxp = player[13]
                    combatxp = player[9] - player[5]
                    content += "\n#%s: %s\n(%s Slayer XP | %s Combat XP)" % (position, name, f"{slayerxp:,.0f}", f"{combatxp:,.0f}")
                content += "```"
                embed.add_field(name="**TOP 25**", value=content, inline=False)
            embed.set_footer(text="FinalFloorFrags © 2020")
            embed.set_thumbnail(url="https://image.flaticon.com/icons/png/512/199/199774.png")
            db.close()
            return await message.edit(content=str(ctx.author.mention), embed=embed)
