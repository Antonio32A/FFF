import discord
from discord.ext import commands
from util.handlers import Handlers


class FFF(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = Handlers.JSON.read("config")

    async def load_extensions(self):
        extensions = ["general", "auction", "applications"]
        for extension in extensions:
            self.load_extension(f"extensions.{extension}")
            print(f"Loaded {extension}.")
        print("Starting...")

    async def update_activity(self):
        activity = discord.Activity(
            name=self.config['activity']['name'],
            type=getattr(discord.ActivityType, self.config['activity']['type'])
        )
        await self.change_presence(activity=activity)

    async def on_ready(self):
        # self.remove_command("help")
        await self.load_extensions()
        await self.update_activity()
        print(f"Logged in as {self.user} ({self.user.id}).")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title=":x: Invalid Command!",
                description="Please refer to the **help** command and try again.",
                color=ctx.author.color
            )
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title=":x: On Cooldown!",
                description=f"Please try again in {round(error.retry_after)} seconds.",
                color=ctx.author.color
            )
            return await ctx.send(embed=embed)
        else:
            raise error


def get_pre(fff, message):
    bot_id = fff.user.id
    prefixes = [f"<@{bot_id}> ", f"<@!{bot_id}> ", fff.config['prefix']]
    return prefixes


fff = FFF(command_prefix=get_pre, owner_ids=(166630166825664512, 304979232814268417))
