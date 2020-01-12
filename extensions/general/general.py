import discord
from discord.ext import commands
import time

class General(commands.Cog, name="General"):
    def __init__(self, fff):
        self.fff = fff

    @commands.command()
    async def ping(self, ctx):
        b = time.monotonic()
        message = await ctx.send("Pinging...")
        await ctx.trigger_typing()
        ping = (time.monotonic() - b) * 1000
        ping = round(ping)
        await message.delete()
        return await ctx.send(f"Pong, {ping}ms")

    @commands.command()
    async def help(self, ctx):
        """
            TODO: Complete "help" command
        """
        embed = discord.Embed(title="FinalFloorFrags Help Commands!", color=ctx.author.color)
        embed.add_field(name="General Commands:", value="• f!help | Help Command List.\n• f!about | About FFF.\n• f!members | Lists current members.\n", inline=False)
        embed.set_footer(text="FinalFloorFrags © 2020")
        await ctx.send(embed=embed)
