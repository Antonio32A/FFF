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
        help_embed = discord.Embed(title=":crossed_swords: FinalFloorFrags Command List.", description="Welcome to the command list for the FinalFloorFrags Bot!\n", color=ctx.author.color)
        help_embed.add_field(name="**Apply:**", value="f!**apply**  |  Apply for the Guild in <#665296815431745578>!\n", inline=False)

        # Genenral Commands
        help_embed.add_field(name="**General Commands:**", value="f!**profile**  |  Skyblock profile search.", inline=False)

        # Guild Commands
        help_embed.add_field(name="**Guild Commands:**", value="`Coming Soon!`\n", inline=False)

        help_embed.set_footer(text="FinalFloorFrags © 2020")
        await ctx.send(embed=help_embed)
